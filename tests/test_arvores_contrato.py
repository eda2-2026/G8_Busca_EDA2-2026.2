"""Testes cruzados do T3: toda árvore registrada responde como a busca binária do T1."""

import random
import string
import unittest

from src.search.busca import busca_binaria, carregar_dados, construir_indice
from src.tree.api import INDICES, construir_arvore


def sem_repeticao(ids):
    # o índice do T1 pode repetir um id na mesma chave; as árvores não repetem
    return list(dict.fromkeys(ids))


def varrer_prefixo(indice, prefixo):
    resultado = []
    vistos = set()
    for chave, ids in indice:
        if chave.startswith(prefixo):
            for id_artista in ids:
                if id_artista not in vistos:
                    vistos.add(id_artista)
                    resultado.append(id_artista)
    return resultado


class TestContratoComDadosReais(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artistas = carregar_dados()
        cls.indice = construir_indice(cls.artistas)
        cls.chaves = [chave for chave, _ in cls.indice]
        cls.arvores = {tipo: construir_arvore(cls.artistas, tipo) for tipo in INDICES}

    def test_as_tres_arvores_estao_registradas(self):
        self.assertEqual(set(INDICES), {"bst", "avl", "trie"})

    def test_todas_as_chaves_reais_iguais_a_busca_binaria(self):
        for tipo, arvore in self.arvores.items():
            with self.subTest(tipo=tipo):
                divergentes = [
                    chave for chave in self.chaves
                    if arvore.buscar(chave) != sem_repeticao(busca_binaria(self.indice, chave))
                ]
                self.assertEqual(divergentes, [])

    def test_termos_ausentes_devolvem_lista_vazia(self):
        rng = random.Random(42)
        existentes = set(self.chaves)
        ausentes = []
        while len(ausentes) < 20:
            termo = "".join(rng.choice(string.ascii_lowercase) for _ in range(rng.randint(3, 10)))
            if termo not in existentes:
                ausentes.append(termo)

        for tipo, arvore in self.arvores.items():
            for termo in ausentes:
                with self.subTest(tipo=tipo, termo=termo):
                    self.assertEqual(arvore.buscar(termo), [])

    def test_tamanho_igual_ao_numero_de_chaves(self):
        for tipo, arvore in self.arvores.items():
            with self.subTest(tipo=tipo):
                self.assertEqual(len(arvore), len(self.chaves))

    def test_prefixo_da_trie_igual_a_varredura(self):
        trie = self.arvores["trie"]
        prefixos = sorted({chave[:t] for chave in self.chaves for t in (1, 2, 3)}) + ["", "zzz"]

        divergentes = [
            p for p in prefixos
            if trie.buscar_prefixo(p) != varrer_prefixo(self.indice, p)
        ]
        self.assertEqual(divergentes, [])


if __name__ == "__main__":
    unittest.main()
