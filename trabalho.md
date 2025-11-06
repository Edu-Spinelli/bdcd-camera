Tema do trabalho: Análise de Dados Câmara dos Deputados do Brasil com Neo4j
 
Grupo deve obrigatoriamente ser feito por 2 alunos.
 
 
Objetivo Principal
Desenvolver habilidades práticas em resolução de problemas, trabalho em equipe,  modelagem, carga, consulta de bancos de dados orientados a grafos e conexão com linguagens de programação. Os alunos deverão extrair um conjunto de dados públicos da internet, modelá-lo como um grafo, carregá-lo no Neo4j e, através de consultas em Cypher, descobrir e apresentar insights que não seriam triviais em um modelo relacional.
 
Qual é o desafio do trabalho?
Modelar a relação entre frentes, deputados, partidos, projetos de lei e seus votos.
 
Quais dados você deverá usar?
Portal de Dados Abertos da Câmara dos Deputados
https://dadosabertos.camara.leg.br/swagger/api.html
Datasets sugeridos para serem usados:
A.     frentes: agrupamento de deputados a respeito de um determinado tema (idFrente, idDeputado, tipo frente)
B.     deputados: Lista de todos os deputados (id, nome, partido, UF, etc.).
C.    proposicoes: Lista de projetos de lei, PECs, etc. (id, tipo, ano, ementa).
D.    proposicoesAutores: Tabela que conecta proposições aos seus autores (deputados).
E.     votacoesVotos: Registro de como cada deputado votou em diversas votações.
 
 
 
O que você deve fazer e entregar?
 
Entregar um documento .pdf com:
 
 
1 -  Os nomes completos dos integrantes do grupo
 
 
2 - Introdução e descrição do dataset escolhido:
a)     dados envolvidos, quantidade;
b)     período a que os dados se referem;
c)     outros detalhes importantes para entendermos os dados;
 
2 – Script de coleta/obtenção de dados ou printscreen das telas principais de coleta;
 
3 – Modelagem dos dados. Fazer um diagrama de como será modelado a base (pode-se usar o Canvas ou outra ferramenta que desejar). Colar no trabalho a figura com a ilustração:
a)     2 itens de cada tipo de nó;
b)     2 itens de cada tipo de relacionamento possíveis entre eles..
 
3 – Script de importação dos dados e/ou tela de importação
 
4 – Consulta com todos os dados importados..  Colar um print-screen da tela gráfica resultado da consulta.
 
5 – Fazer 5 perguntas interessantes no grafo para gerar insights que serão mapeadas para consultas Cypher. Ir além de buscas simples. Exemplo de pergunta “Deputados de um mesmo estado (UF) tendem a ser autores dos mesmos tipos de projetos?”. Para cada consulta, fazer e colocar no documento a ser entregue:
a.     A pergunta de negócio/análise.
b.     O código Cypher da consulta.
c.      Um printscreen do resultado (tabela ou visualização do grafo).
d.     Uma análise escrita (1-2 parágrafos) sobre o que aquele resultado significa. (Esta é a parte mais importante).
6 - Conclusão sobre os desafios e aprendizados do projeto.
7 - Link para um repositório (GitHub) ou pasta compartilhada com os scripts e o dataset original.
 
 
Critérios de Avaliação:
Completude de tudo que foi pedido
Modelagem do grafo: a lógica do modelo, clareza e adequação ao problema.
Implementação da carga: o sucesso na importação dos dados e a qualidade dos scripts.
Complexidade e correção das consultas:  habilidade de traduzir perguntas em Cypher e a complexidade das consultas criadas.
Qualidade dos insights e análise: a capacidade de ir além dos dados, interpretando os resultados e apresentando conclusões interessantes e bem escritas.

