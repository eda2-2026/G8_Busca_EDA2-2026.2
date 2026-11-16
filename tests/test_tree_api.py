import unittest

from src.search.busca import busca_binaria, carregar_dados, construir_indice
from src.tree.api import INDICES, construir_arvore


class TestConstruirArvore(unittest.TestCase):
    def test_tipo_invalido_levanta_value_error(self):
        with self.assertRaises(ValueError):
            construir_arvore([], "invalido")

    def test_lista_vazia_devolve_arvore_vazia(self):
        for tipo in INDICES:
            with self.subTest(tipo=tipo):
                arvore = construir_arvore([], tipo)
                self.assertEqual(len(arvore), 0)
                self.assertEqual(arvore.buscar("rock"), [])

    def test_normaliza_nome_e_generos(self):
        artistas = [{"id": "a", "nome": "  Queen ", "generos": [" Rock", "HARD ROCK"]}]
        for tipo in INDICES:
            with self.subTest(tipo=tipo):
                arvore = construir_arvore(artistas, tipo)
                self.assertEqual(arvore.buscar("queen"), ["a"])
                self.assertEqual(arvore.buscar("rock"), ["a"])
                self.assertEqual(arvore.buscar("hard rock"), ["a"])
                self.assertEqual(len(arvore), 3)

    def test_nome_igual_a_genero_nao_duplica_id(self):
        artistas = [
            {"id": "a", "nome": "Anitta", "generos": ["funk", "anitta"]},
            {"id": "b", "nome": "Outro", "generos": ["anitta"]},
        ]
        for tipo in INDICES:
            with self.subTest(tipo=tipo):
                arvore = construir_arvore(artistas, tipo)
                self.assertEqual(arvore.buscar("anitta"), ["a", "b"])


class TestDadosReais(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artistas = carregar_dados()
        cls.indice = construir_indice(cls.artistas)

    def test_mesmo_numero_de_chaves_que_o_indice(self):
        self.assertEqual(len(self.indice), 979)
        for tipo in INDICES:
            with self.subTest(tipo=tipo):
                self.assertEqual(len(construir_arvore(self.artistas, tipo)), len(self.indice))

    def test_toda_chave_igual_a_busca_binaria(self):
        for tipo in INDICES:
            arvore = construir_arvore(self.artistas, tipo)
            for chave, _ in self.indice:
                with self.subTest(tipo=tipo, chave=chave):
                    esperado = list(dict.fromkeys(busca_binaria(self.indice, chave)))
                    self.assertEqual(arvore.buscar(chave), esperado)

    def test_termos_ausentes_devolvem_lista_vazia(self):
        for tipo in INDICES:
            arvore = construir_arvore(self.artistas, tipo)
            for termo in ["", "zzzz", "roc", "rock ", "Rock"]:
                with self.subTest(tipo=tipo, termo=termo):
                    self.assertEqual(arvore.buscar(termo), [])


if __name__ == "__main__":
    unittest.main()
