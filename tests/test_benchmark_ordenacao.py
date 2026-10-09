import unittest
from copy import deepcopy

from benchmarks.benchmark_ordenacao import (
    CENARIOS,
    aplicar_cenario,
    chave,
    deduplicar_por_id,
    gerar_sintetico,
    identificar,
    montar_bases,
    montar_casos,
    tamanhos_catalogo,
)


def artistas_ficticios():
    return [
        {"id": "a", "nome": "Rock", "generos": ["rock"]},
        {"id": "b", "nome": "Rock Trio", "generos": ["rock"]},
        {"id": "c", "nome": "Rock", "generos": ["jazz"]},
        {"id": "d", "nome": "Queen", "generos": ["rock"]},
        {"id": "e", "nome": "Rock Ensemble", "generos": ["jazz"]},
        {"id": "f", "nome": "Samba Trio", "generos": ["samba"]},
    ]


def registros(chaves):
    return [{"id": f"r{i}", "chave": c} for i, c in enumerate(chaves)]


class TestPreparacao(unittest.TestCase):
    def test_tamanhos_do_catalogo_usam_somente_o_disponivel(self):
        self.assertEqual(tamanhos_catalogo(553), [100, 300, 553])
        self.assertEqual(tamanhos_catalogo(300), [100, 300])
        self.assertEqual(tamanhos_catalogo(150), [100, 150])
        self.assertEqual(tamanhos_catalogo(50), [50])
        self.assertEqual(tamanhos_catalogo(0), [])

    def test_deduplica_preservando_a_primeira_ocorrencia(self):
        primeiro = {"id": "x", "nome": "Primeiro"}
        lista = [primeiro, {"id": "y"}, {"id": "x", "nome": "Repetido"}]

        unicos = deduplicar_por_id(lista)

        self.assertEqual([a["id"] for a in unicos], ["x", "y"])
        self.assertIs(unicos[0], primeiro)

    def test_identifica_registros_reais_e_sinteticos(self):
        self.assertEqual(identificar({"artista": {"id": "a"}, "chave": -100}), "a")
        self.assertEqual(identificar({"id": "s-1", "chave": 3}), "s-1")

    def test_sintetico_e_deterministico_e_respeita_a_faixa(self):
        a = gerar_sintetico("sintetico_poucas_chaves", 200, 42)
        b = gerar_sintetico("sintetico_poucas_chaves", 200, 42)
        amplo = gerar_sintetico("sintetico_faixa_ampla", 200, 42)

        self.assertEqual(a, b)
        self.assertEqual(len({x["id"] for x in a}), 200)
        self.assertTrue(all(-100 <= x["chave"] <= 0 for x in a))
        self.assertTrue(all(0 <= x["chave"] <= 1_000_000 for x in amplo))
        self.assertNotEqual(a, gerar_sintetico("sintetico_poucas_chaves", 200, 7))

    def test_bases_com_consulta_normalizada(self):
        artistas = artistas_ficticios()
        original = deepcopy(artistas)

        bases, observacoes = montar_bases(artistas, "  ROCK ", [3], 42)

        self.assertEqual(observacoes, [])
        self.assertEqual(artistas, original)
        origens = [(origem, len(itens)) for origem, itens in bases]
        self.assertEqual(origens, [
            ("consulta_real", 5),
            ("catalogo_real", 6),
            ("sintetico_poucas_chaves", 3),
            ("sintetico_faixa_ampla", 3),
        ])
        consulta = bases[0][1]
        self.assertEqual([identificar(x) for x in consulta], ["a", "b", "c", "d", "e"])
        self.assertEqual([x["score"] for x in consulta], [100, 70, 60, 40, 30])
        self.assertEqual([chave(x) for x in bases[1][1]], [-100, -70, -60, -40, -30, 0])

    def test_consulta_sem_resultados_e_omitida_e_registrada(self):
        bases, observacoes = montar_bases(artistas_ficticios(), "termo_inexistente", [3], 42)

        self.assertNotIn("consulta_real", [origem for origem, _ in bases])
        self.assertEqual(len(observacoes), 1)
        self.assertIn("termo_inexistente", observacoes[0])

    def test_tamanhos_sinteticos_repetidos_nao_duplicam_casos(self):
        bases, _ = montar_bases(artistas_ficticios(), "rock", [3, 3, 2], 42)
        sinteticos = [(o, len(i)) for o, i in bases if o.startswith("sintetico")]

        self.assertEqual(sinteticos, [
            ("sintetico_poucas_chaves", 2),
            ("sintetico_poucas_chaves", 3),
            ("sintetico_faixa_ampla", 2),
            ("sintetico_faixa_ampla", 3),
        ])


class TestCenarios(unittest.TestCase):
    def setUp(self):
        self.base = registros([-40, -100, 0, -70, -40, -30, 0, -100])

    def test_aleatorio_e_uma_permutacao_reproduzivel(self):
        a, _ = aplicar_cenario(self.base, "aleatorio", 123)
        b, _ = aplicar_cenario(self.base, "aleatorio", 123)

        self.assertEqual(a, b)
        self.assertCountEqual([x["id"] for x in a], [x["id"] for x in self.base])

    def test_ordenado_e_inverso(self):
        ordenado, _ = aplicar_cenario(self.base, "ordenado", 1)
        inverso, _ = aplicar_cenario(self.base, "inverso", 1)

        self.assertEqual([chave(x) for x in ordenado], [-100, -100, -70, -40, -40, -30, 0, 0])
        self.assertEqual([chave(x) for x in inverso], [0, 0, -30, -40, -40, -70, -100, -100])

    def test_quase_ordenado_troca_poucos_pares_com_chaves_diferentes(self):
        base = registros(list(range(250)))

        itens, info = aplicar_cenario(base, "quase_ordenado", 5)

        self.assertEqual(info["trocas_pedidas"], 2)
        self.assertEqual(info["trocas_efetivas"], 2)
        fora_do_lugar = sum(1 for i, x in enumerate(itens) if chave(x) != i)
        self.assertTrue(2 <= fora_do_lugar <= 4)

    def test_quase_ordenado_com_chaves_iguais_ou_lista_minima_nao_trava(self):
        iguais, info_iguais = aplicar_cenario(registros([-40] * 50), "quase_ordenado", 5)
        unitario, info_unitario = aplicar_cenario(registros([7]), "quase_ordenado", 5)

        self.assertEqual([x["id"] for x in iguais], [f"r{i}" for i in range(50)])
        self.assertEqual((info_iguais["trocas_pedidas"], info_iguais["trocas_efetivas"]), (1, 0))
        self.assertEqual((info_unitario["trocas_pedidas"], info_unitario["trocas_efetivas"]), (0, 0))
        self.assertEqual(len(unitario), 1)

    def test_todos_iguais_nao_altera_a_base(self):
        original = deepcopy(self.base)

        itens, info = aplicar_cenario(self.base, "todos_iguais", 1)

        self.assertEqual(self.base, original)
        self.assertTrue(all(chave(x) == 0 for x in itens))
        self.assertEqual([x["id"] for x in itens], [x["id"] for x in self.base])
        self.assertIn("transformação experimental", info["transformacao"])

    def test_cenario_desconhecido(self):
        with self.assertRaises(ValueError):
            aplicar_cenario(self.base, "embaralhado", 1)


class TestCasos(unittest.TestCase):
    def test_cinco_cenarios_por_base_com_ids_unicos_e_reproduziveis(self):
        bases, _ = montar_bases(artistas_ficticios(), "rock", [3], 42)

        casos = montar_casos(bases, 42)
        de_novo = montar_casos(bases, 42)

        self.assertEqual(len(casos), len(bases) * len(CENARIOS))
        self.assertEqual(len({c["caso_id"] for c in casos}), len(casos))
        self.assertEqual(casos[0]["caso_id"], "consulta_real-5-aleatorio")
        self.assertEqual(
            [(c["caso_id"], c["semente"], [identificar(x) for x in c["itens"]]) for c in casos],
            [(c["caso_id"], c["semente"], [identificar(x) for x in c["itens"]]) for c in de_novo],
        )
        todos_iguais = [c for c in casos if c["cenario"] == "todos_iguais"]
        self.assertTrue(all(c["chaves_distintas"] == 1 for c in todos_iguais))


if __name__ == "__main__":
    unittest.main()
