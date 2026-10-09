def pontuar_artista(artista, termo):
    termo = termo.strip().lower()

    if not termo:
        return 0

    nome = artista["nome"].strip().lower()

    if nome == termo:
        pontos = 60
    elif termo in nome:
        pontos = 30
    else:
        pontos = 0

    generos = {
        genero.strip().lower()
        for genero in artista["generos"]
    }

    if termo in generos:
        pontos += 40

    return pontos


def preparar_resultados(artistas, termo):
    resultados = []

    for artista in artistas:
        score = pontuar_artista(artista, termo)

        resultados.append({
            "artista": artista,
            "score": score,
            "chave": -score,
        })

    return resultados
