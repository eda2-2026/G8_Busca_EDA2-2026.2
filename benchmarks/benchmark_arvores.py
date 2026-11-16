"""Benchmark do T3: lista ordenada (T1) x BST x AVL x Trie.

Mede, sobre as mesmas chaves e as mesmas consultas:
  - construcao_ms: tempo para montar o índice a partir dos pares (chave, id);
  - busca_exata_us: tempo médio de uma busca exata (metade presentes, metade ausentes);
  - busca_prefixo_us: tempo médio de uma busca por prefixo (Trie x varredura linear);
  - altura: altura da árvore (não se aplica à lista ordenada).

Uso:
    python -m benchmarks.benchmark_arvores --repeticoes 2 --tamanhos-sinteticos 500 --saida /tmp/ensaio_t3.csv
"""

import argparse
import csv
import hashlib
import json
import random
import statistics
import string
import sys
import time
from pathlib import Path

from benchmarks.benchmark_ordenacao import coletar_ambiente, derivar_semente, inteiro_minimo
from src.search.busca import busca_binaria, carregar_dados
from src.tree.trie import Trie

CENARIOS_REAIS = ("original", "aleatorio", "ordenado")
CENARIOS_SINTETICOS = ("aleatorio", "ordenado", "quase_ordenado")
CENARIOS_DEGENERADOS = ("ordenado", "quase_ordenado")
# A BST sem balanceamento vira uma lista com chaves em ordem: cada inserção custa O(n).
# Acima deste tamanho o caso degenerado levaria minutos, então fica de fora (e é registrado).
LIMITE_BST_ORDENADA = 5000
TAMANHOS_PREFIXO = (1, 2, 3)
PREFIXOS_POR_TAMANHO = 30
CAMPOS_CSV = [
    "caso_id", "origem", "n", "cenario", "estrutura", "medida",
    "detalhe", "repeticao", "semente", "valor",
]


# --- Estruturas ----------------------------------------------------------------

class IndiceOrdenado:
    """O índice do T1: dicionário de chaves ordenado uma vez + busca binária."""

    def __init__(self, pares):
        indice = {}
        for chave, id_artista in pares:
            indice.setdefault(chave, []).append(id_artista)
        self.itens = sorted(indice.items())

    def buscar(self, chave):
        return busca_binaria(self.itens, chave)

    def altura(self):
        return None


def construtor_de_arvore(classe):
    def construir(pares):
        arvore = classe()
        for chave, id_artista in pares:
            arvore.inserir(chave, id_artista)
        return arvore
    construir.__name__ = f"construir_{classe.__name__.lower()}"
    return construir


def estruturas_disponiveis():
    estruturas = {"lista_ordenada": IndiceOrdenado}
    try:
        from src.tree.api import INDICES
    except ImportError:
        INDICES = {}
    for nome, classe in INDICES.items():
        estruturas[nome] = construtor_de_arvore(classe)
    estruturas.setdefault("trie", construtor_de_arvore(Trie))
    return estruturas


def varrer_prefixo(lista, prefixo):
    """Busca por prefixo sem Trie: percorre todas as chaves da lista ordenada."""
    vistos = set()
    resultado = []
    for chave, ids in lista.itens:
        if chave.startswith(prefixo):
            for id_artista in ids:
                if id_artista not in vistos:
                    vistos.add(id_artista)
                    resultado.append(id_artista)
    return resultado


def sem_repeticao(ids):
    return list(dict.fromkeys(ids))


# --- Preparação dos casos (tudo fora do cronômetro) ----------------------------

def pares_reais(artistas):
    """Mesmas chaves e mesma ordem de inserção de construir_indice/construir_arvore."""
    pares = []
    for artista in artistas:
        for chave in [artista["nome"], *artista["generos"]]:
            pares.append((chave.strip().lower(), artista["id"]))
    return pares


def _palavra(rng, minimo, maximo):
    return "".join(rng.choice(string.ascii_lowercase) for _ in range(rng.randint(minimo, maximo)))


def gerar_chaves_sinteticas(n, semente):
    rng = random.Random(semente)
    chaves = {}
    while len(chaves) < n:
        chaves.setdefault(_palavra(rng, 3, 12), None)
    return list(chaves)


def aplicar_ordem(pares, cenario, semente):
    if cenario == "original":
        return list(pares)
    if cenario == "aleatorio":
        resultado = list(pares)
        random.Random(semente).shuffle(resultado)
        return resultado

    resultado = sorted(pares)
    if cenario == "ordenado":
        return resultado
    if cenario == "quase_ordenado":
        rng = random.Random(semente)
        n = len(resultado)
        for _ in range(max(1, n // 20)):
            i = rng.randrange(n)
            j = min(n - 1, i + rng.randint(1, 10))
            resultado[i], resultado[j] = resultado[j], resultado[i]
        return resultado
    raise ValueError(f"cenário desconhecido: {cenario}")


def gerar_consultas(chaves, semente, quantidade=200):
    rng = random.Random(semente)
    distintas = list(dict.fromkeys(chaves))
    existentes = set(distintas)

    presentes = [rng.choice(distintas) for _ in range(quantidade // 2)]
    ausentes = []
    while len(ausentes) < quantidade - len(presentes):
        palavra = _palavra(rng, 4, 12)
        if palavra not in existentes:
            ausentes.append(palavra)
    exatas = presentes + ausentes
    rng.shuffle(exatas)

    prefixos = {}
    for tamanho in TAMANHOS_PREFIXO:
        candidatas = [c for c in distintas if len(c) >= tamanho]
        prefixos[tamanho] = (
            [rng.choice(candidatas)[:tamanho] for _ in range(PREFIXOS_POR_TAMANHO)]
            if candidatas else []
        )
    return {"exatas": exatas, "prefixos": prefixos}


def _novo_caso(origem, n, cenario, pares, consultas, semente, estruturas):
    caso_id = f"{origem}-{n}-{cenario}"
    semente_caso = derivar_semente(semente, caso_id)
    nomes = list(estruturas)
    if "bst" in nomes and cenario in CENARIOS_DEGENERADOS and n > LIMITE_BST_ORDENADA:
        nomes.remove("bst")
    return {
        "caso_id": caso_id,
        "origem": origem,
        "n": n,
        "cenario": cenario,
        "semente": semente_caso,
        "pares": aplicar_ordem(pares, cenario, semente_caso),
        "consultas": consultas,
        "estruturas": nomes,
    }


def montar_casos(artistas, tamanhos, semente, estruturas, quantidade_consultas=200):
    casos = []
    if artistas:
        pares = pares_reais(artistas)
        chaves = [c for c, _ in pares]
        n = len(set(chaves))
        consultas = gerar_consultas(chaves, derivar_semente(semente, "real", "consultas"),
                                    quantidade_consultas)
        for cenario in CENARIOS_REAIS:
            casos.append(_novo_caso("real", n, cenario, pares, consultas, semente, estruturas))

    for n in tamanhos:
        chaves = gerar_chaves_sinteticas(n, derivar_semente(semente, "sintetico", n))
        pares = [(c, f"s{i}") for i, c in enumerate(chaves)]
        consultas = gerar_consultas(chaves, derivar_semente(semente, "sintetico", n, "consultas"),
                                    quantidade_consultas)
        for cenario in CENARIOS_SINTETICOS:
            casos.append(_novo_caso("sintetico", n, cenario, pares, consultas, semente, estruturas))
    return casos


def observar_casos(casos, todas):
    observacoes = []
    for nome in ("bst", "avl"):
        if nome not in todas:
            observacoes.append(f"estrutura '{nome}' indisponível (src.tree.api sem ela); não medida")
    for caso in casos:
        if "bst" in todas and "bst" not in caso["estruturas"]:
            observacoes.append(
                f"{caso['caso_id']}: BST fora do caso (n > {LIMITE_BST_ORDENADA} com chaves "
                "em ordem degenera a árvore em lista; inserção O(n) por chave)"
            )
    return observacoes


# --- Medição ---------------------------------------------------------------------

class ErroValidacao(AssertionError):
    """Uma estrutura respondeu diferente da lista ordenada: a coleta é interrompida."""


def validar(caso, construtores):
    """Confere, fora do cronômetro, que toda estrutura responde como a lista ordenada."""
    referencia = IndiceOrdenado(caso["pares"])
    for nome in caso["estruturas"]:
        indice = construtores[nome](caso["pares"])
        for consulta in caso["consultas"]["exatas"]:
            obtido = sem_repeticao(indice.buscar(consulta))
            esperado = sem_repeticao(referencia.buscar(consulta))
            if obtido != esperado:
                raise ErroValidacao(f"{caso['caso_id']}/{nome}: '{consulta}' -> {obtido} != {esperado}")
        if hasattr(indice, "buscar_prefixo"):
            for prefixos in caso["consultas"]["prefixos"].values():
                for prefixo in prefixos:
                    obtido = indice.buscar_prefixo(prefixo)
                    esperado = varrer_prefixo(referencia, prefixo)
                    if obtido != esperado:
                        raise ErroValidacao(f"{caso['caso_id']}/{nome}: prefixo '{prefixo}'")


def _cronometrar_buscas(funcao, consultas):
    inicio = time.perf_counter_ns()
    for consulta in consultas:
        funcao(consulta)
    fim = time.perf_counter_ns()
    return (fim - inicio) / len(consultas) / 1000


def executar_caso(caso, repeticoes, construtores=None):
    construtores = construtores or estruturas_disponiveis()
    validar(caso, construtores)

    pares = caso["pares"]
    exatas = caso["consultas"]["exatas"]
    prefixos = caso["consultas"]["prefixos"]
    base = {k: caso[k] for k in ("caso_id", "origem", "n", "cenario", "semente")}
    linhas = []

    def registrar(estrutura, medida, repeticao, valor, detalhe=""):
        linhas.append({**base, "estrutura": estrutura, "medida": medida, "detalhe": detalhe,
                       "repeticao": repeticao, "valor": valor})

    # repetição 0 = aquecimento descartado
    for repeticao in range(repeticoes + 1):
        construidos = {}
        for nome in caso["estruturas"]:
            inicio = time.perf_counter_ns()
            indice = construtores[nome](pares)
            fim = time.perf_counter_ns()
            construidos[nome] = indice
            busca = _cronometrar_buscas(indice.buscar, exatas)
            if repeticao:
                registrar(nome, "construcao_ms", repeticao, (fim - inicio) / 1_000_000)
                registrar(nome, "busca_exata_us", repeticao, busca)

        trie = construidos.get("trie")
        lista = construidos.get("lista_ordenada")
        if trie is not None and lista is not None:
            for tamanho, lote in prefixos.items():
                if not lote:
                    continue
                tempo_trie = _cronometrar_buscas(trie.buscar_prefixo, lote)
                tempo_varredura = _cronometrar_buscas(lambda p: varrer_prefixo(lista, p), lote)
                if repeticao:
                    registrar("trie", "busca_prefixo_us", repeticao, tempo_trie, f"p{tamanho}")
                    registrar("varredura", "busca_prefixo_us", repeticao, tempo_varredura, f"p{tamanho}")

        if repeticao == 1:
            for nome, indice in construidos.items():
                altura = indice.altura()
                if altura is not None:
                    registrar(nome, "altura", 1, altura)

    return linhas


# --- Resumo e arquivos -----------------------------------------------------------

def resumir(linhas):
    grupos = {}
    for linha in linhas:
        chave = tuple(linha[k] for k in ("caso_id", "origem", "n", "cenario", "estrutura", "medida", "detalhe"))
        grupos.setdefault(chave, []).append(float(linha["valor"]))

    resumo = []
    for chave, valores in grupos.items():
        if len(valores) >= 2:
            q1, _, q3 = statistics.quantiles(valores, n=4, method="inclusive")
            iqr = q3 - q1
        else:
            iqr = 0.0
        resumo.append({
            **dict(zip(("caso_id", "origem", "n", "cenario", "estrutura", "medida", "detalhe"), chave)),
            "mediana": statistics.median(valores),
            "iqr": iqr,
            "repeticoes": len(valores),
        })
    return resumo


def _fmt(valor):
    return f"{valor:.4g}"


def _tabela(resumo, medida, estruturas, com_iqr=True, por_detalhe=False):
    linhas_tabela = {}
    for item in resumo:
        if item["medida"] != medida:
            continue
        chave = (item["origem"], item["n"], item["cenario"], item["detalhe"] if por_detalhe else "")
        texto = _fmt(item["mediana"])
        if com_iqr:
            texto += f" ({_fmt(item['iqr'])})"
        linhas_tabela.setdefault(chave, {})[item["estrutura"]] = texto
    if not linhas_tabela:
        return ""

    cabecalho = ["Origem", "n", "Cenário"] + (["Prefixo"] if por_detalhe else []) + list(estruturas)
    saida = ["| " + " | ".join(cabecalho) + " |",
             "|" + "---|" * 3 + ("---|" if por_detalhe else "") + "---:|" * len(estruturas)]
    for (origem, n, cenario, detalhe), valores in linhas_tabela.items():
        celulas = [origem, str(n), cenario] + ([detalhe] if por_detalhe else [])
        celulas += [valores.get(e, "—") for e in estruturas]
        saida.append("| " + " | ".join(celulas) + " |")
    return "\n".join(saida)


def formatar_resumo(resumo, ambiente, nome_csv):
    presentes = []
    for item in resumo:
        if item["estrutura"] not in presentes:
            presentes.append(item["estrutura"])
    arvores = [e for e in presentes if e not in ("varredura",)]
    so_arvores = [e for e in arvores if e != "lista_ordenada"]

    partes = [
        "# Resumo do benchmark T3 — lista ordenada × BST × AVL × Trie",
        "",
        f"Gerado a partir de `{nome_csv}`. Revisão do código: `{ambiente['git_revisao']}` "
        f"(árvore {ambiente['git_arvore']}). Dataset SHA-256: `{ambiente['dataset_sha256']}`.",
        f"Repetições por estrutura e caso: {ambiente['configuracao']['repeticoes']} (mais 1 aquecimento "
        "descartado). Valores: mediana e, entre parênteses, IQR (Q3 − Q1, quartis inclusivos). "
        "`n` = número de chaves distintas. — = estrutura não medida no caso.",
        "",
    ]
    for observacao in ambiente["observacoes"]:
        partes += [f"> {observacao}", ""]

    secoes = [
        ("Construção do índice (ms)", _tabela(resumo, "construcao_ms", arvores)),
        ("Busca exata (µs por busca)", _tabela(resumo, "busca_exata_us", arvores)),
        ("Altura", _tabela(resumo, "altura", so_arvores, com_iqr=False)),
        ("Busca por prefixo (µs por busca)",
         _tabela(resumo, "busca_prefixo_us", ["trie", "varredura"], por_detalhe=True)),
    ]
    for titulo, tabela in secoes:
        if tabela:
            partes += [f"## {titulo}", "", tabela, ""]
    return "\n".join(partes)


def caminhos_derivados(saida):
    saida = Path(saida)
    nome = saida.stem
    sufixo = nome[len("resultados_"):] if nome.startswith("resultados_") else nome
    return {
        "ambiente": saida.with_name(f"ambiente_{sufixo}.json"),
        "entradas": saida.with_name(f"entradas_{sufixo}.json"),
        "resumo": saida.with_name(f"resumo_{sufixo}.md"),
    }


def escrever_entradas(caminho, casos):
    # As chaves sintéticas são regeneradas pela semente; aqui ficam o hash da sequência
    # inserida (para conferir a reprodução), as primeiras chaves e as consultas.
    descricoes = []
    for caso in casos:
        sequencia = "\n".join(f"{c}\t{i}" for c, i in caso["pares"]).encode("utf-8")
        descricoes.append(json.dumps({
            "caso_id": caso["caso_id"],
            "origem": caso["origem"],
            "n": caso["n"],
            "cenario": caso["cenario"],
            "semente": caso["semente"],
            "estruturas": caso["estruturas"],
            "insercoes": len(caso["pares"]),
            "sequencia_sha256": hashlib.sha256(sequencia).hexdigest(),
            "primeiras_chaves": [c for c, _ in caso["pares"][:10]],
            "consultas": caso["consultas"],
        }, ensure_ascii=False))
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("[\n" + ",\n".join(descricoes) + "\n]\n")


def criar_parser():
    parser = argparse.ArgumentParser(
        description="Compara lista ordenada, BST, AVL e Trie sobre as mesmas chaves (T3)."
    )
    parser.add_argument("--dados", default="data/processed/artistas.json",
                        help="JSON de artistas (padrão: %(default)s)")
    parser.add_argument("--repeticoes", type=inteiro_minimo(2), default=10,
                        help="repetições medidas por estrutura e caso, >= 2 (padrão: %(default)s)")
    parser.add_argument("--tamanhos-sinteticos", type=inteiro_minimo(1), nargs="+",
                        default=[1000, 5000, 20000],
                        help="números de chaves dos conjuntos sintéticos (padrão: %(default)s)")
    parser.add_argument("--consultas", type=inteiro_minimo(2), default=200,
                        help="buscas exatas por caso, metade presentes (padrão: %(default)s)")
    parser.add_argument("--semente", type=int, default=42,
                        help="semente base dos sorteios (padrão: %(default)s)")
    parser.add_argument("--saida", default="benchmarks/resultados_t3.csv",
                        help="CSV de destino (padrão: %(default)s)")
    return parser


def executar(args, argv):
    construtores = estruturas_disponiveis()
    configuracao = {
        "dados": args.dados,
        "repeticoes": args.repeticoes,
        "tamanhos_sinteticos": args.tamanhos_sinteticos,
        "consultas": args.consultas,
        "semente": args.semente,
        "saida": args.saida,
        "estruturas": list(construtores),
        "limite_bst_ordenada": LIMITE_BST_ORDENADA,
    }
    artistas = carregar_dados(args.dados)
    casos = montar_casos(artistas, args.tamanhos_sinteticos, args.semente,
                         list(construtores), args.consultas)
    observacoes = observar_casos(casos, construtores)
    ambiente = coletar_ambiente(args.dados, argv, configuracao, observacoes)
    ambiente["comando"] = " ".join(["python -m benchmarks.benchmark_arvores", *argv])
    ambiente.pop("selecao_catalogo", None)

    linhas = []
    for caso in casos:
        linhas.extend(executar_caso(caso, args.repeticoes, construtores))

    saida = Path(args.saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    derivados = caminhos_derivados(saida)
    with open(saida, "w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=CAMPOS_CSV)
        escritor.writeheader()
        escritor.writerows(linhas)
    with open(derivados["ambiente"], "w", encoding="utf-8") as f:
        json.dump(ambiente, f, ensure_ascii=False, indent=2)
        f.write("\n")
    escrever_entradas(derivados["entradas"], casos)
    with open(derivados["resumo"], "w", encoding="utf-8") as f:
        f.write(formatar_resumo(resumir(linhas), ambiente, saida.name))
    return linhas, len(casos)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    args = criar_parser().parse_args(argv)
    try:
        linhas, total_casos = executar(args, argv)
    except (OSError, json.JSONDecodeError) as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return 1
    except ErroValidacao as erro:
        print(f"erro de validação, coleta interrompida: {erro}", file=sys.stderr)
        return 1
    print(f"{total_casos} casos, {len(linhas)} medições gravadas em {args.saida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
