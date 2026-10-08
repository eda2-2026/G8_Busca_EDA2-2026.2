import unittest
from copy import deepcopy

from src.ranking.relevancia import (
    pontuar_artista,
    preparar_resultados,
)


class TestRanking(unittest.TestCase):
    def test_pontuacao_por_nome_e_genero(self):
        casos = [
            ("Rock", ["rock"], 100),
            ("Rock Trio", ["rock"], 70),
            ("Rock", ["jazz"], 60),
            ("Queen", ["rock"], 40),
            ("Rock Ensemble", ["jazz"], 30),
            ("Samba Trio", ["samba"], 0),
        ]

        for nome, generos, esperado in casos:
            with self.subTest(nome=nome, generos=generos):
                artista = {"nome": nome, "generos": generos}

                self.assertEqual(
                    pontuar_artista(artista, "rock"),
                    esperado,
                )

    def test_normaliza_maiusculas_e_espacos(self):
        artista = {
            "nome": " ROCK TRIO ",
            "generos": [" ROCK "],
        }

        self.assertEqual(
            pontuar_artista(artista, " Rock "),
            70,
        )

    def test_genero_repetido_nao_soma_pontos_extras(self):
        artista = {
            "nome": "Queen",
            "generos": ["rock", "ROCK", "rock"],
        }

        self.assertEqual(pontuar_artista(artista, "rock"), 40)

    def test_consulta_vazia_recebe_zero(self):
        artista = {"nome": "Rock", "generos": ["rock"]}

        for termo in ["", "   "]:
            with self.subTest(termo=termo):
                self.assertEqual(
                    pontuar_artista(artista, termo),
                    0,
                )

    def test_preparacao_preserva_dados_e_cria_chave(self):
        artistas = [
            {
                "id": "a",
                "nome": "Rock Trio",
                "generos": ["rock"],
                "ano_formacao": None,
                "ouvintes": None,
            },
            {
                "id": "b",
                "nome": "Queen",
                "generos": ["rock"],
            },
        ]
        original = deepcopy(artistas)

        resultados = preparar_resultados(artistas, "rock")

        self.assertEqual(artistas, original)
        self.assertIsNot(resultados, artistas)
        self.assertEqual(len(resultados), 2)
        self.assertEqual(
            [r["artista"] for r in resultados],
            original,
        )
        self.assertEqual(
            [r["score"] for r in resultados],
            [70, 40],
        )
        self.assertEqual(
            [r["chave"] for r in resultados],
            [-70, -40],
        )

    def test_lista_vazia(self):
        self.assertEqual(preparar_resultados([], "rock"), [])


if __name__ == "__main__":
    unittest.main()
