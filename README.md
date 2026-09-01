# Motor de Busca Musical — EDA2 2026-2

Projeto integrado da disciplina Estrutura de Dados 2 (EDA2), desenvolvido ao longo do semestre em 4 entregas, cada uma introduzindo uma nova estrutura de dados sobre a mesma base de dados musical.

## O que o projeto faz

Um sistema de busca e indexação de artistas/bandas, com dados coletados via APIs musicais (MusicBrainz e Last.fm). A cada entrega, o sistema evolui:

| Entrega | Tema | Data | O que adiciona |
|---|---|---|---|
| T1 | Busca | 31/08 | Busca sequencial vs. busca binária sobre índice ordenado |
| T2 | Ordenação | 12/10 | Ranqueamento de resultados por relevância |
| T3 | Árvores | 16/11 | Índice reestruturado como árvore (BST/AVL/Trie) |
| T4 | Grafos | 07/12 | Grafo de artistas conectados por gênero em comum |

## Links dos vídeos de entrega

T1 (Busca): https://youtu.be/cE65mJbQSSs

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
│   ├── sort/          # algoritmos de ordenação (T2)
│   ├── tree/          # estrutura de árvore (T3)
│   └── graph/         # grafo de artistas (T4)
├── benchmarks/        # scripts e resultados de comparação de desempenho
└── docs/              # relatórios e decisões de cada entrega
```

## Como rodar

```bash
pip install -r requirements.txt
python src/collect/musicbrainz.py   # testa a coleta de dados
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

## Integrantes

- [Felipe Matheus Ribeiro Lopes]
- [Pedro Araujo Lucena]
