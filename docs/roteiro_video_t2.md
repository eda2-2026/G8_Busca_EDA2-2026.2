# Roteiro do vídeo T2 (5 minutos)

**Formato:** terminal legível (fonte grande) e os dois falando. Nada de ler código linha por linha.
**Antes de gravar:** a CLI do Pedro (A5) precisa estar integrada para a demonstração, e os números citados abaixo vêm de `benchmarks/resumo_t2.md`.

| Tempo | Quem | Conteúdo |
|---|---|---|
| 0:00–0:30 | Pedro | O que o T1 fazia e o que o T2 acrescenta |
| 0:30–1:10 | Pedro | Ranking com exemplo e empates |
| 1:10–1:50 | Pedro | Insertion Sort |
| 1:50–2:35 | Felipe | Merge Sort |
| 2:35–3:15 | Pedro | Demonstração: a mesma busca com os dois algoritmos |
| 3:15–4:25 | Felipe | Metodologia e resultados |
| 4:25–5:00 | Felipe | Conclusão, limitações e divisão |

## 0:00–0:30 · Pedro: do T1 ao T2

> "No T1 o nosso motor respondia *quais* artistas combinam com a busca, usando busca sequencial e binária sobre 553 artistas que o Felipe coletou do MusicBrainz. No T2 a pergunta é *em que ordem* mostrar esses artistas. Para isso, damos um score de relevância a cada um e ordenamos com dois algoritmos que implementamos: Insertion Sort e Merge Sort."

## 0:30–1:10 · Pedro: ranking

Mostrar a tabela fictícia (a–f) do relatório, **identificada como fictícia**.

> "Nome igual à busca vale 60 pontos. Nome que contém a busca vale 30. Gênero igual vale mais 40. Ordenamos pela chave igual a menos o score, em ordem crescente, então quem tem mais pontos aparece primeiro. Como só existem seis scores possíveis, empate é a regra: na base real, os 35 artistas de `rock` têm todos 40 pontos. Por isso os dois algoritmos precisam ser estáveis, mantendo a ordem original entre os empatados."

## 1:10–1:50 · Pedro: Insertion Sort

Mostrar as chaves `[-40, -100, -70]` virando `[-100, -70, -40]`, com pelo menos um deslocamento.

> "O trecho da esquerda já está ordenado. Pego o próximo item e desloco para a direita só quem tem chave *estritamente maior*. É esse 'estritamente' que garante a estabilidade. Melhor caso O(n), quando já está ordenado ou tudo empatado. Caso médio e pior caso O(n²)."

## 1:50–2:35 · Felipe: Merge Sort

Mostrar o exemplo do teste `test_empates_entre_as_duas_metades_preservam_a_ordem`: entrada `a(-40) b(-40) c(-100) | d(-40) e(-100) f(-40)`, saída `c e a b d f`.

> "O Merge divide a lista ao meio, ordena cada metade e intercala as duas com dois índices. No empate, eu sempre tiro primeiro da metade da esquerda, e é isso que deixa o Merge estável. Neste exemplo, `a` e `b` estão na esquerda e `d` e `f` na direita, todos com −40: na saída eles continuam na ordem original. São log n níveis, cada um intercalando n itens, então O(n log n) em qualquer caso, pagando O(n) de memória extra. Os dois algoritmos devolvem uma lista nova e não mexem nos dados de entrada, e os testes cruzados comparam as duas saídas item a item."

## 2:35–3:15 · Pedro: demonstração

```bash
python main.py --termo rock --algoritmo insertion
python main.py --termo rock --algoritmo merge
```

> "A mesma busca, os mesmos 35 artistas, na mesma ordem com os dois algoritmos, inclusive nos empates."

Se o top 10 estiver todo empatado (é o esperado para `rock`), dizer isso e mostrar também `--termo samba`. Lá aparece 1 artista com 70 pontos na frente dos 50 com 40.

## 3:15–4:25 · Felipe: metodologia e resultados

> "Para comparar de forma justa, os dois algoritmos recebem exatamente a mesma lista em cada caso. O cronômetro mede só a chamada de ordenação: busca, score, validação e escrita de arquivo ficam de fora. Cada caso tem um aquecimento descartado e 10 repetições, alternando quem roda primeiro, e reportamos mediana e intervalo interquartil. Usamos a busca real por `rock`, prefixos do catálogo real e dados sintéticos de 100, 500 e 2000 itens, em cinco ordens iniciais. No total são 1000 medições, e o commit do código medido e o hash do dataset ficam registrados."

Mostrar esta tabela, copiada de `benchmarks/resumo_t2.md` (cenário aleatório, mediana em ms):

| Origem | n | Insertion | Merge |
|---|---:|---:|---:|
| consulta_real | 35 | 0.01027 | 0.05944 |
| catalogo_real | 553 | 0.6069 | 0.6637 |
| sintetico_faixa_ampla | 100 | 0.1828 | 0.1326 |
| sintetico_faixa_ampla | 500 | 4.455 | 0.8013 |
| sintetico_faixa_ampla | 2000 | 84.24 | 3.956 |

> "Com chaves variadas, o Merge já vence em 100 itens e fica cerca de 21 vezes mais rápido em 2000. No inverso, o Insertion dobra de tempo (166 ms em 2000 itens), como a teoria prevê. Mas nos dados reais, que são pequenos e quase todos empatados, o Insertion ganhou, porque ali ele está perto do melhor caso. Na entrada já ordenada ele vence sempre."

## 4:25–5:00 · Felipe: conclusão

> "Não existe um vencedor absoluto. Para as nossas consultas reais, as diferenças são de centésimos de milissegundo. O Merge garante O(n log n) se o catálogo crescer ou o score ganhar mais níveis, e o Insertion brilha em listas pequenas, ordenadas ou empatadas. Limitações: uma única máquina, um ranking com poucos scores e memória discutida só na teoria. Divisão: o Pedro fez o ranking, o Insertion, a integração com a CLI e o README. Eu fiz o Merge, os testes cruzados, o benchmark e a análise. No T3, o índice da busca vira uma árvore."
