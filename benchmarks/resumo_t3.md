# Resumo do benchmark T3 — lista ordenada × BST × AVL × Trie

Gerado a partir de `resultados_t3.csv`. Revisão do código: `5d5bfb17a1b1cfaf72fe5cd7d91ba1fd33e4cc61` (árvore limpa). Dataset SHA-256: `3af823fd32faf392d7cda1771937c829bb0de3e98179266ce0beaa4679f89825`.
Repetições por estrutura e caso: 10 (mais 1 aquecimento descartado). Valores: mediana e, entre parênteses, IQR (Q3 − Q1, quartis inclusivos). `n` = número de chaves distintas. — = estrutura não medida no caso.

> sintetico-20000-ordenado: BST fora do caso (n > 5000 com chaves em ordem degenera a árvore em lista; inserção O(n) por chave)

> sintetico-20000-quase_ordenado: BST fora do caso (n > 5000 com chaves em ordem degenera a árvore em lista; inserção O(n) por chave)

## Construção do índice (ms)

| Origem | n | Cenário | lista_ordenada | bst | avl | trie |
|---|---|---|---:|---:|---:|---:|
| real | 979 | original | 0.4693 (0.009918) | 1.953 (0.491) | 6.697 (0.1972) | 5.911 (1.208) |
| real | 979 | aleatorio | 0.5499 (0.06378) | 1.808 (0.3113) | 6.307 (1.325) | 8.415 (1.724) |
| real | 979 | ordenado | 0.3093 (0.019) | 54.23 (1.934) | 7.47 (1.449) | 6.66 (1.404) |
| sintetico | 1000 | aleatorio | 0.3859 (0.02628) | 0.9122 (0.1088) | 3.349 (0.1499) | 4.771 (0.6229) |
| sintetico | 1000 | ordenado | 0.2099 (0.01268) | 22.89 (1.254) | 3.493 (0.2038) | 4.408 (2.26) |
| sintetico | 1000 | quase_ordenado | 0.2796 (0.05943) | 16.91 (0.5759) | 3.482 (0.108) | 4.442 (3.276) |
| sintetico | 5000 | aleatorio | 2.749 (0.8277) | 6.284 (1.646) | 22.52 (1.336) | 36.32 (36.8) |
| sintetico | 5000 | ordenado | 1.588 (0.8111) | 564.3 (19.93) | 22.03 (1.758) | 37.95 (26.42) |
| sintetico | 5000 | quase_ordenado | 1.61 (1.173) | 451.1 (17.09) | 22.26 (1.376) | 20.48 (4.985) |
| sintetico | 20000 | aleatorio | 26.52 (6.796) | 49.63 (32.83) | 130.9 (38.9) | 326.8 (87.02) |
| sintetico | 20000 | ordenado | 11.12 (2.894) | — | 109.3 (11.84) | 226.1 (64.36) |
| sintetico | 20000 | quase_ordenado | 11.84 (4.927) | — | 105.5 (9.982) | 191.4 (76.11) |

## Busca exata (µs por busca)

| Origem | n | Cenário | lista_ordenada | bst | avl | trie |
|---|---|---|---:|---:|---:|---:|
| real | 979 | original | 1.278 (0.1354) | 0.8611 (0.03632) | 0.6378 (0.03824) | 0.7731 (0.2839) |
| real | 979 | aleatorio | 1.268 (0.1069) | 0.7223 (0.03719) | 0.6672 (0.1642) | 0.8737 (0.3362) |
| real | 979 | ordenado | 1.262 (0.06591) | 24.04 (2.65) | 0.7751 (0.3397) | 1.007 (0.3466) |
| sintetico | 1000 | aleatorio | 1.248 (0.1364) | 0.7084 (0.118) | 0.6848 (0.05465) | 0.6507 (0.2136) |
| sintetico | 1000 | ordenado | 1.186 (0.06207) | 22.27 (0.3438) | 0.6317 (0.3314) | 0.5675 (0.2223) |
| sintetico | 1000 | quase_ordenado | 1.16 (0.04287) | 16.66 (0.2215) | 0.6141 (0.07709) | 0.5779 (0.162) |
| sintetico | 5000 | aleatorio | 1.542 (0.04479) | 1.28 (0.08215) | 2.052 (0.9076) | 1.057 (0.1765) |
| sintetico | 5000 | ordenado | 1.571 (0.132) | 116 (7.494) | 1.432 (0.8597) | 1.178 (0.319) |
| sintetico | 5000 | quase_ordenado | 1.538 (0.03911) | 91.21 (4.645) | 1.447 (0.4851) | 1.152 (0.1791) |
| sintetico | 20000 | aleatorio | 2.718 (0.8149) | 2.873 (0.9597) | 2.928 (1.611) | 1.347 (0.3297) |
| sintetico | 20000 | ordenado | 2.192 (0.4076) | — | 2.484 (0.9855) | 1.442 (0.04872) |
| sintetico | 20000 | quase_ordenado | 2.167 (0.197) | — | 2.294 (0.4001) | 1.408 (0.06653) |

## Altura

| Origem | n | Cenário | bst | avl | trie |
|---|---|---|---:|---:|---:|
| real | 979 | original | 39 | 12 | 33 |
| real | 979 | aleatorio | 20 | 12 | 33 |
| real | 979 | ordenado | 979 | 10 | 33 |
| sintetico | 1000 | aleatorio | 22 | 12 | 13 |
| sintetico | 1000 | ordenado | 1000 | 10 | 13 |
| sintetico | 1000 | quase_ordenado | 746 | 11 | 13 |
| sintetico | 5000 | aleatorio | 30 | 15 | 13 |
| sintetico | 5000 | ordenado | 5000 | 13 | 13 |
| sintetico | 5000 | quase_ordenado | 3889 | 13 | 13 |
| sintetico | 20000 | aleatorio | 33 | 17 | 13 |
| sintetico | 20000 | ordenado | — | 15 | 13 |
| sintetico | 20000 | quase_ordenado | — | 15 | 13 |

## Busca por prefixo (µs por busca)

| Origem | n | Cenário | Prefixo | trie | varredura |
|---|---|---|---|---:|---:|
| real | 979 | original | p1 | 120.5 (12.19) | 47.23 (5.902) |
| real | 979 | original | p2 | 19.02 (3.086) | 30.59 (2.043) |
| real | 979 | original | p3 | 8.907 (1.504) | 29.24 (0.9085) |
| real | 979 | aleatorio | p1 | 134.1 (9.775) | 46.06 (6.687) |
| real | 979 | aleatorio | p2 | 20.54 (6.44) | 36.4 (3.678) |
| real | 979 | aleatorio | p3 | 11.59 (3.936) | 34.84 (8.44) |
| real | 979 | ordenado | p1 | 127.8 (13.03) | 44.5 (3.676) |
| real | 979 | ordenado | p2 | 18.26 (6.131) | 30.84 (2.525) |
| real | 979 | ordenado | p3 | 9.934 (2.857) | 28.94 (1.521) |
| sintetico | 1000 | aleatorio | p1 | 78.12 (15.54) | 37.86 (2.548) |
| sintetico | 1000 | aleatorio | p2 | 6.328 (1.075) | 27.3 (0.7782) |
| sintetico | 1000 | aleatorio | p3 | 2.606 (0.7171) | 26.6 (1.959) |
| sintetico | 1000 | ordenado | p1 | 67.11 (15) | 33.72 (3.412) |
| sintetico | 1000 | ordenado | p2 | 5.717 (1.603) | 26.98 (2.684) |
| sintetico | 1000 | ordenado | p3 | 2.653 (1.198) | 26.66 (1.488) |
| sintetico | 1000 | quase_ordenado | p1 | 79.81 (20.4) | 34.54 (2.919) |
| sintetico | 1000 | quase_ordenado | p2 | 5.217 (0.5459) | 26.46 (0.9923) |
| sintetico | 1000 | quase_ordenado | p3 | 2.223 (0.9586) | 27.11 (2.759) |
| sintetico | 5000 | aleatorio | p1 | 339.9 (22.84) | 255.7 (16.93) |
| sintetico | 5000 | aleatorio | p2 | 17.05 (2.165) | 197.4 (15.27) |
| sintetico | 5000 | aleatorio | p3 | 3.959 (0.2474) | 195.7 (0.8946) |
| sintetico | 5000 | ordenado | p1 | 329 (122.3) | 234.9 (117.1) |
| sintetico | 5000 | ordenado | p2 | 15.42 (7.15) | 163.1 (30.04) |
| sintetico | 5000 | ordenado | p3 | 4.441 (1.34) | 165.9 (25.88) |
| sintetico | 5000 | quase_ordenado | p1 | 329.6 (35.31) | 214.8 (67.84) |
| sintetico | 5000 | quase_ordenado | p2 | 17.3 (3.505) | 177.1 (46.91) |
| sintetico | 5000 | quase_ordenado | p3 | 4.726 (0.5395) | 167.7 (52.01) |
| sintetico | 20000 | aleatorio | p1 | 1622 (360.8) | 5180 (1677) |
| sintetico | 20000 | aleatorio | p2 | 59.88 (8.517) | 4054 (2076) |
| sintetico | 20000 | aleatorio | p3 | 6.879 (0.8841) | 3675 (2364) |
| sintetico | 20000 | ordenado | p1 | 1119 (62.81) | 1861 (610.6) |
| sintetico | 20000 | ordenado | p2 | 48.27 (7.042) | 1596 (1376) |
| sintetico | 20000 | ordenado | p3 | 5.978 (0.9725) | 1349 (756) |
| sintetico | 20000 | quase_ordenado | p1 | 1152 (125.4) | 1889 (801.7) |
| sintetico | 20000 | quase_ordenado | p2 | 47 (5.446) | 1400 (408.4) |
| sintetico | 20000 | quase_ordenado | p3 | 5.67 (0.8712) | 1233 (671.6) |
