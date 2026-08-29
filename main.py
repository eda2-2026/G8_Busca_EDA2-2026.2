from src.search.busca import carregar_dados, busca_sequencial, construir_indice, busca_binaria, ids_para_artistas

# 1. Carrega o dataset real de artistas
artistas = carregar_dados()

# 2. Testa a Busca Sequencial
print("--- BUSCA SEQUENCIAL: 'rock' ---")
resultados_seq = busca_sequencial(artistas, "rock")
for r in resultados_seq:
    print(f"- {r['nome']} (Gêneros: {r['generos']})")

# 3. Testa a Busca Binária
print("\n--- BUSCA BINÁRIA: 'rock' ---")
indice = construir_indice(artistas)
ids_encontrados = busca_binaria(indice, "rock")
resultados_bin = ids_para_artistas(ids_encontrados, artistas)
for r in resultados_bin:
    print(f"- {r['nome']} (Gêneros: {r['generos']})")

# 4. Testa termo inexistente e string vazia
print(f"\nBusca Sequencial por 'kpop': {busca_sequencial(artistas, 'kpop')}")
print(f"Busca Sequencial por string vazia: {len(busca_sequencial(artistas, ''))} encontrados")