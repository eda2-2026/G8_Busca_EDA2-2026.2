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

import hashlib
import random

from src.ranking.relevancia import preparar_resultados
from src.search.busca import busca_sequencial
from src.sort.insertion import insertion_sort
from src.sort.merge import merge_sort

ALGORITMOS = {"insertion": insertion_sort, "merge": merge_sort}
CENARIOS = ("aleatorio", "ordenado", "inverso", "quase_ordenado", "todos_iguais")
TAMANHOS_CATALOGO = (100, 300)
FAIXAS_SINTETICAS = {
    "sintetico_poucas_chaves": (-100, 0),
    "sintetico_faixa_ampla": (0, 1_000_000),
}


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
