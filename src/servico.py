from src.search.busca import (
    busca_sequencial,
    construir_indice,
    busca_binaria,
    ids_para_artistas,
)
from src.ranking.relevancia import preparar_resultados
from src.sort.api import ALGORITMOS, ordenar
from src.tree.api import INDICES, construir_arvore


BUSCAS = ("sequencial", "binaria", "bst", "avl", "trie", "prefixo")


def pesquisar_e_ordenar(artistas, termo, busca="sequencial", algoritmo="merge"):
    if busca not in BUSCAS:
        opcoes = ", ".join(f"'{nome}'" for nome in BUSCAS)
        raise ValueError(f"Busca deve ser uma de: {opcoes}.")

    # INDICES é lido aqui, e não na importação, para a Trie passar a
    # funcionar assim que for registrada em src/tree/api.py.
    if busca == "prefixo" and "trie" not in INDICES:
        raise ValueError("Busca por prefixo requer a Trie.")
    if busca == "trie" and "trie" not in INDICES:
        raise ValueError("Busca 'trie' requer a Trie.")

    if algoritmo not in ALGORITMOS:
        raise ValueError("Algoritmo deve ser 'insertion' ou 'merge'.")

    termo = termo.strip().lower()

    if not termo:
        encontrados = artistas
    elif busca == "sequencial":
        encontrados = busca_sequencial(artistas, termo)
    elif busca == "binaria":
        indice = construir_indice(artistas)
        ids = busca_binaria(indice, termo)
        encontrados = ids_para_artistas(ids, artistas)
    elif busca == "prefixo":
        ids = construir_arvore(artistas, "trie").buscar_prefixo(termo)
        encontrados = ids_para_artistas(ids, artistas)
    else:
        ids = construir_arvore(artistas, busca).buscar(termo)
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
