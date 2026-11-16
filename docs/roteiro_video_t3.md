# Roteiro do vídeo T3 (5 minutos)

**Formato:** terminal legível (fonte grande) e os dois falando. Nada de ler código linha por linha.
**Antes de gravar:** rode `git pull` na `main` depois do PR do Felipe. Os números citados abaixo vêm de `benchmarks/resumo_t3.md`.

| Tempo | Quem | Conteúdo |
|---|---|---|
| 0:00–0:30 | Pedro | Do índice ordenado do T1 às árvores |
| 0:30–1:45 | Pedro | BST, degeneração e AVL com uma rotação desenhada |
| 1:45–2:45 | Felipe | Trie e busca por prefixo |
| 2:45–3:30 | Pedro | Demonstração na CLI |
| 3:30–4:30 | Felipe | Metodologia e resultados do benchmark |
| 4:30–5:00 | Felipe | Conclusão, limitações e ligação com o T4 |

## 0:00–0:30 · Pedro: do T1 ao T3

> "No T1, o índice da busca era uma lista ordenada com 979 chaves: o nome e os gêneros de cada um dos 553 artistas. A busca binária encontrava uma chave em O(log n). Mas essa lista tem dois limites: para inserir uma chave nova é preciso reordenar, e ela só acha a chave completa. No T3 trocamos esse índice por três árvores: BST, AVL e Trie. O ranking e a ordenação do T2 continuam iguais; só a etapa de busca mudou."

## 0:30–1:45 · Pedro: BST, degeneração e AVL

Desenhar (no papel ou num slide) as chaves `a`, `b`, `c` inseridas nessa ordem.

> "Numa BST, menor vai para a esquerda e maior para a direita. Se as chaves chegam em ordem, cada uma vira filha direita da anterior, e a árvore vira uma lista. Isso não é teórico: o nosso JSON já vem ordenado por nome. Com as 979 chaves em ordem, a BST ficou com altura 979. Por isso fiz a BST toda iterativa: uma versão recursiva estouraria o limite de recursão do Python, que é 1000."

Mostrar a rotação simples à esquerda (caso RR): `a → b → c` vira `b` com filhos `a` e `c`.

> "A AVL guarda a altura de cada nó. Quando um lado fica mais de um nível mais alto que o outro, uma rotação corrige. Aqui o `a` ficou desbalanceado para a direita, então o `b` sobe e o `a` desce para a esquerda. São quatro casos: LL e RR com uma rotação, LR e RL com duas. Com as mesmas 979 chaves em ordem, a AVL ficou com altura 10."

## 1:45–2:45 · Felipe: Trie e busca por prefixo

Desenhar as chaves `rap`, `rap metal` e `rock` numa Trie: `r` na raiz, que se divide em `a` e `o`.

> "Na Trie, cada nível é um caractere. Chaves com o mesmo começo compartilham o caminho: `rap` e `rock` dividem o `r`. O nó onde uma chave termina guarda os ids dos artistas. Para buscar, desço uma letra por vez, então o custo é O(m), o tamanho do termo, e não depende de quantas chaves existem. E aparece algo que a busca binária não fazia: a busca por prefixo. Desço até `ro` e recolho tudo que está abaixo. Os filhos de cada nó ficam em ordem alfabética, mantidos por inserção, como no Insertion Sort do T2, sem `sorted`. Por isso o resultado sai em ordem alfabética, com `rap` antes de `rap metal`. O custo é memória: para as 979 chaves, a Trie tem 7768 nós, um por caractere, contra 979 da AVL."

## 2:45–3:30 · Pedro: demonstração

```bash
python main.py --termo rock --busca binaria --limite 3
python main.py --termo rock --busca avl --limite 3
python main.py --termo samb --busca prefixo --limite 5
```

> "A mesma busca por `rock` na binária e na AVL: os mesmos 35 artistas, na mesma ordem. Os testes cruzados do Felipe conferem isso para todas as 979 chaves e para as três árvores. E com `prefixo`, `samb` encontra 65 artistas que têm alguma chave começando por `samb`."

Comentar o score: na busca por prefixo, quase todos aparecem com score 0, porque o ranking do T2 só pontua gênero **igual** ao termo. Isso é uma limitação registrada no relatório.

## 3:30–4:30 · Felipe: metodologia e resultados

> "No benchmark, as quatro estruturas, contando a lista ordenada do T1, recebem a mesma sequência de chaves e as mesmas consultas. Usamos as chaves reais e chaves sintéticas de 1000, 5000 e 20.000, inseridas em ordem aleatória, ordenada e quase ordenada. Antes de medir, o script confere que todas respondem igual. Cada caso tem um aquecimento descartado e 10 repetições, e reportamos a mediana. São 1674 medições."

Mostrar estas tabelas, copiadas de `benchmarks/resumo_t3.md`:

| Caso | Altura BST | Altura AVL | Busca BST (µs) | Busca AVL (µs) |
|---|---:|---:|---:|---:|
| reais, ordem do JSON | 39 | 12 | 0.86 | 0.64 |
| reais, ordenadas | 979 | 10 | 24.0 | 0.78 |
| 5000 sintéticas, ordenadas | 5000 | 13 | 116.0 | 1.43 |

| Prefixo (µs) | 1 letra | 2 letras | 3 letras |
|---|---:|---:|---:|
| Trie, chaves reais | 120.5 | 19.0 | 8.9 |
| Varredura, chaves reais | 47.2 | 30.6 | 29.2 |
| Trie, 20.000 chaves | 1119 | 48.3 | 6.0 |
| Varredura, 20.000 chaves | 1861 | 1596 | 1349 |

> "Com chaves em ordem, a BST virou uma lista e ficou cerca de 80 vezes mais lenta que a AVL na busca. A AVL ficou entre 10 e 17 de altura em todos os casos. Na busca por prefixo, a Trie ganha com 2 ou 3 letras: com 20.000 chaves, 6 microssegundos contra mais de 1 milissegundo da varredura. Mas com 1 letra, nos dados reais, ela perdeu, porque uma letra seleciona boa parte do índice, e percorrer a árvore nó a nó custa mais do que testar todas as chaves."

## 4:30–5:00 · Felipe: conclusão

> "A BST sozinha não serve para os nossos dados, que já chegam ordenados. A AVL resolve isso com uma garantia de altura, e a Trie é a estrutura certa para busca por prefixo. A lista ordenada do T1 continua a mais rápida de construir, porque o `sorted` é feito em C. A vantagem das árvores está em inserir uma chave sem reordenar tudo. Limitações: uma única máquina, ruído grande em buscas de microssegundos, memória estimada pelo número de nós e um ranking que não pontua prefixos. Divisão: o Pedro fez a BST, a AVL e a integração com o serviço e a CLI. Eu fiz a Trie, os testes cruzados, o benchmark e a análise. No T4, as chaves de gênero que as árvores já agrupam viram as arestas de um grafo de artistas."
