import unittest
from copy import deepcopy

from src.servico import pesquisar_e_ordenar


class TestServico(unittest.TestCase):
    def setUp(self):
        self.artistas = [
            {"id": "a", "nome": "Queen", "generos": ["rock"]},
            {"id": "b", "nome": "Rock Trio", "generos": ["rock"]},
            {"id": "c", "nome": "Rock", "generos": ["rock"]},
            {"id": "d", "nome": "Samba Trio", "generos": ["samba"]},
        ]

    def test_ordena_por_relevancia_sem_alterar_entrada(self):
        original = deepcopy(self.artistas)

        resultados = pesquisar_e_ordenar(self.artistas, "rock")

        self.assertEqual(
            [r["artista"]["id"] for r in resultados],
            ["c", "b", "a"],
        )
        self.assertEqual(
            [r["score"] for r in resultados],
            [100, 70, 40],
        )
        self.assertEqual(self.artistas, original)

    def test_busca_binaria_remove_resultados_duplicados(self):
        resultados = pesquisar_e_ordenar(
            self.artistas,
            "rock",
            busca="binaria",
        )

        self.assertEqual(
            [r["artista"]["id"] for r in resultados],
            ["c", "b", "a"],
        )

    def test_consulta_vazia_lista_todos(self):
        for busca in ("sequencial", "binaria"):
            with self.subTest(busca=busca):
                resultados = pesquisar_e_ordenar(
                    self.artistas,
                    "   ",
                    busca=busca,
                )

                self.assertEqual(
                    [r["artista"]["id"] for r in resultados],
                    ["a", "b", "c", "d"],
                )
                self.assertTrue(
                    all(r["score"] == 0 for r in resultados)
                )

    def test_termo_inexistente(self):
        for busca in ("sequencial", "binaria"):
            with self.subTest(busca=busca):
                self.assertEqual(
                    pesquisar_e_ordenar(
                        self.artistas,
                        "xyz_inexistente",
                        busca=busca,
                    ),
                    [],
                )

    def test_normaliza_consulta(self):
        resultados = pesquisar_e_ordenar(
            self.artistas,
            " ROCK ",
        )

        self.assertEqual(
            [r["artista"]["id"] for r in resultados],
            ["c", "b", "a"],
        )

    def test_preserva_diferenca_entre_buscas(self):
        sequencial = pesquisar_e_ordenar(
            self.artistas, "roc", busca="sequencial"
        )
        binaria = pesquisar_e_ordenar(
            self.artistas, "roc", busca="binaria"
        )

        self.assertEqual(
            [r["artista"]["id"] for r in sequencial],
            ["b", "c"],
        )
        self.assertEqual(binaria, [])

    def test_rejeita_busca_invalida(self):
        with self.assertRaises(ValueError):
            pesquisar_e_ordenar(
                self.artistas,
                "",
                busca="invalida",
            )


if __name__ == "__main__":
    unittest.main()
