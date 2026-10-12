import unittest
from copy import deepcopy

from src.sort.merge import merge_sort


def chave(item):
    return item["chave"]


def montar(chaves):
    return [{"id": f"id{i}", "chave": c} for i, c in enumerate(chaves)]


class TestMergeSort(unittest.TestCase):
    def test_ordena_diferentes_entradas(self):
        casos = [
            [],
            [-40],
            [-70, -100, -40],
            [-100, -70, -40, 0],
            [0, -40, -70, -100],
            [5, -3, 0, -3, 12, -8, 5],
            [-40, -40, -40, -40],
        ]

        for chaves in casos:
            with self.subTest(chaves=chaves):
                itens = montar(chaves)
                original = deepcopy(itens)

                resultado = merge_sort(itens, key=chave)

                self.assertEqual(resultado, sorted(original, key=chave))
                self.assertEqual(itens, original)
                self.assertIsNot(resultado, itens)

    def test_unitario_retorna_nova_lista_com_o_mesmo_registro(self):
        itens = [{"id": "a", "chave": 0}]

        resultado = merge_sort(itens, key=chave)

        self.assertIsNot(resultado, itens)
        self.assertEqual(len(resultado), 1)
        self.assertIs(resultado[0], itens[0])

    def test_empates_entre_as_duas_metades_preservam_a_ordem(self):
        # meio = 3: "a" e "b" ficam na metade esquerda, "d" e "f" na direita.
        itens = [
            {"id": "a", "chave": -40},
            {"id": "b", "chave": -40},
            {"id": "c", "chave": -100},
            {"id": "d", "chave": -40},
            {"id": "e", "chave": -100},
            {"id": "f", "chave": -40},
        ]

        resultado = merge_sort(itens, key=chave)

        self.assertEqual(
            [item["id"] for item in resultado],
            ["c", "e", "a", "b", "d", "f"],
        )

    def test_preserva_registros_completos(self):
        itens = [
            {"id": "x", "chave": 0, "artista": {"nome": "X", "generos": ["rock"]}},
            {"id": "y", "chave": -70, "artista": {"nome": "Y", "generos": []}},
        ]
        original = deepcopy(itens)

        resultado = merge_sort(itens, key=chave)

        self.assertEqual(itens, original)
        self.assertIs(resultado[0], itens[1])
        self.assertIs(resultado[1], itens[0])


if __name__ == "__main__":
    unittest.main()
