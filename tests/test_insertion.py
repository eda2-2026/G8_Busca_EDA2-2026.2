import unittest
from copy import deepcopy

from src.sort.insertion import insertion_sort


class TestInsertionSort(unittest.TestCase):
    def test_ordena_diferentes_entradas(self):
        casos = [
            [],
            [-40],
            [-100, -70, -40],
            [-40, -70, -100],
            [-40, -100, -70, -40],
            [-40, -40, -40],
        ]

        for chaves in casos:
            with self.subTest(chaves=chaves):
                itens = [
                    {"id": i, "chave": chave}
                    for i, chave in enumerate(chaves)
                ]
                original = deepcopy(itens)

                resultado = insertion_sort(
                    itens,
                    key=lambda item: item["chave"],
                )

                self.assertEqual(
                    resultado,
                    sorted(original, key=lambda item: item["chave"]),
                )
                self.assertEqual(itens, original)
                self.assertIsNot(resultado, itens)

    def test_preserva_ordem_dos_empates(self):
        itens = [
            {"id": "a", "chave": -40},
            {"id": "b", "chave": -100},
            {"id": "c", "chave": -40},
        ]

        resultado = insertion_sort(
            itens,
            key=lambda item: item["chave"],
        )

        self.assertEqual(
            [item["id"] for item in resultado],
            ["b", "a", "c"],
        )


if __name__ == "__main__":
    unittest.main()
