from src.tree.avl import AVL
from src.tree.bst import BST


INDICES = {
    "bst": BST,
    "avl": AVL,
}


def construir_arvore(artistas, tipo):
    if tipo not in INDICES:
        opcoes = ", ".join(f"'{nome}'" for nome in INDICES)
        raise ValueError(f"Tipo de árvore deve ser um de: {opcoes}.")

    arvore = INDICES[tipo]()
    for artista in artistas:
        chaves = [artista["nome"]] + list(artista["generos"])
        for chave in chaves:
            arvore.inserir(chave.strip().lower(), artista["id"])
    return arvore
