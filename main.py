import argparse
import json

from src.search.busca import carregar_dados
from src.servico import pesquisar_e_ordenar
from src.sort.api import ALGORITMOS


def inteiro_positivo(valor):
    try:
        numero = int(valor)
    except ValueError:
        raise argparse.ArgumentTypeError("Informe um número inteiro.")

    if numero <= 0:
        raise argparse.ArgumentTypeError("O limite deve ser maior que zero.")

    return numero


def main():
    parser = argparse.ArgumentParser(
        description="Motor de busca musical com ranking por relevância."
    )

    parser.add_argument("--termo", default="")
    parser.add_argument(
        "--busca",
        choices=["sequencial", "binaria"],
        default="sequencial",
    )
    parser.add_argument(
        "--algoritmo",
        choices=list(ALGORITMOS),
        default="merge",
    )
    parser.add_argument("--limite", type=inteiro_positivo, default=10)
    parser.add_argument(
        "--dados",
        default="data/processed/artistas.json",
    )

    args = parser.parse_args()

    try:
        artistas = carregar_dados(args.dados)
    except (OSError, json.JSONDecodeError, UnicodeError) as erro:
        parser.error(f"Não foi possível carregar os dados: {erro}")

    resultados = pesquisar_e_ordenar(
        artistas,
        args.termo,
        busca=args.busca,
        algoritmo=args.algoritmo,
    )

    print(f"Busca: {args.busca} | Ordenação: {args.algoritmo.title()} Sort")
    print(f"Total encontrado: {len(resultados)}")

    if not resultados:
        print("Nenhum artista encontrado.")
        return

    for posicao, resultado in enumerate(
        resultados[:args.limite],
        start=1,
    ):
        artista = resultado["artista"]
        generos = ", ".join(artista["generos"]) or "Não informado"

        print(
            f"{posicao}. {artista['nome']} "
            f"| Score: {resultado['score']} "
            f"| Gêneros: {generos}"
        )


if __name__ == "__main__":
    main()
