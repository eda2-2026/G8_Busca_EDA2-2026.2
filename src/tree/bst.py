class NoBST:
    def __init__(self, chave, id_artista):
        self.chave = chave
        self.ids = [id_artista]
        self.esquerda = None
        self.direita = None


class BST:
    """Árvore binária de busca sem balanceamento, toda iterativa."""

    def __init__(self):
        self.raiz = None
        self._quantidade = 0

    def inserir(self, chave, id_artista):
        if self.raiz is None:
            self.raiz = NoBST(chave, id_artista)
            self._quantidade += 1
            return

        no = self.raiz
        while True:
            if chave == no.chave:
                if id_artista not in no.ids:
                    no.ids.append(id_artista)
                return
            if chave < no.chave:
                if no.esquerda is None:
                    no.esquerda = NoBST(chave, id_artista)
                    self._quantidade += 1
                    return
                no = no.esquerda
            else:
                if no.direita is None:
                    no.direita = NoBST(chave, id_artista)
                    self._quantidade += 1
                    return
                no = no.direita

    def buscar(self, chave):
        no = self.raiz
        while no is not None:
            if chave == no.chave:
                return list(no.ids)
            no = no.esquerda if chave < no.chave else no.direita
        return []

    def altura(self):
        if self.raiz is None:
            return 0

        maior = 0
        pilha = [(self.raiz, 1)]
        while pilha:
            no, profundidade = pilha.pop()
            if profundidade > maior:
                maior = profundidade
            if no.esquerda is not None:
                pilha.append((no.esquerda, profundidade + 1))
            if no.direita is not None:
                pilha.append((no.direita, profundidade + 1))
        return maior

    def __len__(self):
        return self._quantidade
