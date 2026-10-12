# Motor de Busca Musical — EDA2 2026-2

Projeto integrado da disciplina Estrutura de Dados 2 (EDA2), desenvolvido ao longo do semestre em 4 entregas, cada uma introduzindo uma nova estrutura de dados sobre a mesma base de dados musical.

## O que o projeto faz

Um sistema de busca e indexação de artistas/bandas, com dados coletados via APIs musicais (MusicBrainz e Last.fm). A cada entrega, o sistema evolui:

| Entrega | Tema | Data | O que adiciona |
|---|---|---|---|
| T1 | Busca | 31/08 | Busca sequencial vs. busca binária sobre índice ordenado |
| T2 | Ordenação | 12/10 | Ranqueamento de resultados por relevância, com Insertion Sort e Merge Sort |
| T3 | Árvores | 16/11 | Índice reestruturado como árvore (BST/AVL/Trie) |
| T4 | Grafos | 07/12 | Grafo de artistas conectados por gênero em comum |

## Links dos vídeos de entrega

T1 (Busca): https://youtu.be/cE65mJbQSSs

T2 (Ordenação): _a definir após a gravação_

## Fonte de dados

- **MusicBrainz API** — dados principais: nome, país, ano de formação, gêneros
- **Last.fm API** (opcional) — enriquecimento: tags da comunidade, número de ouvintes

## Estrutura do repositório

```
├── data/
│   ├── raw/          # dados brutos coletados das APIs
│   └── processed/    # dados limpos, prontos pra uso
├── src/
│   ├── collect/      # coleta de dados (MusicBrainz, Last.fm, cache)
│   ├── search/        # algoritmos de busca (T1)
│   ├── ranking/       # cálculo de relevância (T2)
│   ├── sort/          # Insertion Sort, Merge Sort e adaptador (T2)
│   ├── servico.py     # busca + ranking + ordenação (T2)
│   ├── tree/          # estrutura de árvore (T3)
│   └── graph/         # grafo de artistas (T4)
├── benchmarks/        # scripts e resultados de comparação de desempenho (T1 e T2)
├── tests/             # testes unitários (unittest)
├── main.py            # CLI do motor de busca
└── docs/              # relatórios e decisões de cada entrega
```

## Como rodar

```bash
pip install -r requirements.txt
python src/collect/musicbrainz.py   # testa a coleta de dados
```

### Busca com ranking (CLI)

```bash
python main.py --termo rock --busca sequencial --algoritmo merge --limite 10
python main.py --termo rock --busca binaria --algoritmo insertion
python main.py --termo "" --limite 5     # sem termo: lista todo o catálogo
```

| Opção | Valores | Padrão |
|---|---|---|
| `--termo` | texto da consulta | vazio |
| `--busca` | `sequencial` ou `binaria` | `sequencial` |
| `--algoritmo` | `insertion` ou `merge` | `merge` |
| `--limite` | inteiro positivo (só limita a exibição, depois de ordenar) | `10` |
| `--dados` | caminho do JSON | `data/processed/artistas.json` |

### Testes e benchmark do T2

```bash
python -m unittest discover -s tests -v

# ensaio rápido (grava fora do repositório)
python -m benchmarks.benchmark_ordenacao --repeticoes 2 --tamanhos-sinteticos 100 --saida /tmp/ensaio_t2.csv

# coleta final (regera benchmarks/*_t2.*)
python -m benchmarks.benchmark_ordenacao --dados data/processed/artistas.json --termo rock --repeticoes 10 --tamanhos-sinteticos 100 500 2000 --semente 42 --saida benchmarks/resultados_t2.csv
```

## 👥 Divisão de Tarefas (T1)

O trabalho foi dividido em duas frentes atuando de forma paralela através do uso de um *mock* temporário, até a integração final dos dados reais:

*   **Felipe Matheus Ribeiro Lopes:** Responsável pela integração com a API do MusicBrainz, script de extração estruturada, montagem do cache local em JSON e limpeza dos dados brutos.
*   **Pedro Araujo Lucena:** Responsável pela lógica de pesquisa, implementando a Busca Sequencial, a construção do Índice Ordenado, a Busca Binária e os scripts parametrizados de Benchmark.

## 📊 Resultados do Benchmark (T1)

Comparamos o tempo de execução da Busca Sequencial ($O(n)$) e da Busca Binária ($O(\log n)$) utilizando o dataset real final coletado da API, que totalizou **553 artistas**. Os testes foram realizados calculando a média de 100 repetições para cada termo.

| Termo Buscado | Busca Sequencial (ms) | Busca Binária (ms) |
|---------------|-----------------------|--------------------|
| `rock`        | 0.8572 ms             | 0.0045 ms          |
| `pop`         | 0.8599 ms             | 0.0042 ms          |
| `termo_inexistente` | 0.6867 ms       | 0.0033 ms          |

**Conclusão:** 
Como esperado pela teoria de complexidade, a Busca Binária se mostrou exponencialmente mais rápida (cerca de 190 a 200 vezes mais rápida) para todos os cenários. Isso confirma a eficiência e a necessidade de se construir um índice ordenado inicial quando o sistema precisará lidar com um volume alto de consultas frequentes.

## 👥 Divisão de Tarefas (T2)

*   **Pedro Araujo Lucena:** ranking por relevância (`src/ranking/`), Insertion Sort estável (`src/sort/insertion.py`), serviço que integra busca, ranking e ordenação (`src/servico.py`, `src/sort/api.py`) e a CLI (`main.py`).
*   **Felipe Matheus Ribeiro Lopes:** Merge Sort estável (`src/sort/merge.py`), testes cruzados dos dois algoritmos, benchmark reproduzível (`benchmarks/benchmark_ordenacao.py`), coleta dos resultados, relatório e roteiro do vídeo.

## 🏆 Ranking de relevância (T2)

Cada artista encontrado recebe uma pontuação: **60** se o nome é igual ao termo, **30** se o nome contém o termo e **+40** se algum gênero contém o termo. A lista é ordenada por pontuação decrescente (a chave de ordenação é `-score`), e os dois algoritmos são **estáveis**: artistas empatados mantêm a ordem em que a busca os devolveu. Como existem só seis pontuações possíveis (0, 30, 40, 60, 70 e 100), há muitos empates.

## 📊 Resultados do Benchmark (T2)

Insertion Sort ($O(n^2)$) × Merge Sort ($O(n \log n)$) em origens reais (consulta `rock` e catálogo de 553 artistas) e sintéticas, em cinco cenários de entrada. Cada caso tem 1 aquecimento descartado e 10 repetições; a tabela mostra a **mediana em ms** no cenário aleatório. Dados completos em `benchmarks/resultados_t2.csv` e `benchmarks/resumo_t2.md`.

| Origem | n | Insertion (ms) | Merge (ms) |
|---|---:|---:|---:|
| consulta real (`rock`) | 35 | 0.01027 | 0.05944 |
| catálogo real | 100 | 0.01942 | 0.09785 |
| catálogo real | 300 | 0.1525 | 0.3349 |
| catálogo real | 553 | 0.6069 | 0.6637 |
| sintético (faixa ampla) | 500 | 4.455 | 0.8013 |
| sintético (faixa ampla) | 2000 | 84.24 | 3.956 |

**Conclusão:** o Insertion Sort vence em listas pequenas, já ordenadas ou quase ordenadas (menos sobrecarga, melhor caso $O(n)$) e em dados com poucas chaves distintas, como o catálogo real, que tem só 2 (n = 553: 0.61 contra 0.66 ms). Com chaves variadas, o Merge Sort já ganha a partir de n = 100 e chega a ser ~21 vezes mais rápido com n = 2000 (84.24 contra 3.956 ms). Para as consultas reais do projeto a diferença absoluta é de décimos de milissegundo, mas o Merge garante $O(n \log n)$ se o catálogo crescer ou o ranking ganhar mais níveis de pontuação. A análise completa, com metodologia e limitações, está em [`docs/relatorio_t2.md`](docs/relatorio_t2.md); o roteiro do vídeo está em [`docs/roteiro_video_t2.md`](docs/roteiro_video_t2.md).

## Integrantes

- [Felipe Matheus Ribeiro Lopes]
- [Pedro Araujo Lucena]
