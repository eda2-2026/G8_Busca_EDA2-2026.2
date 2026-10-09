# Resumo do benchmark T2 — Insertion Sort × Merge Sort

Gerado a partir de `resultados_t2.csv`. Revisão do código: `c8b94693cd064993d8028e48ffa7841506ce7f98` (árvore limpa). Dataset SHA-256: `3af823fd32faf392d7cda1771937c829bb0de3e98179266ce0beaa4679f89825`.
Repetições por algoritmo e caso: 10. Tempos em milissegundos: mediana e IQR (Q3 − Q1, quartis inclusivos).

> consulta_real-35: apenas 1 chave(s) distinta(s); com tantos empates, o cenário inverso não representa o pior caso do Insertion

> consulta_real-35-quase_ordenado: 0 de 1 trocas efetivas (não há pares de chaves diferentes suficientes)

> catalogo_real-100: apenas 2 chave(s) distinta(s); com tantos empates, o cenário inverso não representa o pior caso do Insertion

> catalogo_real-300: apenas 2 chave(s) distinta(s); com tantos empates, o cenário inverso não representa o pior caso do Insertion

> catalogo_real-553: apenas 2 chave(s) distinta(s); com tantos empates, o cenário inverso não representa o pior caso do Insertion

| Origem | n | Cenário | Chaves distintas | insertion mediana | insertion IQR | merge mediana | merge IQR |
|---|---|---|---|---:|---:|---:|---:|
| consulta_real | 35 | aleatorio | 1 | 0.01027 | 0.005622 | 0.05944 | 0.03826 |
| consulta_real | 35 | ordenado | 1 | 0.005238 | 0.0001222 | 0.03192 | 0.0004533 |
| consulta_real | 35 | inverso | 1 | 0.005308 | 0.0001225 | 0.03192 | 0.0002615 |
| consulta_real | 35 | quase_ordenado | 1 | 0.005308 | 0.0001225 | 0.03195 | 6.975e-05 |
| consulta_real | 35 | todos_iguais | 1 | 0.005274 | 0.000331 | 0.03174 | 0.0004188 |
| catalogo_real | 100 | aleatorio | 2 | 0.01942 | 0.0001925 | 0.09785 | 0.006775 |
| catalogo_real | 100 | ordenado | 2 | 0.0118 | 0.0003318 | 0.09628 | 0.002357 |
| catalogo_real | 100 | inverso | 2 | 0.02965 | 0.0003842 | 0.09729 | 0.0006107 |
| catalogo_real | 100 | quase_ordenado | 2 | 0.01278 | 0.0003493 | 0.09561 | 0.0006817 |
| catalogo_real | 100 | todos_iguais | 1 | 0.01152 | 0.0002792 | 0.09537 | 0.0006112 |
| catalogo_real | 300 | aleatorio | 2 | 0.1525 | 0.001607 | 0.3349 | 0.009621 |
| catalogo_real | 300 | ordenado | 2 | 0.0329 | 0.00028 | 0.3267 | 0.01343 |
| catalogo_real | 300 | inverso | 2 | 0.256 | 0.006495 | 0.3305 | 0.01261 |
| catalogo_real | 300 | quase_ordenado | 2 | 0.05378 | 0.008049 | 0.3286 | 0.001344 |
| catalogo_real | 300 | todos_iguais | 1 | 0.0329 | 0.000751 | 0.322 | 0.009306 |
| catalogo_real | 553 | aleatorio | 2 | 0.6069 | 0.01757 | 0.6637 | 0.01198 |
| catalogo_real | 553 | ordenado | 2 | 0.0653 | 0.0008728 | 0.6435 | 0.01454 |
| catalogo_real | 553 | inverso | 2 | 1.362 | 0.006233 | 0.6571 | 0.01365 |
| catalogo_real | 553 | quase_ordenado | 2 | 0.1387 | 0.001152 | 0.6459 | 0.01571 |
| catalogo_real | 553 | todos_iguais | 1 | 0.06572 | 0.001136 | 0.6393 | 0.01479 |
| sintetico_poucas_chaves | 100 | aleatorio | 66 | 0.1679 | 0.008504 | 0.135 | 0.001327 |
| sintetico_poucas_chaves | 100 | ordenado | 66 | 0.0124 | 0.0001225 | 0.0976 | 0.0005758 |
| sintetico_poucas_chaves | 100 | inverso | 66 | 0.3233 | 0.000646 | 0.1092 | 0.007158 |
| sintetico_poucas_chaves | 100 | quase_ordenado | 66 | 0.01753 | 0.0007515 | 0.1027 | 0.0007337 |
| sintetico_poucas_chaves | 100 | todos_iguais | 1 | 0.01173 | 0.0002615 | 0.09656 | 0.004103 |
| sintetico_poucas_chaves | 500 | aleatorio | 100 | 4.653 | 0.0197 | 0.812 | 0.01123 |
| sintetico_poucas_chaves | 500 | ordenado | 100 | 0.06247 | 0.0003845 | 0.5872 | 0.01535 |
| sintetico_poucas_chaves | 500 | inverso | 100 | 8.909 | 0.03667 | 0.641 | 0.01144 |
| sintetico_poucas_chaves | 500 | quase_ordenado | 100 | 0.1393 | 0.000384 | 0.6441 | 0.00571 |
| sintetico_poucas_chaves | 500 | todos_iguais | 1 | 0.05916 | 0.001397 | 0.5754 | 0.01308 |
| sintetico_poucas_chaves | 2000 | aleatorio | 101 | 82.6 | 3.314 | 3.944 | 0.05418 |
| sintetico_poucas_chaves | 2000 | ordenado | 101 | 0.2711 | 0.01103 | 2.657 | 0.01528 |
| sintetico_poucas_chaves | 2000 | inverso | 101 | 163.4 | 4.625 | 2.93 | 0.07653 |
| sintetico_poucas_chaves | 2000 | quase_ordenado | 101 | 2.83 | 0.02334 | 3.252 | 0.01676 |
| sintetico_poucas_chaves | 2000 | todos_iguais | 1 | 0.2536 | 0.009324 | 2.589 | 0.01072 |
| sintetico_faixa_ampla | 100 | aleatorio | 100 | 0.1828 | 0.000558 | 0.1326 | 0.0008732 |
| sintetico_faixa_ampla | 100 | ordenado | 100 | 0.01226 | 0.0004367 | 0.0968 | 0.0003843 |
| sintetico_faixa_ampla | 100 | inverso | 100 | 0.3398 | 0.1274 | 0.1086 | 0.02252 |
| sintetico_faixa_ampla | 100 | quase_ordenado | 100 | 0.01847 | 0.0003835 | 0.1081 | 0.003335 |
| sintetico_faixa_ampla | 100 | todos_iguais | 1 | 0.01191 | 0.0001918 | 0.09593 | 0.001275 |
| sintetico_faixa_ampla | 500 | aleatorio | 500 | 4.455 | 0.03193 | 0.8013 | 0.006897 |
| sintetico_faixa_ampla | 500 | ordenado | 500 | 0.0608 | 0.0011 | 0.5816 | 0.008137 |
| sintetico_faixa_ampla | 500 | inverso | 500 | 8.934 | 0.0322 | 0.597 | 0.01542 |
| sintetico_faixa_ampla | 500 | quase_ordenado | 500 | 0.1744 | 0.007647 | 0.6526 | 0.007665 |
| sintetico_faixa_ampla | 500 | todos_iguais | 1 | 0.05916 | 0.0004365 | 0.5726 | 0.008801 |
| sintetico_faixa_ampla | 2000 | aleatorio | 1997 | 84.24 | 4.377 | 3.956 | 0.02933 |
| sintetico_faixa_ampla | 2000 | ordenado | 1997 | 0.2727 | 0.0125 | 2.67 | 0.0154 |
| sintetico_faixa_ampla | 2000 | inverso | 1997 | 166.2 | 2.707 | 2.744 | 0.03911 |
| sintetico_faixa_ampla | 2000 | quase_ordenado | 1997 | 3.002 | 0.02832 | 3.233 | 0.3789 |
| sintetico_faixa_ampla | 2000 | todos_iguais | 1 | 0.2645 | 0.01243 | 2.599 | 0.01067 |
