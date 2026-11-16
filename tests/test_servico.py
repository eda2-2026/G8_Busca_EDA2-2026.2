import unittest
from copy import deepcopy

from src.servico import pesquisar_e_ordenar
from src.tree.api import INDICES


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

    def test_algoritmos_produzem_mesma_lista_inclusive_empates(self):
        self.artistas.append(
            {"id": "e", "nome": "Outra Banda", "generos": ["rock"]}
        )
        original = deepcopy(self.artistas)

        for busca in ("sequencial", "binaria"):
            for termo, ids_esperados in (
                ("rock", ["c", "b", "a", "e"]),
                ("   ", ["a", "b", "c", "d", "e"]),
                ("xyz_inexistente", []),
            ):
                with self.subTest(busca=busca, termo=termo):
                    saidas = [
                        pesquisar_e_ordenar(
                            self.artistas, termo, busca=busca,
                            algoritmo=algoritmo,
                        )
                        for algoritmo in ("insertion", "merge")
                    ]
                    self.assertEqual(saidas[0], saidas[1])
                    self.assertEqual(
                        [r["artista"]["id"] for r in saidas[0]],
                        ids_esperados,
                    )
                    self.assertEqual(self.artistas, original)

    def test_rejeita_algoritmo_invalido_mesmo_sem_resultados(self):
        for artistas in (self.artistas, []):
            for termo in ("rock", "", "xyz_inexistente"):
                with self.subTest(n=len(artistas), termo=termo):
                    with self.assertRaisesRegex(ValueError, "Algoritmo"):
                        pesquisar_e_ordenar(
                            artistas, termo, algoritmo="invalido"
                        )

    def test_arvores_iguais_a_binaria(self):
        self.artistas.append(
            {"id": "e", "nome": "Queen Cover", "generos": ["rock", "queen"]}
        )
        original = deepcopy(self.artistas)

        for busca in ("bst", "avl"):
            for termo in ("rock", "samba trio", "xyz_inexistente", "  ROCK ", "Queen"):
                with self.subTest(busca=busca, termo=termo):
                    esperado = pesquisar_e_ordenar(
                        self.artistas, termo, busca="binaria"
                    )
                    obtido = pesquisar_e_ordenar(
                        self.artistas, termo, busca=busca
                    )
                    self.assertEqual(obtido, esperado)
                    self.assertEqual(self.artistas, original)

    def test_arvores_com_termo_vazio_listam_todos(self):
        for busca in ("bst", "avl"):
            with self.subTest(busca=busca):
                resultados = pesquisar_e_ordenar(
                    self.artistas, "   ", busca=busca
                )
                self.assertEqual(
                    [r["artista"]["id"] for r in resultados],
                    ["a", "b", "c", "d"],
                )

    @unittest.skipIf("trie" in INDICES, "Trie já registrada")
    def test_sem_trie_prefixo_e_trie_levantam_erro(self):
        with self.assertRaisesRegex(ValueError, "Busca por prefixo requer a Trie."):
            pesquisar_e_ordenar(self.artistas, "ro", busca="prefixo")
        with self.assertRaisesRegex(ValueError, "requer a Trie"):
            pesquisar_e_ordenar(self.artistas, "rock", busca="trie")

    @unittest.skipUnless("trie" in INDICES, "Trie ainda não registrada")
    def test_trie_igual_a_binaria(self):
        for termo in ("rock", "samba trio", "xyz_inexistente", "  ROCK "):
            with self.subTest(termo=termo):
                self.assertEqual(
                    pesquisar_e_ordenar(self.artistas, termo, busca="trie"),
                    pesquisar_e_ordenar(self.artistas, termo, busca="binaria"),
                )

    @unittest.skipUnless("trie" in INDICES, "Trie ainda não registrada")
    def test_prefixo_encontra_por_inicio_da_chave(self):
        resultados = pesquisar_e_ordenar(self.artistas, "ro", busca="prefixo")
        ids = {r["artista"]["id"] for r in resultados}
        self.assertIn("b", ids)  # Rock Trio
        self.assertIn("c", ids)  # Rock
        self.assertNotIn("d", ids)  # Samba Trio


if __name__ == "__main__":
    unittest.main()
