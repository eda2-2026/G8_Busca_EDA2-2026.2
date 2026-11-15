import unittest

from src.tree.trie import Trie


def montar(pares):
    trie = Trie()
    for chave, id_artista in pares:
        trie.inserir(chave, id_artista)
    return trie


class TestTrieVazia(unittest.TestCase):
    def test_trie_vazia(self):
        trie = Trie()

        self.assertEqual(len(trie), 0)
        self.assertEqual(trie.altura(), 0)
        self.assertEqual(trie.buscar("rock"), [])
        self.assertEqual(trie.buscar_prefixo("r"), [])


class TestTrieBuscaExata(unittest.TestCase):
    def test_encontra_chave_inserida(self):
        trie = montar([("rock", "a1")])

        self.assertEqual(trie.buscar("rock"), ["a1"])

    def test_chave_ausente_devolve_lista_vazia(self):
        trie = montar([("rock", "a1")])

        self.assertEqual(trie.buscar("pop"), [])
        self.assertEqual(trie.buscar("roc"), [])
        self.assertEqual(trie.buscar("rocks"), [])
        self.assertEqual(trie.buscar(""), [])

    def test_chave_repetida_acumula_ids_na_ordem_de_insercao(self):
        trie = montar([("rock", "a2"), ("rock", "a1"), ("rock", "a3")])

        self.assertEqual(trie.buscar("rock"), ["a2", "a1", "a3"])
        self.assertEqual(len(trie), 1)

    def test_mesmo_id_na_mesma_chave_nao_duplica(self):
        trie = montar([("rock", "a1"), ("rock", "a1")])

        self.assertEqual(trie.buscar("rock"), ["a1"])

    def test_chave_prefixo_de_outra(self):
        trie = montar([("rap metal", "a1"), ("rap", "a2")])

        self.assertEqual(trie.buscar("rap"), ["a2"])
        self.assertEqual(trie.buscar("rap metal"), ["a1"])
        self.assertEqual(len(trie), 2)

    def test_normaliza_maiusculas_e_espacos_nas_pontas(self):
        trie = montar([("  Rock ", "a1")])

        self.assertEqual(trie.buscar("ROCK"), ["a1"])
        self.assertEqual(trie.buscar(" rock  "), ["a1"])

    def test_acentos_sao_caracteres_distintos(self):
        trie = montar([("forró", "a1"), ("forro", "a2")])

        self.assertEqual(trie.buscar("forró"), ["a1"])
        self.assertEqual(trie.buscar("forro"), ["a2"])

    def test_devolve_copia_da_lista(self):
        trie = montar([("rock", "a1")])

        trie.buscar("rock").append("intruso")

        self.assertEqual(trie.buscar("rock"), ["a1"])


class TestTriePrefixo(unittest.TestCase):
    def setUp(self):
        self.trie = montar([
            ("rock", "a1"),
            ("rap", "a2"),
            ("roberto carlos", "a3"),
            ("rap metal", "a4"),
            ("rock", "a5"),
            ("pop", "a6"),
            ("rap", "a1"),
        ])

    def test_prefixo_coleta_ids_em_ordem_alfabetica_das_chaves(self):
        # chaves com "ro": "roberto carlos" < "rock"
        self.assertEqual(self.trie.buscar_prefixo("ro"), ["a3", "a1", "a5"])

    def test_prefixo_nao_repete_id(self):
        # "rap" -> a2, a1; "rap metal" -> a4; "roberto carlos" -> a3; "rock" -> a1 (repetido), a5
        self.assertEqual(
            self.trie.buscar_prefixo("r"),
            ["a2", "a1", "a4", "a3", "a5"],
        )

    def test_prefixo_igual_a_chave_inclui_a_propria_chave(self):
        self.assertEqual(self.trie.buscar_prefixo("rap"), ["a2", "a1", "a4"])

    def test_prefixo_ausente(self):
        self.assertEqual(self.trie.buscar_prefixo("x"), [])
        self.assertEqual(self.trie.buscar_prefixo("rockabilly"), [])

    def test_prefixo_vazio_devolve_todos_os_ids(self):
        self.assertEqual(
            self.trie.buscar_prefixo(""),
            ["a6", "a2", "a1", "a4", "a3", "a5"],
        )

    def test_prefixo_normalizado(self):
        self.assertEqual(self.trie.buscar_prefixo("  RO "), ["a3", "a1", "a5"])

    def test_prefixo_com_espaco_interno(self):
        self.assertEqual(self.trie.buscar_prefixo("rap m"), ["a4"])


class TestTrieTamanhoEAltura(unittest.TestCase):
    def test_len_conta_chaves_distintas(self):
        trie = montar([("rock", "a1"), ("rock", "a2"), ("pop", "a3")])

        self.assertEqual(len(trie), 2)

    def test_altura_e_maior_chave_mais_raiz(self):
        trie = montar([("pop", "a1"), ("rap metal", "a2"), ("rock", "a3")])

        self.assertEqual(trie.altura(), len("rap metal") + 1)

    def test_muitas_chaves_longas_sem_erro_de_recursao(self):
        chave = "a" * 3000
        trie = montar([(chave, "a1")])

        self.assertEqual(trie.buscar(chave), ["a1"])
        self.assertEqual(trie.buscar_prefixo("aaa"), ["a1"])
        self.assertEqual(trie.altura(), 3001)


if __name__ == "__main__":
    unittest.main()
