# Análise de Dados Legislativos - Câmara dos Deputados com Neo4j

**Trabalho 2 - Banco de Dados para Ciência de Dados**
**Aluno**: Eduardo Spinelli - RA 800220

## Descrição

Este projeto analisa dados da Câmara dos Deputados do Brasil utilizando Neo4j (banco de dados orientado a grafos). Os dados são coletados da API oficial de Dados Abertos e importados para análise de relacionamentos entre deputados, partidos, estados e frentes parlamentares.

## Estrutura do Projeto

```
.
├── coletor_dados.py       # Script de coleta de dados da API
├── importar_aura.py       # Script de importação para Neo4j Aura
├── executar_analises.py   # Script com as 5 consultas analíticas
├── dados_camara/          # Diretório com dados coletados (JSON)
├── main.tex               # Documento LaTeX do trabalho
└── README.md              # Este arquivo
```

## Dataset

- **Deputados**: 1.125
- **Partidos**: 38
- **Frentes Parlamentares**: 1.428
- **Estados (UF)**: 27
- **Relacionamentos**: 2.250

## Como Usar

### 1. Coletar Dados

```bash
python coletor_dados.py --modo rapido
```

Modos disponíveis:
- `teste`: Poucos dados para testes
- `rapido`: Dados essenciais (padrão)
- `completo`: Todos os dados disponíveis

### 2. Importar para Neo4j Aura

Configure suas credenciais no arquivo `importar_aura.py` e execute:

```bash
python importar_aura.py --limpar
```

### 3. Executar Análises

```bash
python executar_analises.py
```

Este script executa as 5 consultas analíticas:
1. Distribuição de deputados por partido
2. Distribuição geográfica por região
3. Força partidária por região
4. Análise de frentes temáticas
5. Composição partidária multidimensional

## Requisitos

```bash
pip install neo4j requests
```

## Fonte dos Dados

API de Dados Abertos da Câmara dos Deputados:
https://dadosabertos.camara.leg.br/swagger/api.html

## Neo4j

- **Instância**: Neo4j Aura (cloud)
- **Driver**: neo4j-python-driver

## Modelo de Dados

### Nós
- `Deputado`: Deputados federais
- `Partido`: Partidos políticos
- `Frente`: Frentes parlamentares
- `UF`: Estados brasileiros

### Relacionamentos
- `FILIADO_A`: Deputado → Partido
- `REPRESENTA`: Deputado → UF

## Licença

Projeto acadêmico - UFSCar 2025
