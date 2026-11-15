class _No:
    __slots__ = ("filhos", "letras", "ids")

    def __init__(self):
        self.filhos = {}   # caractere -> _No
        self.letras = []   # caracteres dos filhos, mantidos em ordem crescente
        self.ids = []      # vazio se nenhuma chave termina neste nó

    def filho_ou_novo(self, letra):
        filho = self.filhos.get(letra)
        if filho is not None:
            return filho

        filho = _No()
        self.filhos[letra] = filho

        # inserção ordenada (como no insertion sort) para percorrer em ordem alfabética
        self.letras.append(letra)
        i = len(self.letras) - 1
        while i > 0 and self.letras[i - 1] > letra:
            self.letras[i] = self.letras[i - 1]
            i -= 1
        self.letras[i] = letra

        return filho


def _normalizar(texto):
    return texto.strip().lower()


class Trie:
    """Árvore de prefixos: cada aresta é um caractere da chave.

    Busca exata e por prefixo custam O(m), com m = tamanho do termo,
    independentemente de quantas chaves estão guardadas.
    """

    def __init__(self):
        self._raiz = _No()
        self._tamanho = 0

    def inserir(self, chave, id_artista):
        chave = _normalizar(chave)
        if not chave:
            return

        no = self._raiz
        for letra in chave:
            no = no.filho_ou_novo(letra)

        if not no.ids:
            self._tamanho += 1
        if id_artista not in no.ids:
            no.ids.append(id_artista)

    def _descer(self, texto):
        no = self._raiz
        for letra in texto:
            no = no.filhos.get(letra)
            if no is None:
                return None
        return no

    def buscar(self, chave):
        no = self._descer(_normalizar(chave))
        if no is None:
            return []
        return list(no.ids)

    def buscar_prefixo(self, prefixo):
        inicio = self._descer(_normalizar(prefixo))
        if inicio is None:
            return []

        resultado = []
        vistos = set()

        # DFS iterativa em pré-ordem: a chave do nó vem antes das chaves que a estendem,
        # e os filhos são visitados em ordem alfabética (empilhados ao contrário).
        pilha = [inicio]
        while pilha:
            no = pilha.pop()
            for id_artista in no.ids:
                if id_artista not in vistos:
                    vistos.add(id_artista)
                    resultado.append(id_artista)
            for i in range(len(no.letras) - 1, -1, -1):
                pilha.append(no.filhos[no.letras[i]])

        return resultado

    def altura(self):
        if self._tamanho == 0:
            return 0

        maior = 0
        pilha = [(self._raiz, 1)]
        while pilha:
            no, nivel = pilha.pop()
            if nivel > maior:
                maior = nivel
            for filho in no.filhos.values():
                pilha.append((filho, nivel + 1))
        return maior

    def __len__(self):
        return self._tamanho
