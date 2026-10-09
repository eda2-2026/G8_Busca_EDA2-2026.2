"""Benchmark do T2: compara Insertion Sort e Merge Sort sobre as mesmas entradas.

Executar da raiz do repositório:

    python -m benchmarks.benchmark_ordenacao --repeticoes 10

Arquivos gerados ao lado do CSV de saída:
- saída ``resultados_<sufixo>.csv`` -> ``ambiente_<sufixo>.json``,
  ``entradas_<sufixo>.json`` e ``resumo_<sufixo>.md``;
- qualquer outro nome ``<nome>.csv`` -> ``<nome>_ambiente.json``,
  ``<nome>_entradas.json`` e ``<nome>_resumo.md``.

Assim um ensaio em /tmp/ensaio_t2.csv nunca sobrescreve os resultados finais.
"""

import argparse
import csv
import hashlib
import json
import platform
import random
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from src.ranking.relevancia import preparar_resultados
from src.search.busca import busca_sequencial, carregar_dados
from src.sort.insertion import insertion_sort
from src.sort.merge import merge_sort

ALGORITMOS = {"insertion": insertion_sort, "merge": merge_sort}
CENARIOS = ("aleatorio", "ordenado", "inverso", "quase_ordenado", "todos_iguais")
TAMANHOS_CATALOGO = (100, 300)
FAIXAS_SINTETICAS = {
    "sintetico_poucas_chaves": (-100, 0),
    "sintetico_faixa_ampla": (0, 1_000_000),
}
CAMPOS_CSV = [
    "caso_id", "origem", "n", "cenario", "chaves_distintas",
    "algoritmo", "repeticao", "semente", "tempo_ms",
]


class ErroValidacao(Exception):
    """A saída de um algoritmo divergiu da ordenação estável de referência."""


def chave(item):
    return item["chave"]


def identificar(item):
    if "artista" in item:
        return item["artista"]["id"]
    return item["id"]


def derivar_semente(semente, *partes):
    texto = ":".join(str(parte) for parte in (semente, *partes))
    return int(hashlib.sha256(texto.encode("utf-8")).hexdigest()[:8], 16)


# --- Preparação dos casos (tudo fora do cronômetro) ---------------------------

def deduplicar_por_id(artistas):
    vistos = set()
    unicos = []
    for artista in artistas:
        if artista["id"] not in vistos:
            vistos.add(artista["id"])
            unicos.append(artista)
    return unicos


def tamanhos_catalogo(total):
    """Prefixos do JSON: 100, 300 e o total, só os que existem e sem repetir."""
    if total <= 0:
        return []
    return sorted({t for t in TAMANHOS_CATALOGO if t <= total} | {total})


def gerar_sintetico(origem, n, semente):
    minimo, maximo = FAIXAS_SINTETICAS[origem]
    rng = random.Random(derivar_semente(semente, origem, n))
    return [
        {"id": f"{origem}-{i:05d}", "chave": rng.randint(minimo, maximo)}
        for i in range(n)
    ]


def montar_bases(artistas, termo, tamanhos_sinteticos, semente):
    """Retorna ([(origem, itens pontuados)], observações)."""
    termo = termo.strip().lower()
    bases = []
    observacoes = []

    encontrados = deduplicar_por_id(busca_sequencial(artistas, termo))
    if encontrados:
        bases.append(("consulta_real", preparar_resultados(encontrados, termo)))
    else:
        observacoes.append(
            f"consulta_real omitida: a busca sequencial por '{termo}' não retornou artistas"
        )

    for tamanho in tamanhos_catalogo(len(artistas)):
        bases.append(("catalogo_real", preparar_resultados(artistas[:tamanho], termo)))

    for origem in FAIXAS_SINTETICAS:
        for n in sorted(set(tamanhos_sinteticos)):
            bases.append((origem, gerar_sintetico(origem, n, semente)))

    return bases, observacoes


def perturbar(itens, rng, pedidas):
    """Troca até `pedidas` pares de posições com chaves diferentes; devolve as efetivas."""
    n = len(itens)
    if n < 2 or len({chave(x) for x in itens}) < 2:
        return 0
    efetivas = 0
    for _ in range(pedidas):
        for _tentativa in range(100):
            i, j = rng.sample(range(n), 2)
            if chave(itens[i]) != chave(itens[j]):
                itens[i], itens[j] = itens[j], itens[i]
                efetivas += 1
                break
    return efetivas


def aplicar_cenario(base, cenario, semente):
    """Monta a ordem inicial de um caso. `sorted` aqui é preparação, não medição."""
    if cenario == "aleatorio":
        itens = list(base)
        random.Random(semente).shuffle(itens)
        return itens, {"transformacao": "embaralhamento com a semente do caso"}
    if cenario == "ordenado":
        return sorted(base, key=chave), {"transformacao": "chaves crescentes (scores decrescentes)"}
    if cenario == "inverso":
        return sorted(base, key=chave, reverse=True), {"transformacao": "chaves decrescentes"}
    if cenario == "quase_ordenado":
        itens = sorted(base, key=chave)
        pedidas = max(1, len(itens) // 100) if len(itens) >= 2 else 0
        efetivas = perturbar(itens, random.Random(semente), pedidas)
        return itens, {
            "transformacao": "ordem crescente com trocas de pares de chaves diferentes",
            "trocas_pedidas": pedidas,
            "trocas_efetivas": efetivas,
        }
    if cenario == "todos_iguais":
        itens = [{**item, "chave": 0} for item in base]
        return itens, {"transformacao": "transformação experimental: chave 0 para todos"}
    raise ValueError(f"cenário desconhecido: {cenario}")


def montar_casos(bases, semente):
    casos = []
    for origem, base in bases:
        n = len(base)
        for cenario in CENARIOS:
            caso_id = f"{origem}-{n}-{cenario}"
            semente_caso = derivar_semente(semente, caso_id)
            itens, info = aplicar_cenario(base, cenario, semente_caso)
            casos.append({
                "caso_id": caso_id,
                "origem": origem,
                "n": n,
                "cenario": cenario,
                "semente": semente_caso,
                "chaves_distintas": len({chave(x) for x in itens}),
                **info,
                "itens": itens,
            })
    return casos


# --- Medição e validação ------------------------------------------------------

def medir(algoritmo, entrada):
    inicio = time.perf_counter_ns()
    saida = algoritmo(entrada, key=chave)
    fim = time.perf_counter_ns()
    return saida, (fim - inicio) / 1_000_000


def retrato(itens):
    return [(id(item), chave(item)) for item in itens]


def validar(nome, caso, saida, retrato_entrada):
    entrada = caso["itens"]
    if retrato(entrada) != retrato_entrada:
        raise ErroValidacao(f"{nome} alterou a entrada de {caso['caso_id']}")
    if saida is entrada:
        raise ErroValidacao(f"{nome} devolveu a própria lista de entrada em {caso['caso_id']}")
    esperado = sorted(entrada, key=chave)
    if len(saida) != len(esperado) or any(a is not b for a, b in zip(saida, esperado)):
        raise ErroValidacao(f"{nome} não reproduziu a ordenação estável em {caso['caso_id']}")


def executar_caso(caso, repeticoes, algoritmos=ALGORITMOS):
    entrada = caso["itens"]
    referencia = retrato(entrada)

    # Validação inicial + aquecimento descartado.
    for nome, algoritmo in algoritmos.items():
        saida, _ = medir(algoritmo, entrada)
        validar(nome, caso, saida, referencia)

    nomes = list(algoritmos)
    linhas = []
    for repeticao in range(1, repeticoes + 1):
        # Par: Insertion primeiro. Ímpar: Merge primeiro.
        ordem = nomes if repeticao % 2 == 0 else list(reversed(nomes))
        for nome in ordem:
            saida, tempo_ms = medir(algoritmos[nome], entrada)
            validar(nome, caso, saida, referencia)
            linhas.append({
                "caso_id": caso["caso_id"],
                "origem": caso["origem"],
                "n": caso["n"],
                "cenario": caso["cenario"],
                "chaves_distintas": caso["chaves_distintas"],
                "algoritmo": nome,
                "repeticao": repeticao,
                "semente": caso["semente"],
                "tempo_ms": tempo_ms,
            })
    return linhas


def resumir(linhas):
    grupos = {}
    for linha in linhas:
        grupo = (linha["origem"], linha["n"], linha["cenario"], linha["chaves_distintas"])
        grupos.setdefault(grupo, {}).setdefault(linha["algoritmo"], []).append(linha["tempo_ms"])

    resumo = []
    for (origem, n, cenario, distintas), por_algoritmo in grupos.items():
        estatisticas = {}
        for nome, tempos in por_algoritmo.items():
            q1, _, q3 = statistics.quantiles(tempos, n=4, method="inclusive")
            estatisticas[nome] = {"mediana": statistics.median(tempos), "iqr": q3 - q1}
        resumo.append({
            "origem": origem,
            "n": n,
            "cenario": cenario,
            "chaves_distintas": distintas,
            "algoritmos": estatisticas,
        })
    return resumo


# --- Ambiente e exportação ----------------------------------------------------

def _git(*args):
    try:
        resultado = subprocess.run(["git", *args], capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return resultado.stdout.strip()


def identificar_processador():
    try:
        with open("/proc/cpuinfo", encoding="utf-8") as f:
            for linha in f:
                if linha.lower().startswith("model name"):
                    return linha.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or "não informado"


def coletar_ambiente(dados, argv, configuracao, observacoes):
    with open(dados, "rb") as f:
        hash_dados = hashlib.sha256(f.read()).hexdigest()
    revisao = _git("rev-parse", "HEAD")
    # Só arquivos versionados contam: arquivos não rastreados não mudam o código medido.
    status = _git("status", "--porcelain", "--untracked-files=no")
    return {
        "python": sys.version,
        "implementacao": platform.python_implementation(),
        "sistema": platform.platform(),
        "processador": identificar_processador(),
        "git_revisao": revisao or "não informado",
        "git_arvore": "não informado" if status is None else ("suja" if status else "limpa"),
        "dataset": str(dados),
        "dataset_sha256": hash_dados,
        "comando": " ".join(["python -m benchmarks.benchmark_ordenacao", *argv]),
        "configuracao": configuracao,
        "selecao_catalogo": (
            "prefixos do JSON original (100, 300 e total disponíveis); "
            "não é uma amostra estatisticamente representativa"
        ),
        "observacoes": observacoes,
        "data_execucao": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def caminhos_derivados(saida):
    saida = Path(saida)
    nome = saida.stem
    if nome.startswith("resultados_"):
        sufixo = nome[len("resultados_"):]
        nomes = (f"ambiente_{sufixo}.json", f"entradas_{sufixo}.json", f"resumo_{sufixo}.md")
    else:
        nomes = (f"{nome}_ambiente.json", f"{nome}_entradas.json", f"{nome}_resumo.md")
    return dict(zip(("ambiente", "entradas", "resumo"), (saida.with_name(n) for n in nomes)))


def escrever_csv(caminho, linhas):
    with open(caminho, "w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=CAMPOS_CSV)
        escritor.writeheader()
        escritor.writerows(linhas)


def escrever_entradas(caminho, casos):
    # Um caso por linha: JSON válido e diffs legíveis.
    descricoes = []
    for caso in casos:
        descricao = {k: v for k, v in caso.items() if k != "itens"}
        descricao["itens"] = [[identificar(x), chave(x)] for x in caso["itens"]]
        descricoes.append(json.dumps(descricao, ensure_ascii=False))
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("[\n" + ",\n".join(descricoes) + "\n]\n")


def formatar_resumo(resumo, ambiente, nome_csv):
    nomes = list(ALGORITMOS)
    linhas = [
        "# Resumo do benchmark T2 — Insertion Sort × Merge Sort",
        "",
        f"Gerado a partir de `{nome_csv}`. Revisão do código: `{ambiente['git_revisao']}` "
        f"(árvore {ambiente['git_arvore']}). Dataset SHA-256: `{ambiente['dataset_sha256']}`.",
        f"Repetições por algoritmo e caso: {ambiente['configuracao']['repeticoes']}. "
        "Tempos em milissegundos: mediana e IQR (Q3 − Q1, quartis inclusivos).",
        "",
    ]
    for observacao in ambiente["observacoes"]:
        linhas.append(f"> {observacao}")
        linhas.append("")
    cabecalho = ["Origem", "n", "Cenário", "Chaves distintas"]
    for nome in nomes:
        cabecalho += [f"{nome} mediana", f"{nome} IQR"]
    linhas.append("| " + " | ".join(cabecalho) + " |")
    linhas.append("|" + "---|" * 4 + "---:|" * (2 * len(nomes)))
    for grupo in resumo:
        celulas = [grupo["origem"], str(grupo["n"]), grupo["cenario"], str(grupo["chaves_distintas"])]
        for nome in nomes:
            estat = grupo["algoritmos"][nome]
            celulas += [f"{estat['mediana']:.4g}", f"{estat['iqr']:.4g}"]
        linhas.append("| " + " | ".join(celulas) + " |")
    return "\n".join(linhas) + "\n"


# --- Interface de linha de comando -------------------------------------------

def inteiro_minimo(minimo):
    def converter(texto):
        try:
            valor = int(texto)
        except ValueError:
            raise argparse.ArgumentTypeError(f"'{texto}' não é um inteiro")
        if valor < minimo:
            raise argparse.ArgumentTypeError(f"deve ser um inteiro >= {minimo}")
        return valor
    return converter


def criar_parser():
    parser = argparse.ArgumentParser(
        description="Compara Insertion Sort e Merge Sort sobre as mesmas entradas (T2)."
    )
    parser.add_argument("--dados", default="data/processed/artistas.json",
                        help="JSON de artistas (padrão: %(default)s)")
    parser.add_argument("--termo", default="rock",
                        help="consulta usada no ranking (padrão: %(default)s)")
    parser.add_argument("--repeticoes", type=inteiro_minimo(2), default=10,
                        help="repetições medidas por algoritmo e caso, >= 2 (padrão: %(default)s)")
    parser.add_argument("--tamanhos-sinteticos", type=inteiro_minimo(1), nargs="+",
                        default=[100, 500, 2000],
                        help="tamanhos dos conjuntos sintéticos (padrão: %(default)s)")
    parser.add_argument("--semente", type=int, default=42,
                        help="semente base dos sorteios (padrão: %(default)s)")
    parser.add_argument("--saida", default="benchmarks/resultados_t2.csv",
                        help="CSV de destino (padrão: %(default)s)")
    return parser


def executar(args, argv):
    configuracao = {
        "dados": args.dados,
        "termo": args.termo,
        "repeticoes": args.repeticoes,
        "tamanhos_sinteticos": args.tamanhos_sinteticos,
        "semente": args.semente,
        "saida": args.saida,
    }
    artistas = carregar_dados(args.dados)
    bases, observacoes = montar_bases(artistas, args.termo, args.tamanhos_sinteticos, args.semente)
    ambiente = coletar_ambiente(args.dados, argv, configuracao, observacoes)
    casos = montar_casos(bases, args.semente)

    linhas = []
    for caso in casos:
        linhas.extend(executar_caso(caso, args.repeticoes))

    saida = Path(args.saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    derivados = caminhos_derivados(saida)
    escrever_csv(saida, linhas)
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
