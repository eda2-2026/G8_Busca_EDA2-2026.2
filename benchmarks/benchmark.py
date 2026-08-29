import time
import sys
import os

# Ajuste de caminho para conseguir importar a pasta src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.search.busca import carregar_dados, busca_sequencial, construir_indice, busca_binaria

def benchmark(artistas, indice, termo, repeticoes=100):
    inicio = time.perf_counter()
    for _ in range(repeticoes):
        busca_sequencial(artistas, termo)
    tempo_sequencial = (time.perf_counter() - inicio) / repeticoes

    inicio = time.perf_counter()
    for _ in range(repeticoes):
        busca_binaria(indice, termo)
    tempo_binaria = (time.perf_counter() - inicio) / repeticoes

    print(f"Sequencial: {tempo_sequencial*1000:.4f} ms")
    print(f"Binária:    {tempo_binaria*1000:.4f} ms")

def rodar_benchmark_completo(caminho_dados, termos_teste):
    artistas = carregar_dados(caminho_dados)
    indice = construir_indice(artistas)
    for termo in termos_teste:
        print(f"\n--- Termo: '{termo}' | Total de artistas: {len(artistas)} ---")
        benchmark(artistas, indice, termo)

if __name__ == "__main__":
    termos = ["rock", "pop", "termo_inexistente"]
    print("Testando Benchmark com o Dataset Real:")
    rodar_benchmark_completo("data/processed/artistas.json", termos)