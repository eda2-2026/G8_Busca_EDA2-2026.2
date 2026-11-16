# Relatório T3: índice de busca em árvores

**Projeto:** Motor de Busca Musical (EDA2 2026-2)
**Etapa:** T3, Árvores
**Dupla:** Felipe Matheus Ribeiro Lopes e Pedro Araujo Lucena

## 1. Objetivo

No T1 o índice de busca é uma **lista ordenada** de chaves (nome e gêneros), consultada por busca binária. Ela tem dois limites: para inserir uma chave nova é preciso reordenar ou deslocar a lista, e a busca só encontra a chave **completa**. O T3 troca esse índice por árvores:

- **BST** (árvore binária de busca, sem balanceamento) e **AVL** (BST que se rebalanceia com rotações), para busca exata;
- **Trie** (árvore de prefixos), para busca exata e **busca por prefixo**, que o T1 não tinha (`ro` encontra `roberto menescal`, `rock`, `rock alternativo`, `rock gaúcho`...).

As três são comparadas experimentalmente com a lista ordenada do T1.

```text
JSON do T1 → chaves (nome + gêneros) → lista ordenada | BST | AVL | Trie
           → ids dos artistas → score de relevância (T2) → Insertion ou Merge Sort (T2)
```

## 2. Base reaproveitada

- **Dados:** `data/processed/artistas.json` (553 artistas do MusicBrainz, coletados no T1), sem alterações.
- **Chaves:** as mesmas de `construir_indice` (`src/search/busca.py`): o nome e cada gênero do artista, em minúsculas. São **2312 inserções** e **979 chaves distintas**. Uma mesma chave pode apontar para vários artistas (184 chaves apontam para mais de um).
- **Ranking e ordenação:** o score e os dois algoritmos do T2 continuam iguais. As árvores só trocam a etapa de busca.

**Detalhe encontrado ao comparar com o T1:** no índice do T1, quatro chaves (`anitta`, `desatino`, `legião urbana`, `pig soul`) guardam o mesmo id duas vezes, porque o nome do artista também aparece entre os gêneros, ou o artista está duplicado. As árvores não repetem um id na mesma chave. Isso não muda nenhum resultado, porque o serviço já removia duplicatas antes do ranking, mas os testes comparam com a busca binária depois de tirar as repetições.

## 3. Contrato comum

As três árvores (`src/tree/`) seguem a mesma interface, combinada antes da implementação para que a dupla trabalhasse em paralelo:

| Método | Comportamento |
|---|---|
| `inserir(chave, id)` | Chave repetida acrescenta o id à lista dela, sem duplicar o mesmo id |
| `buscar(chave)` | Ids da chave, na ordem de inserção; chave ausente devolve `[]` |
| `altura()` | Árvore vazia = 0; só a raiz = 1 |
| `len(arvore)` | Número de chaves distintas |
| `buscar_prefixo(prefixo)` | Só na Trie: ids de todas as chaves que começam com o prefixo, sem repetir id |

`src/tree/api.py` registra as árvores em `INDICES` (como `src/sort/api.py` registra os algoritmos no T2), e `construir_arvore(artistas, tipo)` insere as chaves na mesma ordem do JSON. Nenhuma árvore usa `sorted`, `bisect` ou estrutura ordenada pronta.

## 4. Estruturas

### BST (Pedro, `src/tree/bst.py`)

Cada nó guarda uma chave, a lista de ids e os filhos esquerdo e direito. Inserção e busca descem pela árvore comparando a chave: menor vai para a esquerda, maior para a direita. **Tudo é iterativo**, inclusive a altura (pilha explícita). Isso foi uma decisão de projeto: com as 979 chaves inseridas em ordem, a BST vira uma lista com altura 979, perto do limite de recursão do Python (1000). Uma versão recursiva quebraria justamente no caso que queremos medir.

### AVL (Pedro, `src/tree/avl.py`)

É uma BST em que cada nó guarda a própria altura. Depois de cada inserção, o fator de balanceamento (altura da esquerda − altura da direita) é recalculado no caminho de volta. Se ele sai de [−1, 1], uma rotação corrige: simples para os casos LL e RR, dupla para LR e RL. A inserção é recursiva, o que aqui é seguro, porque a altura de uma AVL é no máximo cerca de 1,44·log₂(n). Com 20.000 chaves, isso dá menos de 21 níveis.

### Trie (Felipe, `src/tree/trie.py`)

Cada nó representa um prefixo. Os filhos ficam num dicionário caractere → nó, e o nó em que uma chave termina guarda os ids dela. Para a busca por prefixo devolver as chaves em ordem alfabética, sem usar `sorted`, cada nó mantém também a lista dos seus caracteres em ordem. Cada letra nova é colocada na posição certa por inserção, como no Insertion Sort do T2. A busca por prefixo desce até o nó do prefixo e percorre a subárvore em pré-ordem com uma pilha explícita. Assim, a chave `rap` vem antes de `rap metal`, e os ids repetidos são ignorados. Tudo é iterativo, e uma chave de 3000 caracteres está nos testes.

### Complexidade

`n` = número de chaves distintas; `m` = tamanho do termo buscado; `k` = número de chaves que começam com o prefixo; `L` = soma do tamanho das chaves dessa subárvore.

| Operação | Lista ordenada (T1) | BST | AVL | Trie |
|---|---|---|---|---|
| Construir com n chaves | O(n log n) (ordena uma vez) | O(n log n) médio, O(n²) com chaves em ordem | O(n log n) | O(soma dos tamanhos das chaves) |
| Inserir uma chave nova | O(n) (deslocar a lista) | O(h); h = n no pior caso | O(log n) | O(m) |
| Busca exata | O(log n) comparações | O(h) | O(log n) | O(m), não depende de n |
| Busca por prefixo | O(n) varrendo, ou O(log n + k) com duas buscas binárias* | — | — | O(m + L) |
| Memória | Uma entrada por chave | Um nó por chave | Um nó por chave, mais a altura | Um nó por **caractere** distinto de prefixo |

\* A busca por prefixo em lista ordenada poderia usar busca binária para achar o início do intervalo. No benchmark, comparamos a Trie com a **varredura linear** (`startswith` em todas as chaves), que é o que o projeto teria sem uma estrutura própria. Essa ressalva vale para a discussão.

Nas comparações de string, "O(log n) comparações" esconde o custo de comparar textos, que pode chegar a O(m) cada uma. A Trie compara um caractere por nível.

## 5. Integração

Pedro integrou as árvores em `src/servico.py`: `pesquisar_e_ordenar` aceita `busca` igual a `sequencial`, `binaria`, `bst`, `avl`, `trie` ou `prefixo`. O serviço normaliza o termo (`strip().lower()`) uma vez. As quatro últimas opções montam o índice com `construir_arvore`, buscam os ids e seguem para o ranking e a ordenação do T2, sem mudança nenhuma neles. As árvores não normalizam por conta própria: recebem as chaves e os termos já normalizados, e as três se comportam igual nisso. A CLI expõe as opções novas, e um erro de busca vira mensagem do `argparse`, sem traceback:

```bash
python main.py --busca avl --termo rock
python main.py --busca prefixo --termo samb --limite 5
```

```text
Busca: prefixo | Ordenação: Merge Sort
Total encontrado: 65
1. Os Originais do Samba | Score: 30 | Gêneros: samba
2. Adriana Calcanhotto | Score: 0 | Gêneros: mpb, brazilian, bossa nova, samba, ...
```

`tests/test_arvores_contrato.py` verifica que, para as 979 chaves reais e para 20 termos ausentes, BST, AVL e Trie devolvem os mesmos ids que a busca binária do T1 (sem repetições). Também verifica que `buscar_prefixo` devolve o mesmo que a varredura linear para todos os prefixos reais de 1 a 3 letras. Foi um teste desse tipo, escrito pelo Pedro, que mostrou que a Trie normalizava os termos e as outras árvores não. A Trie foi ajustada.

**Limitação do ranking na busca por prefixo:** o score do T2 dá +40 só para gênero **igual** ao termo e +30 para nome que **contém** o termo. Numa busca por prefixo, o termo raramente é um gênero completo. Com `ro`, 41 dos 56 artistas encontrados ficam com score 0 e 15 com score 30. Com `samb`, 64 de 65 ficam com 0. A busca encontra os artistas certos, mas o ranking quase não os diferencia, e os empates seguem a ordem alfabética das chaves (o Merge Sort é estável). Um score próprio para prefixo (por exemplo, pontos para gênero que **começa** com o termo) fica como trabalho futuro.

## 6. Metodologia

Script: `benchmarks/benchmark_arvores.py` (Felipe). Comando da coleta final:

```bash
python -m benchmarks.benchmark_arvores --dados data/processed/artistas.json --repeticoes 10 --tamanhos-sinteticos 1000 5000 20000 --consultas 200 --semente 42 --saida benchmarks/resultados_t3.csv
```

**Entradas**

| Origem | Chaves | Para quê |
|---|---|---|
| `real` | As 2312 inserções (979 chaves distintas) de nome e gêneros, como em `construir_arvore` | Uso real do motor |
| `sintetico` | 1000, 5000 e 20.000 chaves distintas, palavras aleatórias de 3 a 12 letras (`a`–`z`) | Ver o crescimento com n |

**Cenários (ordem de inserção):** os dados reais entram em `original` (a ordem do JSON, que já vem **ordenado por nome**), `aleatorio` e `ordenado`. Os sintéticos entram em `aleatorio`, `ordenado` e `quase_ordenado` (ordenado com n/20 trocas próximas). A BST fica fora dos casos ordenado e quase ordenado com n > 5000: ali ela é uma lista, cada inserção custa O(n), e o caso levaria minutos sem mostrar nada novo. A exclusão fica registrada no resumo.

**Consultas:** 200 buscas exatas por base (metade de chaves presentes, sorteadas; metade de palavras ausentes) e 30 prefixos de 1, 2 e 3 letras, sorteados entre as chaves. As mesmas consultas valem para todas as estruturas e para os três cenários da mesma base.

**Medição**

- Cada estrutura é construída a partir da **mesma** sequência de pares (chave, id). O cronômetro (`time.perf_counter_ns()`) mede a construção completa e, separadamente, o lote de buscas, dividido pelo número de buscas (µs por busca).
- Antes de medir, fora do cronômetro, todas as estruturas são comparadas com a lista ordenada em todas as consultas exatas, e a Trie com a varredura em todos os prefixos. Qualquer divergência interrompe a coleta.
- 1 aquecimento descartado e 10 repetições. O resumo usa mediana e IQR (Q3 − Q1, quartis inclusivos), como no T2.
- A altura é determinística e é registrada uma vez por caso.
- As sementes de cada caso são derivadas da semente base 42 por SHA-256, como no T2. `entradas_t3.json` guarda, por caso, o hash da sequência inserida, as primeiras chaves e todas as consultas. As chaves sintéticas são regeneradas pela semente.
- São 12 casos e **1674 medições**, em 46 segundos.

**Ambiente** (de `benchmarks/ambiente_t3.json`): CPython 3.14.6, Linux 6.19.14 (Fedora 43), AMD Ryzen 5 5500U, código na revisão `5d5bfb17a1b1cfaf72fe5cd7d91ba1fd33e4cc61` (árvore limpa). Essa revisão já tinha a BST, a AVL e a Trie registradas, com o mesmo código que entrou na `main` pelo PR #4. A memória não foi medida com ferramenta; o número de nós da Trie é contado e serve de indicação.

## 7. Resultados

Tabelas extraídas de `benchmarks/resumo_t3.md`, que tem os 12 casos com IQR. As 1674 medições estão em `benchmarks/resultados_t3.csv`. Os valores são medianas de 10 repetições.

### Altura

| Origem | n | Cenário | BST | AVL | Trie |
|---|---:|---|---:|---:|---:|
| real | 979 | original (JSON) | 39 | 12 | 33 |
| real | 979 | aleatorio | 20 | 12 | 33 |
| real | 979 | ordenado | **979** | 10 | 33 |
| sintetico | 1000 | aleatorio | 22 | 12 | 13 |
| sintetico | 1000 | quase_ordenado | 746 | 11 | 13 |
| sintetico | 5000 | aleatorio | 30 | 15 | 13 |
| sintetico | 5000 | ordenado | **5000** | 13 | 13 |
| sintetico | 20000 | aleatorio | 33 | 17 | 13 |
| sintetico | 20000 | ordenado | — | 15 | 13 |

### Construção do índice (ms)

| Origem | n | Cenário | Lista ordenada | BST | AVL | Trie |
|---|---:|---|---:|---:|---:|---:|
| real | 979 | original | 0,469 | 1,95 | 6,70 | 5,91 |
| real | 979 | ordenado | 0,309 | 54,2 | 7,47 | 6,66 |
| sintetico | 5000 | aleatorio | 2,75 | 6,28 | 22,5 | 36,3 |
| sintetico | 5000 | ordenado | 1,59 | 564,3 | 22,0 | 38,0 |
| sintetico | 20000 | aleatorio | 26,5 | 49,6 | 130,9 | 326,8 |

### Busca exata (µs por busca)

| Origem | n | Cenário | Lista ordenada | BST | AVL | Trie |
|---|---:|---|---:|---:|---:|---:|
| real | 979 | original | 1,28 | 0,86 | 0,64 | 0,77 |
| real | 979 | ordenado | 1,26 | 24,0 | 0,78 | 1,01 |
| sintetico | 5000 | ordenado | 1,57 | 116,0 | 1,43 | 1,18 |
| sintetico | 20000 | aleatorio | 2,72 | 2,87 | 2,93 | 1,35 |

### Busca por prefixo (µs por busca): Trie × varredura linear

| Origem | n | Cenário | Prefixo | Trie | Varredura |
|---|---:|---|---|---:|---:|
| real | 979 | original | 1 letra | 120,5 | 47,2 |
| real | 979 | original | 2 letras | 19,0 | 30,6 |
| real | 979 | original | 3 letras | 8,9 | 29,2 |
| sintetico | 20000 | ordenado | 1 letra | 1119 | 1861 |
| sintetico | 20000 | ordenado | 2 letras | 48,3 | 1596 |
| sintetico | 20000 | ordenado | 3 letras | 6,0 | 1349 |

## 8. Discussão

**A BST degenera com os dados reais?** Em parte, e já na ordem do próprio JSON. Como os artistas vêm ordenados por nome, as chaves de nome entram em ordem crescente, intercaladas com os gêneros. A altura foi 39, o dobro da altura com as mesmas chaves embaralhadas (20). Com as chaves totalmente ordenadas, a BST vira uma lista: altura 979 com os dados reais e 5000 com 5000 chaves sintéticas. Nesse caso a busca exata fica cerca de 80 vezes mais lenta que na AVL (116,0 contra 1,43 µs, n = 5000), e a construção cerca de 26 vezes (564 contra 22 ms). É o pior caso O(n) da teoria, e foi para medi-lo que a BST foi escrita sem recursão.

**A AVL compensa o custo das rotações?** No caso favorável à BST, ela é mais lenta para construir (22,5 contra 6,3 ms com 5000 chaves aleatórias), porque recalcula alturas e faz rotações a cada inserção, e porque a inserção é recursiva. Em troca, a altura ficou entre 10 e 17 em **todos** os casos, perto de log₂(n), e o tempo de busca não depende da ordem de entrada. Para um índice que recebe dados já ordenados, como o JSON deste projeto, essa garantia é o que importa.

**E a lista ordenada do T1?** Ela foi a mais rápida para construir em todos os casos (26,5 ms com 20.000 chaves, contra 49,6 da BST, 130,9 da AVL e 326,8 da Trie). Isso acontece porque o `sorted` do Python é implementado em C, e as árvores são Python puro. Na busca exata com até 5000 chaves, as estruturas balanceadas ficaram entre 0,6 e 2,1 µs, com diferenças próximas do ruído. Com 20.000 chaves, a Trie foi a mais rápida (1,35 contra 2,7 a 2,9 µs das outras), coerente com o custo O(m) dela não depender de n. A vantagem principal das árvores, porém, não é a busca exata num índice que não muda. É **inserir uma chave nova** em O(log n) (AVL) ou O(m) (Trie), sem reordenar a lista. Isso não foi medido separadamente.

**A Trie ganha da varredura na busca por prefixo?** Depende do tamanho do prefixo. Com 2 ou 3 letras, ela ganha de 1,6 a 3,3 vezes nos dados reais e de 33 a 226 vezes com 20.000 chaves (cenário ordenado), porque desce direto ao prefixo e só visita as chaves que começam com ele. Com **1 letra**, ela perde nos dados reais (120,5 contra 47,2 µs). Uma letra seleciona uma parte grande do índice, e percorrer nó a nó (um por caractere) custa mais em Python que testar `startswith` nas 979 chaves. Com 20.000 chaves, a Trie volta a ganhar até com 1 letra (1119 contra 1861 µs). Na varredura com 20.000 chaves, o IQR chegou perto da mediana em vários casos. Por isso citamos os ganhos como ordem de grandeza: dezenas de vezes com 2 letras, centenas com 3.

**Quanto de memória a Trie custa?** Para as 979 chaves reais, a Trie tem **7768 nós**, contra 979 nós da BST ou da AVL: cerca de 8 vezes mais, um por caractere de prefixo distinto. A altura dela não depende de n, e sim do tamanho da maior chave: 33 = os 32 caracteres de `fred sun walk & the dog brothers` mais a raiz. Por isso ela não muda com a ordem de inserção.

**Limitações**

- Há uma única máquina e um único interpretador. Os tempos absolutos não se generalizam, e a comparação favorece o `sorted` em C contra as árvores em Python puro.
- Uma busca exata leva de 1 a 3 µs. Nessa escala o ruído é grande: alguns IQRs da AVL passam da metade da mediana, e a construção da Trie com 5000 chaves aleatórias teve IQR (36,8 ms) maior que a mediana (36,3 ms). Diferenças menores que o IQR não sustentam conclusões.
- As chaves sintéticas são palavras aleatórias, sem a distribuição de prefixos de nomes reais.
- A busca por prefixo foi comparada com a varredura linear, não com uma busca binária de intervalo na lista ordenada.
- A memória foi estimada pelo número de nós, não medida.
- A inserção incremental, que é a principal vantagem das árvores, não foi medida isoladamente.
- Na busca por prefixo, o ranking do T2 deixa a maior parte dos resultados com score 0 (seção 5).

## 9. Divisão e reprodução

| Felipe Matheus Ribeiro Lopes | Pedro Araujo Lucena |
|---|---|
| Trie (`src/tree/trie.py`, `tests/test_trie.py`) | BST (`src/tree/bst.py`, `tests/test_bst.py`) |
| Testes cruzados das árvores (`tests/test_arvores_contrato.py`) | AVL (`src/tree/avl.py`, `tests/test_avl.py`) |
| Benchmark (`benchmarks/benchmark_arvores.py`, `tests/test_benchmark_arvores.py`) | Registro e construção (`src/tree/api.py`) |
| Coleta (`benchmarks/*_t3.*`), este relatório e o roteiro do vídeo | Integração no serviço e na CLI (`src/servico.py`, `main.py`) |

```bash
python -m unittest discover -s tests -v
python -m benchmarks.benchmark_arvores --repeticoes 2 --tamanhos-sinteticos 1000 --saida /tmp/ensaio_t3.csv   # ensaio rápido
python -m benchmarks.benchmark_arvores --dados data/processed/artistas.json --repeticoes 10 --tamanhos-sinteticos 1000 5000 20000 --consultas 200 --semente 42 --saida benchmarks/resultados_t3.csv
```

## 10. Próximas etapas

- **T4 (Grafos):** artistas ligados por gêneros em comum. As chaves de gênero e os ids que a Trie e a AVL já agrupam são exatamente as arestas desse grafo.
- **Autocompletar na CLI:** a busca por prefixo pode limitar o número de resultados e parar a travessia da Trie mais cedo, o que resolveria o caso de 1 letra.
