from src.sort.insertion import insertion_sort
from src.sort.merge import merge_sort


ALGORITMOS = {
    "insertion": insertion_sort,
    "merge": merge_sort,
}


def ordenar(itens, algoritmo, key):
    if algoritmo not in ALGORITMOS:
        raise ValueError("Algoritmo deve ser 'insertion' ou 'merge'.")

    return ALGORITMOS[algoritmo](itens, key=key)
