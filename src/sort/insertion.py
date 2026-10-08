def insertion_sort(itens, key):
    resultado = list(itens)

    for i in range(1, len(resultado)):
        atual = resultado[i]
        chave_atual = key(atual)
        j = i - 1

        while j >= 0 and key(resultado[j]) > chave_atual:
            resultado[j + 1] = resultado[j]
            j -= 1

        resultado[j + 1] = atual

    return resultado
