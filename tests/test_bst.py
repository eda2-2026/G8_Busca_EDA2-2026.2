import inspect
import unittest

from src.tree import bst
from src.tree.bst import BST


class TestBST(unittest.TestCase):
    def test_arvore_vazia(self):
        arvore = BST()
        self.assertEqual(len(arvore), 0)
        self.assertEqual(arvore.altura(), 0)
        self.assertEqual(arvore.buscar("x"), [])

    def test_so_a_raiz_tem_altura_um(self):
        arvore = BST()
        arvore.inserir("rock", "a1")
        self.assertEqual(arvore.altura(), 1)
        self.assertEqual(len(arvore), 1)

    def test_chave_repetida_acumula_ids_sem_duplicar(self):
        arvore = BST()
        arvore.inserir("rock", "a1")
        arvore.inserir("rock", "a2")
        arvore.inserir("rock", "a1")
        arvore.inserir("rock", "a3")
        self.assertEqual(arvore.buscar("rock"), ["a1", "a2", "a3"])
        self.assertEqual(len(arvore), 1)

    def test_chave_ausente_devolve_lista_vazia(self):
        arvore = BST()
        for chave in ["m", "c", "t"]:
            arvore.inserir(chave, chave + "1")
        self.assertEqual(arvore.buscar("a"), [])
        self.assertEqual(arvore.buscar("z"), [])
        self.assertEqual(arvore.buscar("n"), [])

    def test_buscar_devolve_copia(self):
        arvore = BST()
        arvore.inserir("rock", "a1")
        resultado = arvore.buscar("rock")
        resultado.append("intruso")
        self.assertEqual(arvore.buscar("rock"), ["a1"])

    def test_altura_de_formato_conhecido(self):
        arvore = BST()
        for chave in ["m", "c", "t", "a"]:
            arvore.inserir(chave, chave + "1")
        self.assertEqual(arvore.altura(), 3)
        self.assertEqual(len(arvore), 4)
        for chave in ["m", "c", "t", "a"]:
            self.assertEqual(arvore.buscar(chave), [chave + "1"])

    def test_chaves_crescentes_degeneram_sem_recursion_error(self):
        arvore = BST()
        chaves = [f"{i:05d}" for i in range(2000)]
        for chave in chaves:
            arvore.inserir(chave, "id" + chave)
        self.assertEqual(arvore.altura(), 2000)
        self.assertEqual(len(arvore), 2000)
        self.assertEqual(arvore.buscar("01999"), ["id01999"])
        self.assertEqual(arvore.buscar("02000"), [])

    def test_nao_usa_ordenacao_pronta(self):
        fonte = inspect.getsource(bst)
        self.assertNotIn("sorted(", fonte)
        self.assertNotIn(".sort(", fonte)
        self.assertNotIn("bisect", fonte)


if __name__ == "__main__":
    unittest.main()
