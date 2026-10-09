import contextlib
import csv
import io
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from benchmarks.benchmark_ordenacao import (
    ALGORITMOS,
    CAMPOS_CSV,
    CENARIOS,
    ErroValidacao,
    aplicar_cenario,
    caminhos_derivados,
    chave,
    criar_parser,
    deduplicar_por_id,
    executar_caso,
    gerar_sintetico,
    identificar,
    main,
    montar_bases,
    montar_casos,
    resumir,
    tamanhos_catalogo,
)
from src.sort.merge import merge_sort

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


def caso_simples():
    itens = registros([-40, -100, -40, -70])
    return {
        "caso_id": "teste-4-aleatorio",
        "origem": "teste",
        "n": 4,
        "cenario": "aleatorio",
        "semente": 1,
        "chaves_distintas": 3,
        "transformacao": "nenhuma",
        "itens": itens,
    }


class TestMedicao(unittest.TestCase):
    def test_gera_uma_linha_por_algoritmo_e_repeticao_alternando_a_ordem(self):
        linhas = executar_caso(caso_simples(), 4)

        self.assertEqual(len(linhas), 8)
        self.assertEqual(
            [(l["repeticao"], l["algoritmo"]) for l in linhas],
            [(1, "merge"), (1, "insertion"),
             (2, "insertion"), (2, "merge"),
             (3, "merge"), (3, "insertion"),
             (4, "insertion"), (4, "merge")],
        )
        for linha in linhas:
            self.assertEqual(set(linha), set(CAMPOS_CSV))
            self.assertIsInstance(linha["tempo_ms"], float)
            self.assertGreaterEqual(linha["tempo_ms"], 0)

    def test_nao_altera_a_entrada_do_caso(self):
        caso = caso_simples()
        original = deepcopy(caso["itens"])

        executar_caso(caso, 2)

        self.assertEqual(caso["itens"], original)

    def test_algoritmo_instavel_interrompe_a_coleta(self):
        def instavel(itens, key):
            saida = merge_sort(itens, key)
            return saida[:1] + list(reversed(saida[1:3])) + saida[3:]

        with self.assertRaises(ErroValidacao):
            executar_caso(caso_simples(), 2, {"instavel": instavel})

    def test_algoritmo_que_altera_a_entrada_interrompe_a_coleta(self):
        def destrutivo(itens, key):
            itens.reverse()
            return merge_sort(itens, key)

        with self.assertRaises(ErroValidacao):
            executar_caso(caso_simples(), 2, {"destrutivo": destrutivo})

    def test_algoritmo_que_devolve_a_propria_lista_interrompe_a_coleta(self):
        with self.assertRaises(ErroValidacao):
            executar_caso(caso_simples(), 2, {"mesma_lista": lambda itens, key: itens})


class TestResumo(unittest.TestCase):
    def test_mediana_e_iqr_inclusivo(self):
        linhas = [
            {"origem": "o", "n": 4, "cenario": "c", "chaves_distintas": 2,
             "algoritmo": nome, "tempo_ms": t}
            for nome, tempos in (("insertion", [1.0, 2.0, 3.0, 4.0]), ("merge", [5.0, 5.0]))
            for t in tempos
        ]

        resumo = resumir(linhas)

        self.assertEqual(len(resumo), 1)
        self.assertAlmostEqual(resumo[0]["algoritmos"]["insertion"]["mediana"], 2.5)
        self.assertAlmostEqual(resumo[0]["algoritmos"]["insertion"]["iqr"], 1.5)
        self.assertAlmostEqual(resumo[0]["algoritmos"]["merge"]["mediana"], 5.0)
        self.assertAlmostEqual(resumo[0]["algoritmos"]["merge"]["iqr"], 0.0)


class TestCaminhos(unittest.TestCase):
    def test_saida_padrao(self):
        caminhos = caminhos_derivados("benchmarks/resultados_t2.csv")

        self.assertEqual(caminhos["ambiente"], Path("benchmarks/ambiente_t2.json"))
        self.assertEqual(caminhos["entradas"], Path("benchmarks/entradas_t2.json"))
        self.assertEqual(caminhos["resumo"], Path("benchmarks/resumo_t2.md"))

    def test_ensaio_nao_sobrescreve_os_resultados_finais(self):
        caminhos = caminhos_derivados("/tmp/ensaio_t2.csv")

        self.assertEqual(caminhos["ambiente"], Path("/tmp/ensaio_t2_ambiente.json"))
        self.assertEqual(caminhos["entradas"], Path("/tmp/ensaio_t2_entradas.json"))
        self.assertEqual(caminhos["resumo"], Path("/tmp/ensaio_t2_resumo.md"))


class TestCli(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.dir = Path(self.pasta.name)
        self.dados = self.dir / "artistas.json"
        self.dados.write_text(json.dumps(artistas_ficticios()), encoding="utf-8")

    def tearDown(self):
        self.pasta.cleanup()

    def rodar(self, *opcoes):
        argv = ["--dados", str(self.dados), "--repeticoes", "2",
                "--tamanhos-sinteticos", "3", *opcoes]
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return main(argv)

    def test_execucao_completa_gera_os_quatro_arquivos(self):
        saida = self.dir / "sub" / "ensaio.csv"

        codigo = self.rodar("--saida", str(saida))

        self.assertEqual(codigo, 0)
        with open(saida, encoding="utf-8", newline="") as f:
            leitor = csv.DictReader(f)
            self.assertEqual(leitor.fieldnames, CAMPOS_CSV)
            linhas = list(leitor)
        # (1 consulta + 1 catálogo + 2 sintéticos) x 5 cenários x 2 algoritmos x 2 repetições
        self.assertEqual(len(linhas), 80)
        self.assertEqual({l["algoritmo"] for l in linhas}, set(ALGORITMOS))

        caminhos = caminhos_derivados(saida)
        ambiente = json.loads(caminhos["ambiente"].read_text(encoding="utf-8"))
        entradas = json.loads(caminhos["entradas"].read_text(encoding="utf-8"))
        resumo = caminhos["resumo"].read_text(encoding="utf-8")

        self.assertEqual(len(ambiente["dataset_sha256"]), 64)
        self.assertEqual(ambiente["configuracao"]["repeticoes"], 2)
        self.assertEqual(len(entradas), 20)
        self.assertEqual(entradas[0]["caso_id"], "consulta_real-5-aleatorio")
        self.assertTrue(all(len(par) == 2 for par in entradas[0]["itens"]))
        self.assertIn("| consulta_real | 5 | aleatorio |", resumo)

    def test_termo_sem_resultados_registra_a_ausencia(self):
        saida = self.dir / "vazio.csv"

        codigo = self.rodar("--termo", "termo_inexistente", "--saida", str(saida))

        self.assertEqual(codigo, 0)
        ambiente = json.loads(caminhos_derivados(saida)["ambiente"].read_text(encoding="utf-8"))
        self.assertEqual(len(ambiente["observacoes"]), 1)
        self.assertIn("omitida", caminhos_derivados(saida)["resumo"].read_text(encoding="utf-8"))

    def test_dados_inexistentes_retornam_erro_sem_csv(self):
        saida = self.dir / "nada.csv"
        self.dados = self.dir / "nao_existe.json"

        codigo = self.rodar("--saida", str(saida))

        self.assertEqual(codigo, 1)
        self.assertFalse(saida.exists())

    def test_opcoes_invalidas(self):
        parser = criar_parser()
        for argv in (["--repeticoes", "1"], ["--tamanhos-sinteticos", "0"],
                     ["--tamanhos-sinteticos", "x"], ["--semente", "abc"]):
            with self.subTest(argv=argv):
                with contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit) as erro:
                        parser.parse_args(argv)
                self.assertEqual(erro.exception.code, 2)

    def test_padroes_do_guia(self):
        args = criar_parser().parse_args([])

        self.assertEqual(args.dados, "data/processed/artistas.json")
        self.assertEqual(args.termo, "rock")
        self.assertEqual(args.repeticoes, 10)
        self.assertEqual(args.tamanhos_sinteticos, [100, 500, 2000])
        self.assertEqual(args.semente, 42)
        self.assertEqual(args.saida, "benchmarks/resultados_t2.csv")


if __name__ == "__main__":
    unittest.main()
