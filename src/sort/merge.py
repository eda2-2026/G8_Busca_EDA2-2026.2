def merge_sort(itens, key):
    dados = list(itens)

    def ordenar(parte):
        if len(parte) <= 1:
            return parte

        meio = len(parte) // 2
        esquerda = ordenar(parte[:meio])
        direita = ordenar(parte[meio:])

        resultado = []
        i = j = 0

        while i < len(esquerda) and j < len(direita):
            # "<=" escolhe a metade esquerda no empate: é isso que garante estabilidade.
            if key(esquerda[i]) <= key(direita[j]):
                resultado.append(esquerda[i])
                i += 1
            else:
                resultado.append(direita[j])
                j += 1

        resultado.extend(esquerda[i:])
        resultado.extend(direita[j:])
        return resultado

    return ordenar(dados)
