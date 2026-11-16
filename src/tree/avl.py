class NoAVL:
    def __init__(self, chave, id_artista):
        self.chave = chave
        self.ids = [id_artista]
        self.esquerda = None
        self.direita = None
        self.altura = 1


def _altura(no):
    return 0 if no is None else no.altura


def _atualizar_altura(no):
    no.altura = 1 + max(_altura(no.esquerda), _altura(no.direita))


def _fator(no):
    return _altura(no.esquerda) - _altura(no.direita)


def _rotacao_direita(y):
    x = y.esquerda
    y.esquerda = x.direita
    x.direita = y
    _atualizar_altura(y)
    _atualizar_altura(x)
    return x


def _rotacao_esquerda(x):
    y = x.direita
    x.direita = y.esquerda
    y.esquerda = x
    _atualizar_altura(x)
    _atualizar_altura(y)
    return y


class AVL:
    """Árvore AVL: BST que se rebalanceia com rotações a cada inserção."""

    def __init__(self):
        self.raiz = None
        self._quantidade = 0

    def inserir(self, chave, id_artista):
        self.raiz = self._inserir(self.raiz, chave, id_artista)

    def _inserir(self, no, chave, id_artista):
        if no is None:
            self._quantidade += 1
            return NoAVL(chave, id_artista)

        if chave == no.chave:
            if id_artista not in no.ids:
                no.ids.append(id_artista)
            return no

        if chave < no.chave:
            no.esquerda = self._inserir(no.esquerda, chave, id_artista)
        else:
            no.direita = self._inserir(no.direita, chave, id_artista)

        _atualizar_altura(no)
        fator = _fator(no)

        if fator > 1 and chave < no.esquerda.chave:  # LL
            return _rotacao_direita(no)
        if fator < -1 and chave > no.direita.chave:  # RR
            return _rotacao_esquerda(no)
        if fator > 1 and chave > no.esquerda.chave:  # LR
            no.esquerda = _rotacao_esquerda(no.esquerda)
            return _rotacao_direita(no)
        if fator < -1 and chave < no.direita.chave:  # RL
            no.direita = _rotacao_direita(no.direita)
            return _rotacao_esquerda(no)

        return no

    def buscar(self, chave):
        no = self.raiz
        while no is not None:
            if chave == no.chave:
                return list(no.ids)
            no = no.esquerda if chave < no.chave else no.direita
        return []

    def altura(self):
        return _altura(self.raiz)

    def __len__(self):
        return self._quantidade
