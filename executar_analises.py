"""
Executa as 5 consultas de análise e gera resultados
"""

from neo4j import GraphDatabase
import json

class AnalisadorDados:
    def __init__(self):
        self.URI = "neo4j+s://2a3ba8da.databases.neo4j.io"
        self.AUTH = ("neo4j", "N_CdGEmG4OlD7yhMOgsvkkUzHxq7Gi_-5D5kpvcMAV4")
        self.driver = GraphDatabase.driver(self.URI, auth=self.AUTH)
        print("✓ Conectado ao Neo4j Aura\n")

    def close(self):
        self.driver.close()

    def executar_query(self, query, descricao):
        print(f"\n{'='*70}")
        print(f"📊 {descricao}")
        print(f"{'='*70}\n")

        with self.driver.session() as session:
            result = session.run(query)
            dados = [dict(record) for record in result]

            if dados:
                # Mostrar primeiros resultados
                for i, row in enumerate(dados[:15], 1):
                    print(f"{i}. ", end="")
                    for key, value in row.items():
                        print(f"{key}: {value} | ", end="")
                    print()

                if len(dados) > 15:
                    print(f"\n... e mais {len(dados) - 15} resultados")
            else:
                print("Nenhum resultado encontrado")

            print(f"\n✓ Total de resultados: {len(dados)}")
            return dados

    def analise1_distribuicao_partidos(self):
        query = """
        MATCH (p:Partido)<-[:FILIADO_A]-(d:Deputado)
        WITH p, count(d) AS numDeputados
        RETURN p.sigla AS Partido,
               p.nome AS NomeCompleto,
               numDeputados AS NumeroDeputados
        ORDER BY numDeputados DESC
        LIMIT 20
        """
        return self.executar_query(query, "ANÁLISE 1: Distribuição de Deputados por Partido")

    def analise2_geografia_politica(self):
        query = """
        MATCH (uf:UF)<-[:REPRESENTA]-(d:Deputado)
        WITH uf, count(d) AS numDeputados
        RETURN uf.sigla AS Estado,
               uf.nome AS NomeEstado,
               uf.regiao AS Regiao,
               numDeputados AS NumDeputados
        ORDER BY numDeputados DESC
        """
        return self.executar_query(query, "ANÁLISE 2: Geografia Política - Deputados por Estado")

    def analise3_geografia_por_regiao(self):
        query = """
        MATCH (uf:UF)<-[:REPRESENTA]-(d:Deputado)
        WITH uf.regiao AS Regiao, count(d) AS numDeputados
        RETURN Regiao,
               numDeputados AS TotalDeputados
        ORDER BY numDeputados DESC
        """
        return self.executar_query(query, "ANÁLISE 3: Deputados por Região")

    def analise4_partidos_por_regiao(self):
        query = """
        MATCH (d:Deputado)-[:FILIADO_A]->(p:Partido)
        MATCH (d)-[:REPRESENTA]->(uf:UF)
        WITH uf.regiao AS Regiao, p.sigla AS Partido, count(d) AS numDeputados
        WHERE numDeputados > 5
        RETURN Regiao, Partido, numDeputados AS NumDeputados
        ORDER BY Regiao, numDeputados DESC
        """
        return self.executar_query(query, "ANÁLISE 4: Partidos com mais Deputados por Região")

    def analise5_frentes_tematicas(self):
        query = """
        MATCH (f:Frente)
        WHERE f.titulo CONTAINS 'Defesa' OR f.titulo CONTAINS 'Apoio'
        RETURN f.titulo AS Frente,
               f.idLegislatura AS Legislatura
        ORDER BY f.titulo
        LIMIT 30
        """
        return self.executar_query(query, "ANÁLISE 5: Frentes Temáticas (Defesa e Apoio)")

    def estatisticas_gerais(self):
        print(f"\n{'='*70}")
        print(f"📈 ESTATÍSTICAS GERAIS DO GRAFO")
        print(f"{'='*70}\n")

        with self.driver.session() as session:
            # Contar nós
            result = session.run("MATCH (d:Deputado) RETURN count(d) as count")
            print(f"• Deputados: {result.single()['count']:,}")

            result = session.run("MATCH (p:Partido) RETURN count(p) as count")
            print(f"• Partidos: {result.single()['count']:,}")

            result = session.run("MATCH (f:Frente) RETURN count(f) as count")
            print(f"• Frentes: {result.single()['count']:,}")

            result = session.run("MATCH (uf:UF) RETURN count(uf) as count")
            print(f"• UFs: {result.single()['count']:,}")

            # Contar relacionamentos
            result = session.run("MATCH ()-[r:FILIADO_A]->() RETURN count(r) as count")
            print(f"\n• Relacionamentos FILIADO_A: {result.single()['count']:,}")

            result = session.run("MATCH ()-[r:REPRESENTA]->() RETURN count(r) as count")
            print(f"• Relacionamentos REPRESENTA: {result.single()['count']:,}")

if __name__ == "__main__":
    analisador = AnalisadorDados()

    try:
        # Estatísticas gerais
        analisador.estatisticas_gerais()

        # 5 Análises
        analisador.analise1_distribuicao_partidos()
        analisador.analise2_geografia_politica()
        analisador.analise3_geografia_por_regiao()
        analisador.analise4_partidos_por_regiao()
        analisador.analise5_frentes_tematicas()

        print(f"\n{'='*70}")
        print("✅ ANÁLISES CONCLUÍDAS!")
        print(f"{'='*70}\n")

    finally:
        analisador.close()
