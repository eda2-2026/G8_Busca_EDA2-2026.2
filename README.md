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

## Integrantes

- [Felipe Matheus Ribeiro Lopes]
- [Pedro Araujo Lucena]
