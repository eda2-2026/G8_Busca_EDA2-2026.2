import json

def carregar_dados(caminho="data/processed/artistas.json"):
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)

def busca_sequencial(artistas, termo):
    termo = termo.lower()
    resultados = []
    for a in artistas:
        if termo in a["nome"].lower() or termo in [g.lower() for g in a["generos"]]:
            resultados.append(a)
    return resultados

def construir_indice(artistas):
    indice = {}
    for a in artistas:
        chaves = [a["nome"].lower()] + [g.lower() for g in a["generos"]]
        for chave in chaves:
            indice.setdefault(chave, []).append(a["id"])
    return sorted(indice.items())

def busca_binaria(indice_ordenado, termo):
    termo = termo.lower()
    inicio, fim = 0, len(indice_ordenado) - 1
    while inicio <= fim:
        meio = (inicio + fim) // 2
        chave_meio = indice_ordenado[meio][0]
        if chave_meio == termo:
            return indice_ordenado[meio][1]
        elif chave_meio < termo:
            inicio = meio + 1
        else:
            fim = meio - 1
    return []

def ids_para_artistas(ids, artistas):
    mapa = {a["id"]: a for a in artistas}
    return [mapa[i] for i in ids if i in mapa]