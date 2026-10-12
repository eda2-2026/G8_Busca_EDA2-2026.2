from src.search.busca import (
    busca_sequencial,
    construir_indice,
    busca_binaria,
    ids_para_artistas,
)
from src.ranking.relevancia import preparar_resultados
from src.sort.api import ALGORITMOS, ordenar


def pesquisar_e_ordenar(artistas, termo, busca="sequencial", algoritmo="merge"):
    if busca not in ("sequencial", "binaria"):
        raise ValueError("Busca deve ser 'sequencial' ou 'binaria'.")

    if algoritmo not in ALGORITMOS:
        raise ValueError("Algoritmo deve ser 'insertion' ou 'merge'.")

    termo = termo.strip().lower()

    if not termo:
        encontrados = artistas
    elif busca == "sequencial":
        encontrados = busca_sequencial(artistas, termo)
    else:
        indice = construir_indice(artistas)
        ids = busca_binaria(indice, termo)
        encontrados = ids_para_artistas(ids, artistas)

    unicos = []
    ids_vistos = set()

    for artista in encontrados:
        if artista["id"] not in ids_vistos:
            unicos.append(artista)
            ids_vistos.add(artista["id"])

    resultados = preparar_resultados(unicos, termo)

    return ordenar(
        resultados,
        algoritmo,
        key=lambda item: item["chave"],
    )
