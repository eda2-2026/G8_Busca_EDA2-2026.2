import importlib.util
import inspect
import random
import unittest
from collections import Counter
from copy import deepcopy

from src.sort import insertion, merge
from src.sort.insertion import insertion_sort
from src.sort.merge import merge_sort

ALGORITMOS = {"insertion": insertion_sort, "merge": merge_sort}
MODULOS = {"insertion": insertion, "merge": merge}
TEM_ADAPTADOR = importlib.util.find_spec("src.sort.api") is not None


def chave(item):
    return item["chave"]


def montar(chaves):
    return [
        {"id": f"id{i}", "chave": c, "payload": {"posicao_original": i}}
        for i, c in enumerate(chaves)
    ]


def casos_fixos():
    return {
        "vazio": [],
        "unitario": [-40],
        "ordenado": [-100, -70, -60, -40, -30, 0],
        "inverso": [0, -30, -40, -60, -70, -100],
        "todos_iguais": [-40] * 7,
        "negativos_e_positivos": [3, -5, 0, -5, 8, -1],
        "empates_com_ids_diferentes": [-40, -100, -40, -70, -100, -40],
    }


def casos_aleatorios():
    rng = random.Random(42)
    casos = []
    for _ in range(20):
        n = rng.randint(0, 100)
        casos.append([rng.randint(-5, 0) for _ in range(n)])
    return casos


class TestContratoDosAlgoritmos(unittest.TestCase):
    def verificar(self, algoritmo, chaves):
        itens = montar(chaves)
        original = deepcopy(itens)

        resultado = algoritmo(itens, key=chave)
        esperado = sorted(itens, key=chave)  # oráculo estável, só no teste

        self.assertEqual(resultado, esperado)
        self.assertTrue(all(a is b for a, b in zip(resultado, esperado)))
        self.assertEqual(
            Counter(item["id"] for item in resultado),
            Counter(item["id"] for item in original),
        )
        self.assertEqual(itens, original)
        self.assertIsNot(resultado, itens)

    def test_casos_fixos(self):
        for nome_caso, chaves in casos_fixos().items():
            for nome, algoritmo in ALGORITMOS.items():
                with self.subTest(caso=nome_caso, algoritmo=nome):
                    self.verificar(algoritmo, chaves)

    def test_casos_aleatorios_com_muitos_empates(self):
        for indice, chaves in enumerate(casos_aleatorios()):
            for nome, algoritmo in ALGORITMOS.items():
                with self.subTest(caso=indice, n=len(chaves), algoritmo=nome):
                    self.verificar(algoritmo, chaves)

    def test_insertion_e_merge_produzem_a_mesma_lista(self):
        todos = list(casos_fixos().values()) + casos_aleatorios()
        for indice, chaves in enumerate(todos):
            with self.subTest(caso=indice):
                itens = montar(chaves)
                saida_insertion = insertion_sort(itens, key=chave)
                saida_merge = merge_sort(itens, key=chave)
                self.assertEqual(
                    [item["id"] for item in saida_insertion],
                    [item["id"] for item in saida_merge],
                )

    def test_exemplo_de_estabilidade_do_contrato(self):
        itens = [
            {"id": "a", "chave": -40},
            {"id": "b", "chave": -100},
            {"id": "c", "chave": -40},
        ]
        for nome, algoritmo in ALGORITMOS.items():
            with self.subTest(algoritmo=nome):
                saida = algoritmo(itens, key=chave)
                self.assertEqual([x["id"] for x in saida], ["b", "a", "c"])

    def test_algoritmos_nao_usam_ordenacao_pronta(self):
        for nome, modulo in MODULOS.items():
            with self.subTest(algoritmo=nome):
                fonte = inspect.getsource(modulo)
                self.assertNotIn("sorted(", fonte)
                self.assertNotIn(".sort(", fonte)


@unittest.skipUnless(TEM_ADAPTADOR, "src/sort/api.py ainda não foi integrado (A4)")
class TestAdaptador(unittest.TestCase):
    def test_registra_os_dois_nomes(self):
        from src.sort.api import ALGORITMOS as REGISTRO

        self.assertIs(REGISTRO["insertion"], insertion_sort)
        self.assertIs(REGISTRO["merge"], merge_sort)

    def test_ordenar_delega_ao_algoritmo_escolhido(self):
        from src.sort.api import ordenar

        itens = montar([-40, -100, -40])
        for nome in ("insertion", "merge"):
            with self.subTest(algoritmo=nome):
                saida = ordenar(itens, nome, key=chave)
                self.assertEqual([x["id"] for x in saida], ["id1", "id0", "id2"])

    def test_algoritmo_desconhecido_gera_value_error(self):
        from src.sort.api import ordenar

        with self.assertRaises(ValueError):
            ordenar(montar([0, -1]), "bubble", key=chave)


if __name__ == "__main__":
    unittest.main()
