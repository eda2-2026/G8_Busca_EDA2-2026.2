import contextlib
import csv
import io
import json
import tempfile
import unittest
from pathlib import Path

from benchmarks.benchmark_arvores import (
    CAMPOS_CSV,
    LIMITE_BST_ORDENADA,
    IndiceOrdenado,
    aplicar_ordem,
    estruturas_disponiveis,
    executar_caso,
    gerar_chaves_sinteticas,
    gerar_consultas,
    main,
    montar_casos,
    pares_reais,
    resumir,
    varrer_prefixo,
)
from src.tree.trie import Trie


ARTISTAS = [
    {"id": "a1", "nome": "Rock Band", "generos": ["Rock", "pop"]},
    {"id": "a2", "nome": "Pop Star", "generos": ["pop"]},
    {"id": "a3", "nome": "Rap", "generos": ["rap", "rap metal"]},
]


class TestPreparacao(unittest.TestCase):
    def test_pares_reais_seguem_construir_indice(self):
        pares = pares_reais(ARTISTAS)

        self.assertEqual(pares, [
            ("rock band", "a1"), ("rock", "a1"), ("pop", "a1"),
            ("pop star", "a2"), ("pop", "a2"),
            ("rap", "a3"), ("rap", "a3"), ("rap metal", "a3"),
        ])

    def test_chaves_sinteticas_distintas_e_reprodutiveis(self):
        a = gerar_chaves_sinteticas(500, semente=7)
        b = gerar_chaves_sinteticas(500, semente=7)
        c = gerar_chaves_sinteticas(500, semente=8)

        self.assertEqual(a, b)
        self.assertNotEqual(a, c)
        self.assertEqual(len(set(a)), 500)
        self.assertTrue(all(k == k.strip().lower() and k for k in a))

    def test_ordens(self):
        pares = [(k, f"id{i}") for i, k in enumerate(["d", "b", "a", "c", "e"] * 20)]

        ordenado = aplicar_ordem(pares, "ordenado", semente=1)
        self.assertEqual([k for k, _ in ordenado], sorted(k for k, _ in pares))

        aleatorio = aplicar_ordem(pares, "aleatorio", semente=1)
        self.assertCountEqual(aleatorio, pares)
        self.assertEqual(aleatorio, aplicar_ordem(pares, "aleatorio", semente=1))

        quase = aplicar_ordem(pares, "quase_ordenado", semente=1)
        self.assertCountEqual(quase, pares)
        self.assertNotEqual(quase, ordenado)

        self.assertEqual(aplicar_ordem(pares, "original", semente=1), pares)

    def test_entrada_nao_e_alterada(self):
        pares = [("b", "1"), ("a", "2")]
        aplicar_ordem(pares, "ordenado", semente=1)
        self.assertEqual(pares, [("b", "1"), ("a", "2")])


class TestConsultas(unittest.TestCase):
    def test_consultas_presentes_ausentes_e_prefixos(self):
        chaves = gerar_chaves_sinteticas(300, semente=3)
        consultas = gerar_consultas(chaves, semente=3, quantidade=40)

        self.assertEqual(len(consultas["exatas"]), 40)
        presentes = [c for c in consultas["exatas"] if c in set(chaves)]
        self.assertEqual(len(presentes), 20)
        for tamanho in (1, 2, 3):
            prefixos = consultas["prefixos"][tamanho]
            self.assertTrue(prefixos)
            self.assertTrue(all(len(p) == tamanho for p in prefixos))
        self.assertEqual(consultas, gerar_consultas(chaves, semente=3, quantidade=40))


class TestEstruturas(unittest.TestCase):
    def test_lista_e_trie_sempre_disponiveis(self):
        estruturas = estruturas_disponiveis()

        self.assertIn("lista_ordenada", estruturas)
        self.assertIn("trie", estruturas)

    def test_todas_respondem_igual_a_lista_ordenada(self):
        pares = pares_reais(ARTISTAS)
        referencia = IndiceOrdenado(pares)

        for nome, construir in estruturas_disponiveis().items():
            with self.subTest(estrutura=nome):
                indice = construir(pares)
                for chave in ("rock", "pop", "rap", "rap metal", "jazz"):
                    esperado = list(dict.fromkeys(referencia.buscar(chave)))
                    self.assertEqual(list(dict.fromkeys(indice.buscar(chave))), esperado)

    def test_varredura_igual_a_trie(self):
        pares = pares_reais(ARTISTAS)
        lista = IndiceOrdenado(pares)
        trie = estruturas_disponiveis()["trie"](pares)

        for prefixo in ("r", "ra", "po", "x", ""):
            with self.subTest(prefixo=prefixo):
                self.assertEqual(varrer_prefixo(lista, prefixo), trie.buscar_prefixo(prefixo))

    def test_lista_ordenada_nao_tem_altura(self):
        self.assertIsNone(IndiceOrdenado([("a", "1")]).altura())


class TestCasos(unittest.TestCase):
    def test_casos_reais_e_sinteticos(self):
        casos = montar_casos(ARTISTAS, tamanhos=[50], semente=1, estruturas=["lista_ordenada", "bst", "trie"])
        ids = {c["caso_id"] for c in casos}

        self.assertIn("real-6-original", ids)
        self.assertIn("real-6-aleatorio", ids)
        self.assertIn("sintetico-50-ordenado", ids)
        self.assertIn("sintetico-50-quase_ordenado", ids)

    def test_bst_fica_fora_de_caso_ordenado_grande(self):
        grande = LIMITE_BST_ORDENADA + 1
        casos = montar_casos([], tamanhos=[grande], semente=1, estruturas=["lista_ordenada", "bst", "trie"])
        por_id = {c["caso_id"]: c for c in casos}

        self.assertNotIn("bst", por_id[f"sintetico-{grande}-ordenado"]["estruturas"])
        self.assertNotIn("bst", por_id[f"sintetico-{grande}-quase_ordenado"]["estruturas"])
        self.assertIn("bst", por_id[f"sintetico-{grande}-aleatorio"]["estruturas"])

    def test_executar_caso_gera_linhas_de_todas_as_medidas(self):
        caso = montar_casos(ARTISTAS, tamanhos=[], semente=1, estruturas=["lista_ordenada", "trie"])[0]
        linhas = executar_caso(caso, repeticoes=2, construtores={
            "lista_ordenada": IndiceOrdenado,
            "trie": estruturas_disponiveis()["trie"],
        })

        medidas = {(l["estrutura"], l["medida"]) for l in linhas}
        self.assertIn(("lista_ordenada", "construcao_ms"), medidas)
        self.assertIn(("trie", "busca_exata_us"), medidas)
        self.assertIn(("trie", "altura"), medidas)
        self.assertIn(("trie", "busca_prefixo_us"), medidas)
        self.assertIn(("varredura", "busca_prefixo_us"), medidas)
        self.assertNotIn(("lista_ordenada", "altura"), medidas)
        self.assertTrue(all(set(l) == set(CAMPOS_CSV) for l in linhas))

    def test_executar_caso_detecta_estrutura_errada(self):
        class Quebrada(Trie):
            def buscar(self, chave):
                return ["errado"]

        def construir(pares):
            trie = Quebrada()
            for chave, id_artista in pares:
                trie.inserir(chave, id_artista)
            return trie

        caso = montar_casos(ARTISTAS, tamanhos=[], semente=1, estruturas=["lista_ordenada", "trie"])[0]
        with self.assertRaises(AssertionError):
            executar_caso(caso, repeticoes=2, construtores={
                "lista_ordenada": IndiceOrdenado,
                "trie": construir,
            })


class TestResumoEMain(unittest.TestCase):
    def test_resumo_usa_mediana(self):
        linhas = [
            {"caso_id": "c", "origem": "real", "n": 3, "cenario": "original",
             "estrutura": "trie", "medida": "construcao_ms", "detalhe": "",
             "repeticao": r, "semente": 1, "valor": v}
            for r, v in enumerate([1.0, 3.0, 2.0], start=1)
        ]
        resumo = resumir(linhas)

        self.assertEqual(resumo[0]["mediana"], 2.0)

    def test_main_grava_csv_e_arquivos_derivados(self):
        with tempfile.TemporaryDirectory() as pasta:
            dados = Path(pasta) / "artistas.json"
            dados.write_text(json.dumps(ARTISTAS), encoding="utf-8")
            saida = Path(pasta) / "resultados_teste.csv"

            with contextlib.redirect_stdout(io.StringIO()):
                codigo = main(["--dados", str(dados), "--repeticoes", "2",
                               "--tamanhos-sinteticos", "40", "--saida", str(saida)])

            self.assertEqual(codigo, 0)
            with open(saida, encoding="utf-8") as f:
                linhas = list(csv.DictReader(f))
            self.assertTrue(linhas)
            self.assertEqual(list(linhas[0]), CAMPOS_CSV)
            for nome in ("ambiente_teste.json", "entradas_teste.json", "resumo_teste.md"):
                self.assertTrue((Path(pasta) / nome).exists(), nome)


if __name__ == "__main__":
    unittest.main()
