# Relatório T2: ordenação dos resultados por relevância

**Projeto:** Motor de Busca Musical (EDA2 2026-2)
**Etapa:** T2, Algoritmos de Ordenação
**Dupla:** Felipe Matheus Ribeiro Lopes e Pedro Araujo Lucena

## 1. Objetivo

No T1 o motor responde **quais artistas correspondem à consulta**. O T2 acrescenta **em que ordem esses artistas devem aparecer**. Cada artista encontrado recebe um score de relevância, e a lista é ordenada por esse score com um de dois algoritmos implementados pela dupla: **Insertion Sort** e **Merge Sort**. Também comparamos os dois algoritmos experimentalmente.

```text
JSON do T1 → busca sequencial ou binária (T1) → artistas encontrados
           → score de relevância → Insertion Sort ou Merge Sort
           → resultados mais relevantes primeiro
```

## 2. Base reaproveitada

- **Dados:** `data/processed/artistas.json`, com 553 artistas coletados da API do MusicBrainz no T1, priorizando artistas brasileiros (`country:BR`). São 553 IDs distintos.
- **Buscas:** `busca_sequencial` (substring no nome ou gênero exato) e `busca_binaria` sobre o índice ordenado de `construir_indice`, ambas em `src/search/busca.py`.
- **Campos usados no T2:** `id`, `nome` e `generos`. Na base atual, `ouvintes` é nulo em todos os artistas e `tags_lastfm` está vazio em todos, por isso não usamos popularidade no score. 103 artistas não têm ano de formação, mas nenhum é descartado por isso.
- **Integridade do dataset:** o JSON não é alterado. O score depende da consulta e é calculado na hora. O SHA-256 do arquivo medido está registrado em `benchmarks/ambiente_t2.json`.

## 3. Ranking

Implementado por Pedro em `src/ranking/relevancia.py`. O termo e os campos passam por `strip().lower()`, e acentos continuam significativos.

| Condição | Pontos |
|---|---:|
| Consulta igual ao nome | 60 |
| Senão, consulta contida no nome | 30 |
| Consulta igual a algum gênero | +40, uma única vez |
| Consulta vazia | 0 para todos |

Exemplo **fictício** com a consulta `rock`:

| ID | Nome | Gêneros | Score |
|---|---|---|---:|
| a | Rock | rock | 100 |
| b | Rock Trio | rock | 70 |
| c | Rock | jazz | 60 |
| d | Queen | rock | 40 |
| e | Rock Ensemble | jazz | 30 |
| f | Samba Trio | samba | 0 |

Cada resultado vira `{"artista": ..., "score": s, "chave": -s}`. Ordenar a `chave` em ordem crescente coloca os maiores scores primeiro. Nunca invertemos a lista inteira no final, porque isso inverteria também a ordem dos empates.

**Limitação importante:** só existem seis scores possíveis (0, 30, 40, 60, 70 e 100), então empates são a regra. Na base real, nenhum nome de artista contém `rock`. Os 35 artistas encontrados por `rock` recebem todos 40 pontos, por gênero exato. O mesmo se repete em outras consultas: `mpb` encontra 85 artistas, todos com 40 pontos, e `samba` encontra 51, sendo 50 com 40 pontos e 1 com 70. É por isso que os dois algoritmos precisam ser **estáveis**: entre artistas empatados, vale a ordem em que a busca os devolveu.

## 4. Algoritmos

Os dois seguem o mesmo contrato: `algoritmo(itens, key)` devolve uma **nova lista** em ordem crescente de `key`, não altera a lista de entrada nem os registros, é estável e não usa `sorted`/`.sort()`. Esta última regra é verificada por `tests/test_ordenacao.py`.

### Insertion Sort (Pedro, `src/sort/insertion.py`)

A cada passo, o trecho à esquerda já está ordenado. O próximo item é guardado, os itens com chave **estritamente maior** são deslocados uma posição para a direita, e o item entra no espaço aberto. Como o deslocamento só acontece com `>`, um item nunca passa à frente de outro de mesma chave, e isso garante a estabilidade.

### Merge Sort (Felipe, `src/sort/merge.py`)

A lista é dividida ao meio, cada metade é ordenada recursivamente e as duas são intercaladas com dois índices. No empate (`<=`), o item da metade **esquerda** sai primeiro. Isso garante a estabilidade, porque a metade esquerda contém os itens que vinham antes na entrada. Na intercalação usamos `append` e `extend`, nunca `pop(0)`, que deslocaria a lista a cada remoção.

### Complexidade

| Aspecto | Insertion Sort | Merge Sort |
|---|---|---|
| Melhor caso | O(n), lista já ordenada ou só com empates | O(n log n) |
| Caso médio e pior caso | O(n²) | O(n log n) |
| Estável | Sim (`>` estrito) | Sim (`<=` prioriza a esquerda) |
| Espaço extra do núcleo | O(1) | O(n) para intercalar, mais a pilha O(log n) |
| Espaço na interface do projeto | O(n), pela cópia da entrada | O(n), mais as fatias e a pilha O(log n) |

Aqui `n` é a quantidade de itens ordenados, não o tamanho do catálogo. Uma busca que encontra 35 artistas ordena 35 itens. Os dois algoritmos copiam a lista (cópia superficial: os registros continuam sendo os mesmos objetos) e só movem referências.

## 5. Integração

O fluxo previsto é busca → score → ordenação → limite de apresentação. O limite só é aplicado depois de ordenar, e o dataset nunca é alterado. A integração com as buscas do T1 (`src/servico.py`, adaptador `src/sort/api.py`) e a CLI com escolha de busca e algoritmo (`main.py`) são as etapas A4–A5, a cargo de Pedro. Os testes de `tests/test_ordenacao.py` já cobrem o adaptador e passam a rodar automaticamente quando `src/sort/api.py` for integrado. Até lá, ficam marcados como *skipped*.

As buscas sequencial e binária não são equivalentes: a sequencial aceita substring no nome, e a binária procura a chave completa no índice. A comparação entre Insertion e Merge sempre usa **a mesma lista**, produzida por uma única busca.

## 6. Metodologia

Script: `benchmarks/benchmark_ordenacao.py` (Felipe). Comando da coleta final:

```bash
python -m benchmarks.benchmark_ordenacao --dados data/processed/artistas.json --termo rock --repeticoes 10 --tamanhos-sinteticos 100 500 2000 --semente 42 --saida benchmarks/resultados_t2.csv
```

**Origens das entradas**

| Origem | Entrada | Para quê |
|---|---|---|
| `consulta_real` | Busca sequencial por `rock`, deduplicada por ID e pontuada (35 itens) | Uso real do motor |
| `catalogo_real` | Os primeiros 100, 300 e 553 artistas do JSON, pontuados para `rock`, sem filtrar | Tamanhos maiores com dados reais |
| `sintetico_poucas_chaves` | 100, 500 e 2000 registros artificiais com chaves inteiras de −100 a 0 | Muitos empates em escala maior |
| `sintetico_faixa_ampla` | 100, 500 e 2000 registros artificiais com chaves de 0 a 1.000.000 | Chaves quase todas distintas |

O catálogo usa **prefixos** do JSON, não uma amostra estatisticamente representativa, e inclui artistas com score 0. Os registros sintéticos são dados de teste, não artistas coletados.

**Cenários (ordem inicial), iguais para os dois algoritmos:** `aleatorio` (embaralhado), `ordenado` (chaves crescentes), `inverso` (chaves decrescentes), `quase_ordenado` (crescente com `max(1, n // 100)` trocas de pares de chaves diferentes) e `todos_iguais` (cópia com chave 0 para todos, uma transformação experimental). Cada caso usa uma semente própria, derivada por SHA-256 da semente base 42 e do identificador do caso, e registrada no CSV.

**Medição**

- Cada entrada é preparada uma única vez e congelada. Os dois algoritmos recebem exatamente a mesma lista em todas as repetições.
- Há 1 execução de validação e aquecimento por algoritmo e caso, descartada. Depois vêm **10 repetições medidas**. Nas repetições ímpares o Merge roda primeiro, nas pares o Insertion.
- O cronômetro (`time.perf_counter_ns()`) envolve **somente** a chamada do algoritmo. Isso inclui a cópia interna, as comparações, os deslocamentos ou intercalações e as alocações. Ficam de fora a leitura do JSON, a busca, o score, a preparação dos cenários, a validação e a escrita dos arquivos.
- Depois de cada execução, fora do cronômetro, a saída é comparada item a item (por identidade) com a ordenação estável de referência. Também verificamos que a lista de entrada não mudou. Qualquer divergência interrompe a coleta.
- O resumo usa mediana e IQR (Q3 − Q1, `statistics.quantiles(..., method="inclusive")`).
- São 10 grupos de origem e tamanho × 5 cenários × 2 algoritmos × 10 repetições, ou seja, **1000 medições**.

**Ambiente** (copiado de `benchmarks/ambiente_t2.json`): CPython 3.14.6, Linux 6.19.14 (Fedora 43), AMD Ryzen 5 5500U, código na revisão `c8b94693cd064993d8028e48ffa7841506ce7f98` (árvore limpa). A memória **não** foi medida: a discussão sobre espaço é teórica.

**Arquivos gerados:** `resultados_t2.csv` (uma linha por medição), `ambiente_t2.json`, `entradas_t2.json` (IDs e chaves de cada caso, na ordem medida) e `resumo_t2.md`. Um ensaio com outro nome de saída, como `/tmp/ensaio_t2.csv`, gera `/tmp/ensaio_t2_ambiente.json` e os demais ao lado, sem sobrescrever os resultados finais.

## 7. Resultados

Tabelas copiadas de `benchmarks/resumo_t2.md`. Tempos em **milissegundos**: mediana e IQR de 10 repetições.

### Cenário aleatório, todas as origens

| Origem | n | Cenário | Chaves distintas | insertion mediana | insertion IQR | merge mediana | merge IQR |
|---|---|---|---|---:|---:|---:|---:|
| consulta_real | 35 | aleatorio | 1 | 0.01027 | 0.005622 | 0.05944 | 0.03826 |
| catalogo_real | 100 | aleatorio | 2 | 0.01942 | 0.0001925 | 0.09785 | 0.006775 |
| catalogo_real | 300 | aleatorio | 2 | 0.1525 | 0.001607 | 0.3349 | 0.009621 |
| catalogo_real | 553 | aleatorio | 2 | 0.6069 | 0.01757 | 0.6637 | 0.01198 |
| sintetico_poucas_chaves | 100 | aleatorio | 66 | 0.1679 | 0.008504 | 0.135 | 0.001327 |
| sintetico_poucas_chaves | 500 | aleatorio | 100 | 4.653 | 0.0197 | 0.812 | 0.01123 |
| sintetico_poucas_chaves | 2000 | aleatorio | 101 | 82.6 | 3.314 | 3.944 | 0.05418 |
| sintetico_faixa_ampla | 100 | aleatorio | 100 | 0.1828 | 0.000558 | 0.1326 | 0.0008732 |
| sintetico_faixa_ampla | 500 | aleatorio | 500 | 4.455 | 0.03193 | 0.8013 | 0.006897 |
| sintetico_faixa_ampla | 2000 | aleatorio | 1997 | 84.24 | 4.377 | 3.956 | 0.02933 |

### Todos os cenários: catálogo real completo e maiores sintéticos

| Origem | n | Cenário | Chaves distintas | insertion mediana | insertion IQR | merge mediana | merge IQR |
|---|---|---|---|---:|---:|---:|---:|
| catalogo_real | 553 | aleatorio | 2 | 0.6069 | 0.01757 | 0.6637 | 0.01198 |
| catalogo_real | 553 | ordenado | 2 | 0.0653 | 0.0008728 | 0.6435 | 0.01454 |
| catalogo_real | 553 | inverso | 2 | 1.362 | 0.006233 | 0.6571 | 0.01365 |
| catalogo_real | 553 | quase_ordenado | 2 | 0.1387 | 0.001152 | 0.6459 | 0.01571 |
| catalogo_real | 553 | todos_iguais | 1 | 0.06572 | 0.001136 | 0.6393 | 0.01479 |
| sintetico_poucas_chaves | 2000 | aleatorio | 101 | 82.6 | 3.314 | 3.944 | 0.05418 |
| sintetico_poucas_chaves | 2000 | ordenado | 101 | 0.2711 | 0.01103 | 2.657 | 0.01528 |
| sintetico_poucas_chaves | 2000 | inverso | 101 | 163.4 | 4.625 | 2.93 | 0.07653 |
| sintetico_poucas_chaves | 2000 | quase_ordenado | 101 | 2.83 | 0.02334 | 3.252 | 0.01676 |
| sintetico_poucas_chaves | 2000 | todos_iguais | 1 | 0.2536 | 0.009324 | 2.589 | 0.01072 |
| sintetico_faixa_ampla | 2000 | aleatorio | 1997 | 84.24 | 4.377 | 3.956 | 0.02933 |
| sintetico_faixa_ampla | 2000 | ordenado | 1997 | 0.2727 | 0.0125 | 2.67 | 0.0154 |
| sintetico_faixa_ampla | 2000 | inverso | 1997 | 166.2 | 2.707 | 2.744 | 0.03911 |
| sintetico_faixa_ampla | 2000 | quase_ordenado | 1997 | 3.002 | 0.02832 | 3.233 | 0.3789 |
| sintetico_faixa_ampla | 2000 | todos_iguais | 1 | 0.2645 | 0.01243 | 2.599 | 0.01067 |

### Consulta real (`rock`, 35 itens)

| Origem | n | Cenário | Chaves distintas | insertion mediana | insertion IQR | merge mediana | merge IQR |
|---|---|---|---|---:|---:|---:|---:|
| consulta_real | 35 | aleatorio | 1 | 0.01027 | 0.005622 | 0.05944 | 0.03826 |
| consulta_real | 35 | ordenado | 1 | 0.005238 | 0.0001222 | 0.03192 | 0.0004533 |
| consulta_real | 35 | inverso | 1 | 0.005308 | 0.0001225 | 0.03192 | 0.0002615 |
| consulta_real | 35 | quase_ordenado | 1 | 0.005308 | 0.0001225 | 0.03195 | 6.975e-05 |
| consulta_real | 35 | todos_iguais | 1 | 0.005274 | 0.000331 | 0.03174 | 0.0004188 |

A tabela completa, com os 50 casos, está em `benchmarks/resumo_t2.md`, e as 1000 medições individuais estão em `benchmarks/resultados_t2.csv`.

## 8. Discussão

**Em que tamanho o Merge passou a ser mais rápido?** Com chaves variadas (sintéticos) e ordem aleatória, o Merge já foi mais rápido em n = 100 (0,135 ms contra 0,1679 ms com poucas chaves, e 0,1326 contra 0,1828 com faixa ampla). A diferença cresce rápido: cerca de 5,6× em n = 500 (4,455 contra 0,8013 ms) e cerca de 21× em n = 2000 (84,24 contra 3,956 ms). Nos dados reais o quadro é outro. Mesmo com o catálogo inteiro (n = 553) em ordem aleatória, o Insertion ficou à frente (0,6069 contra 0,6637 ms), porque só há duas chaves distintas (0 e −40) e o número de inversões é pequeno.

**O Insertion foi competitivo no resultado real pequeno ou na entrada ordenada?** Sim, e com folga. Na consulta real (35 itens, todos empatados) ele levou cerca de 0,005 ms, contra cerca de 0,032 ms do Merge. Com todas as chaves iguais, ele não desloca nada e faz uma única passada, que é o melhor caso O(n). Na entrada já ordenada ele vence em todas as origens: em n = 2000, 0,2727 ms contra 2,67 ms do Merge. Em `quase_ordenado` com n = 2000, os dois ficaram próximos (3,002 contra 3,233 ms, faixa ampla). A diferença é pequena perto do IQR do Merge nesse caso (0,3789), então não tiramos conclusão forte.

**O cenário inverso prejudicou o Insertion como esperado?** Sim, nos sintéticos: em n = 2000 ele levou 166,2 ms, cerca de o dobro do aleatório (84,24 ms). Isso é coerente com o inverso ter cerca de n²/2 inversões e o aleatório cerca de n²/4. O Merge variou bem menos entre os cenários (de 2,599 a 3,956 ms na faixa ampla com n = 2000). No catálogo real o "inverso" é só uma descida (518 chaves 0 seguidas de 35 chaves −40). Ele custou ao Insertion 1,362 ms, contra 0,6069 no aleatório, mas **não é o pior caso** do algoritmo. O próprio `resumo_t2.md` traz esse alerta.

**Os empates mudaram a diferença entre os algoritmos?** Com muitos empates, o Insertion faz menos deslocamentos, porque empate não é inversão. Nos sintéticos com 2000 itens em ordem aleatória, porém, poucas chaves (82,6 ms) e faixa ampla (84,24 ms) ficaram dentro da variação observada (IQR de 3,3 a 4,4 ms). Os empates fazem diferença de verdade nos dados reais, onde quase tudo é empate: ali o Insertion se aproxima do melhor caso. Para o Merge, empates não mudam o trabalho: ele divide e intercala da mesma forma.

**Crescimento:** ao passar de n = 500 para 2000 (4×), no cenário aleatório com faixa ampla, o Insertion foi de 4,455 para 84,24 ms (cerca de 19×; o modelo n² prevê 16×). O Merge foi de 0,8013 para 3,956 ms (cerca de 4,9×; o modelo n log n prevê cerca de 4,9×). São só três tamanhos, então isso é coerente com a teoria, mas não prova as complexidades.

**O custo extra de memória do Merge se justifica?** Nos tamanhos reais desta aplicação, de dezenas a algumas centenas de resultados, o espaço O(n) a mais é desprezível. O que pesa é o tempo. Para consultas reais, com listas pequenas e muito empatadas, o Insertion foi mais rápido, mas as diferenças ficaram em centésimos de milissegundo, imperceptíveis para quem usa a CLI. O Merge garante O(n log n) em qualquer ordem e com qualquer distribuição de scores, o que importa se o catálogo crescer ou se o score ganhar mais níveis (por exemplo, com ouvintes do Last.fm). Por isso o Merge continua sendo uma escolha padrão razoável. O Insertion também é uma opção defensável para os dados de hoje.

**Limitações**

- Há uma única máquina e um único interpretador (CPython 3.14). Os tempos absolutos não se generalizam.
- Medições com n = 35 são chamadas únicas de 5 a 60 µs, sensíveis a ruído. O caso `consulta_real` aleatório, o primeiro a ser medido, tem IQR bem maior que os demais.
- O catálogo usa prefixos do JSON, e o ranking real tem poucos scores. Os sintéticos ampliam a análise, mas não são artistas reais.
- O cronômetro inclui a cópia da entrada e as fatias do Merge, que fazem parte da implementação medida.
- A memória não foi medida.

## 9. Divisão e reprodução

| Felipe Matheus Ribeiro Lopes | Pedro Araujo Lucena |
|---|---|
| Merge Sort (`src/sort/merge.py`, `tests/test_merge.py`) | Ranking (`src/ranking/relevancia.py`, `tests/test_ranking.py`) |
| Testes cruzados dos dois algoritmos (`tests/test_ordenacao.py`) | Insertion Sort (`src/sort/insertion.py`, `tests/test_insertion.py`) |
| Benchmark (`benchmarks/benchmark_ordenacao.py`, `tests/test_benchmark_ordenacao.py`) | Integração com as buscas e CLI (`src/servico.py`, `src/sort/api.py`, `main.py`) |
| Coleta e resultados (`benchmarks/*_t2.*`), este relatório e o roteiro do vídeo | README e revisão deste relatório |

Para reproduzir, a partir da raiz do repositório e com o venv ativo:

```bash
python -m unittest discover -s tests -v
python -m benchmarks.benchmark_ordenacao --repeticoes 2 --tamanhos-sinteticos 100 --saida /tmp/ensaio_t2.csv   # ensaio rápido
python -m benchmarks.benchmark_ordenacao --dados data/processed/artistas.json --termo rock --repeticoes 10 --tamanhos-sinteticos 100 500 2000 --semente 42 --saida benchmarks/resultados_t2.csv
```

Os tempos variam de máquina para máquina. Já as entradas (`entradas_t2.json`), as sementes e o hash do dataset permitem reconstruir exatamente os mesmos casos.

## 10. Próximas etapas

- **T3 (Árvores):** o índice ordenado da busca binária pode virar uma árvore (BST, AVL ou Trie), o que permitiria busca por prefixo e inserção sem reordenar tudo.
- **T4 (Grafos):** artistas ligados por gêneros em comum formam um grafo, que pode servir para recomendação.
- Os registros, o score e o módulo de ordenação continuam reaproveitáveis nas duas etapas. Nada disso está implementado no T2.
