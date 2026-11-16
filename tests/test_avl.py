import inspect
import math
import random
import unittest

from src.tree import avl
from src.tree.avl import AVL


def conferir_avl(teste, no, minimo=None, maximo=None):
    """Confere fator, altura guardada e ordem de BST em todos os nós.

    Devolve a altura real da subárvore.
    """
    if no is None:
        return 0
    if minimo is not None:
        teste.assertGreater(no.chave, minimo)
    if maximo is not None:
        teste.assertLess(no.chave, maximo)
    altura_esq = conferir_avl(teste, no.esquerda, minimo, no.chave)
    altura_dir = conferir_avl(teste, no.direita, no.chave, maximo)
    teste.assertLessEqual(abs(altura_esq - altura_dir), 1, f"desbalanceado em {no.chave!r}")
    teste.assertEqual(no.altura, 1 + max(altura_esq, altura_dir), f"altura errada em {no.chave!r}")
    return no.altura


def montar(chaves):
    arvore = AVL()
    for chave in chaves:
        arvore.inserir(chave, "id" + chave)
    return arvore


class TestAVLBasico(unittest.TestCase):
    def test_arvore_vazia(self):
        arvore = AVL()
        self.assertEqual(len(arvore), 0)
        self.assertEqual(arvore.altura(), 0)
        self.assertEqual(arvore.buscar("x"), [])

    def test_so_a_raiz_tem_altura_um(self):
        arvore = montar(["rock"])
        self.assertEqual(arvore.altura(), 1)
        self.assertEqual(len(arvore), 1)

    def test_chave_repetida_acumula_ids_sem_duplicar(self):
        arvore = AVL()
        arvore.inserir("rock", "a1")
        arvore.inserir("rock", "a2")
        arvore.inserir("rock", "a1")
        arvore.inserir("rock", "a3")
        self.assertEqual(arvore.buscar("rock"), ["a1", "a2", "a3"])
        self.assertEqual(len(arvore), 1)

    def test_chave_ausente_devolve_lista_vazia(self):
        arvore = montar(["m", "c", "t"])
        self.assertEqual(arvore.buscar("a"), [])
        self.assertEqual(arvore.buscar("z"), [])
        self.assertEqual(arvore.buscar("n"), [])

    def test_buscar_devolve_copia(self):
        arvore = montar(["rock"])
        resultado = arvore.buscar("rock")
        resultado.append("intruso")
        self.assertEqual(arvore.buscar("rock"), ["idrock"])


class TestAVLRotacoes(unittest.TestCase):
    def conferir_formato(self, chaves):
        arvore = montar(chaves)
        self.assertEqual(arvore.raiz.chave, "b")
        self.assertEqual(arvore.raiz.esquerda.chave, "a")
        self.assertEqual(arvore.raiz.direita.chave, "c")
        self.assertEqual(arvore.altura(), 2)
        conferir_avl(self, arvore.raiz)

    def test_rotacao_ll(self):
        self.conferir_formato(["c", "b", "a"])

    def test_rotacao_rr(self):
        self.conferir_formato(["a", "b", "c"])

    def test_rotacao_lr(self):
        self.conferir_formato(["c", "a", "b"])

    def test_rotacao_rl(self):
        self.conferir_formato(["a", "c", "b"])


class TestAVLBalanceamento(unittest.TestCase):
    N = 1000

    def conferir_balanceada(self, chaves):
        arvore = montar(chaves)
        conferir_avl(self, arvore.raiz)
        self.assertEqual(len(arvore), len(chaves))
        self.assertLessEqual(arvore.altura(), 1.44 * math.log2(len(chaves) + 2))
        return arvore

    def test_chaves_crescentes(self):
        self.conferir_balanceada([f"{i:05d}" for i in range(self.N)])

    def test_chaves_decrescentes(self):
        self.conferir_balanceada([f"{i:05d}" for i in reversed(range(self.N))])

    def test_chaves_embaralhadas(self):
        chaves = [f"{i:05d}" for i in range(self.N)]
        random.Random(42).shuffle(chaves)
        arvore = self.conferir_balanceada(chaves)
        for chave in chaves:
            self.assertEqual(arvore.buscar(chave), ["id" + chave])

    def test_ids_de_chave_repetida_sobrevivem_as_rotacoes(self):
        arvore = AVL()
        arvore.inserir("m", "a1")
        for i in range(200):
            arvore.inserir(f"{i:05d}", "x")
            if i % 50 == 0:
                arvore.inserir("m", f"a{i + 2}")
        arvore.inserir("m", "a1")
        conferir_avl(self, arvore.raiz)
        self.assertEqual(arvore.buscar("m"), ["a1", "a2", "a52", "a102", "a152"])
        self.assertEqual(len(arvore), 201)


class TestAVLFonte(unittest.TestCase):
    def test_nao_usa_ordenacao_pronta(self):
        fonte = inspect.getsource(avl)
        self.assertNotIn("sorted(", fonte)
        self.assertNotIn(".sort(", fonte)
        self.assertNotIn("bisect", fonte)


if __name__ == "__main__":
    unittest.main()
