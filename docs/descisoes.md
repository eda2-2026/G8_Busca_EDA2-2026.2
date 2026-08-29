# Decisões de Implementação - T1

## 1. Busca com String Vazia
Durante os testes, notamos que buscar por uma string vazia (`""`) na **busca sequencial** retorna todos os artistas do banco de dados (pois uma string vazia está tecnicamente contida em qualquer nome/gênero no Python). 

Para manter a consistência e evitar travamentos no sistema caso o usuário aperte "Enter" sem digitar nada, decidimos aceitar esse comportamento padrão: uma busca vazia traz a listagem completa (ou falha graciosamente retornando lista vazia, dependendo de como a interface lidará no futuro).