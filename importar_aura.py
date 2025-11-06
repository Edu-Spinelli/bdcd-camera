"""
Script de Importação para Neo4j Aura
Importa dados coletados da Câmara dos Deputados
"""

import json
import os
from neo4j import GraphDatabase

class ImportadorNeo4jAura:
    """Importa dados JSON para Neo4j Aura"""

    def __init__(self, uri=None, username=None, password=None):
        """Inicializa conexão com Neo4j Aura"""
        # Configurações do seu Neo4j Aura - Instance02
        self.URI = uri or "neo4j+s://2a3ba8da.databases.neo4j.io"
        self.AUTH = (username or "neo4j", password or "N_CdGEmG4OlD7yhMOgsvkkUzHxq7Gi_-5D5kpvcMAV4")  # username, password

        print("Conectando ao Neo4j Aura...")
        self.driver = GraphDatabase.driver(self.URI, auth=self.AUTH)

        # Testar conexão
        try:
            self.driver.verify_connectivity()
            print("✓ Conectado ao Neo4j Aura com sucesso!\n")
        except Exception as e:
            print(f"❌ Erro ao conectar: {str(e)}")
            raise

    def close(self):
        """Fecha conexão"""
        self.driver.close()
        print("\n✓ Conexão fechada")

    def limpar_banco(self):
        """CUIDADO: Remove todos os dados do banco"""
        with self.driver.session() as session:
            print("⚠️  Limpando banco de dados...")
            session.run("MATCH (n) DETACH DELETE n")
            print("✓ Banco limpo\n")

    def carregar_json(self, arquivo):
        """Carrega arquivo JSON"""
        if not os.path.exists(arquivo):
            print(f"  ⚠ Arquivo não encontrado: {arquivo}")
            return []

        with open(arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)

    def criar_constraints(self):
        """Cria constraints e índices"""
        with self.driver.session() as session:
            print("📋 Criando constraints...")

            constraints = [
                "CREATE CONSTRAINT deputado_id IF NOT EXISTS FOR (d:Deputado) REQUIRE d.id IS UNIQUE",
                "CREATE CONSTRAINT partido_id IF NOT EXISTS FOR (p:Partido) REQUIRE p.id IS UNIQUE",
                "CREATE CONSTRAINT frente_id IF NOT EXISTS FOR (f:Frente) REQUIRE f.id IS UNIQUE",
                "CREATE CONSTRAINT uf_sigla IF NOT EXISTS FOR (uf:UF) REQUIRE uf.sigla IS UNIQUE"
            ]

            for constraint in constraints:
                try:
                    session.run(constraint)
                    print(f"  ✓ Constraint criado")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        print(f"  → Constraint já existe")
                    else:
                        print(f"  ⚠ {str(e)}")
            print()

    def criar_ufs(self):
        """Cria nós de UFs brasileiras"""
        print("🗺️  Criando UFs...")

        with self.driver.session() as session:
            query = """
            CREATE
              (uf1:UF {sigla: "AC", nome: "Acre", regiao: "Norte"}),
              (uf2:UF {sigla: "AL", nome: "Alagoas", regiao: "Nordeste"}),
              (uf3:UF {sigla: "AP", nome: "Amapá", regiao: "Norte"}),
              (uf4:UF {sigla: "AM", nome: "Amazonas", regiao: "Norte"}),
              (uf5:UF {sigla: "BA", nome: "Bahia", regiao: "Nordeste"}),
              (uf6:UF {sigla: "CE", nome: "Ceará", regiao: "Nordeste"}),
              (uf7:UF {sigla: "DF", nome: "Distrito Federal", regiao: "Centro-Oeste"}),
              (uf8:UF {sigla: "ES", nome: "Espírito Santo", regiao: "Sudeste"}),
              (uf9:UF {sigla: "GO", nome: "Goiás", regiao: "Centro-Oeste"}),
              (uf10:UF {sigla: "MA", nome: "Maranhão", regiao: "Nordeste"}),
              (uf11:UF {sigla: "MT", nome: "Mato Grosso", regiao: "Centro-Oeste"}),
              (uf12:UF {sigla: "MS", nome: "Mato Grosso do Sul", regiao: "Centro-Oeste"}),
              (uf13:UF {sigla: "MG", nome: "Minas Gerais", regiao: "Sudeste"}),
              (uf14:UF {sigla: "PA", nome: "Pará", regiao: "Norte"}),
              (uf15:UF {sigla: "PB", nome: "Paraíba", regiao: "Nordeste"}),
              (uf16:UF {sigla: "PR", nome: "Paraná", regiao: "Sul"}),
              (uf17:UF {sigla: "PE", nome: "Pernambuco", regiao: "Nordeste"}),
              (uf18:UF {sigla: "PI", nome: "Piauí", regiao: "Nordeste"}),
              (uf19:UF {sigla: "RJ", nome: "Rio de Janeiro", regiao: "Sudeste"}),
              (uf20:UF {sigla: "RN", nome: "Rio Grande do Norte", regiao: "Nordeste"}),
              (uf21:UF {sigla: "RS", nome: "Rio Grande do Sul", regiao: "Sul"}),
              (uf22:UF {sigla: "RO", nome: "Rondônia", regiao: "Norte"}),
              (uf23:UF {sigla: "RR", nome: "Roraima", regiao: "Norte"}),
              (uf24:UF {sigla: "SC", nome: "Santa Catarina", regiao: "Sul"}),
              (uf25:UF {sigla: "SP", nome: "São Paulo", regiao: "Sudeste"}),
              (uf26:UF {sigla: "SE", nome: "Sergipe", regiao: "Nordeste"}),
              (uf27:UF {sigla: "TO", nome: "Tocantins", regiao: "Norte"})
            """
            session.run(query)
            print("✓ 27 UFs criadas\n")

    def importar_partidos(self, arquivo='dados_camara/partidos.json'):
        """Importa partidos"""
        print(f"📋 Importando partidos...")
        partidos = self.carregar_json(arquivo)

        if not partidos:
            return

        with self.driver.session() as session:
            for partido in partidos:
                query = """
                MERGE (p:Partido {id: $id})
                SET p.sigla = $sigla,
                    p.nome = $nome,
                    p.uri = $uri
                """
                session.run(query,
                    id=partido['id'],
                    sigla=partido['sigla'],
                    nome=partido['nome'],
                    uri=partido.get('uri', ''))

            print(f"✓ {len(partidos)} partidos importados\n")

    def importar_deputados(self, arquivo='dados_camara/deputados.json'):
        """Importa deputados"""
        print(f"👤 Importando deputados...")
        deputados = self.carregar_json(arquivo)

        if not deputados:
            return

        with self.driver.session() as session:
            # Importar deputados
            for i, dep in enumerate(deputados, 1):
                query = """
                MERGE (d:Deputado {id: $id})
                SET d.nome = $nome,
                    d.siglaPartido = $siglaPartido,
                    d.siglaUf = $siglaUf,
                    d.urlFoto = $urlFoto,
                    d.email = $email
                """
                session.run(query,
                    id=dep['id'],
                    nome=dep.get('nome', ''),
                    siglaPartido=dep.get('siglaPartido', ''),
                    siglaUf=dep.get('siglaUf', ''),
                    urlFoto=dep.get('urlFoto', ''),
                    email=dep.get('email', ''))

                if i % 100 == 0:
                    print(f"  → {i}/{len(deputados)} deputados processados", end='\r')

            print(f"✓ {len(deputados)} deputados importados" + " "*20)

            # Criar relacionamentos FILIADO_A
            print("  Criando relacionamentos FILIADO_A...")
            query_partido = """
            MATCH (d:Deputado)
            WHERE d.siglaPartido IS NOT NULL AND d.siglaPartido <> ''
            MATCH (p:Partido {sigla: d.siglaPartido})
            MERGE (d)-[:FILIADO_A]->(p)
            """
            result = session.run(query_partido)
            print("  ✓ Relacionamentos FILIADO_A criados")

            # Criar relacionamentos REPRESENTA
            print("  Criando relacionamentos REPRESENTA...")
            query_uf = """
            MATCH (d:Deputado)
            WHERE d.siglaUf IS NOT NULL AND d.siglaUf <> ''
            MATCH (uf:UF {sigla: d.siglaUf})
            MERGE (d)-[:REPRESENTA]->(uf)
            """
            result = session.run(query_uf)
            print("  ✓ Relacionamentos REPRESENTA criados\n")

    def importar_frentes(self, arquivo='dados_camara/frentes.json'):
        """Importa frentes"""
        print(f"🤝 Importando frentes...")
        frentes = self.carregar_json(arquivo)

        if not frentes:
            return

        with self.driver.session() as session:
            for frente in frentes:
                query = """
                MERGE (f:Frente {id: $id})
                SET f.titulo = $titulo,
                    f.idLegislatura = $idLegislatura,
                    f.uri = $uri
                """
                session.run(query,
                    id=frente['id'],
                    titulo=frente.get('titulo', ''),
                    idLegislatura=frente.get('idLegislatura', 0),
                    uri=frente.get('uri', ''))

            print(f"✓ {len(frentes)} frentes importadas\n")

    def importar_membros_frentes(self, arquivo='dados_camara/membros_frentes.json'):
        """Importa relacionamentos deputado-frente"""
        print(f"🔗 Importando membros de frentes...")
        membros = self.carregar_json(arquivo)

        if not membros:
            print("  ⚠ Arquivo não encontrado (execute coleta completa)\n")
            return

        with self.driver.session() as session:
            for membro in membros:
                query = """
                MATCH (d:Deputado {id: $idDeputado})
                MATCH (f:Frente {id: $idFrente})
                MERGE (d)-[r:MEMBRO_DE]->(f)
                SET r.titulo = $titulo
                """
                session.run(query,
                    idDeputado=membro['idDeputado'],
                    idFrente=membro['idFrente'],
                    titulo=membro.get('titulo', 'Membro'))

            print(f"✓ {len(membros)} relacionamentos MEMBRO_DE criados\n")

    def estatisticas(self):
        """Mostra estatísticas do grafo"""
        print("="*70)
        print("📊 ESTATÍSTICAS DO GRAFO")
        print("="*70)

        with self.driver.session() as session:
            # Contar nós
            print("\n📍 Nós:")
            tipos = ["Deputado", "Partido", "Frente", "UF"]
            for tipo in tipos:
                query = f"MATCH (n:{tipo}) RETURN count(n) as count"
                result = session.run(query)
                count = result.single()['count']
                print(f"  • {tipo}: {count:,}")

            # Contar relacionamentos
            print("\n🔗 Relacionamentos:")
            rels = ["FILIADO_A", "REPRESENTA", "MEMBRO_DE"]
            for rel in rels:
                query = f"MATCH ()-[r:{rel}]->() RETURN count(r) as count"
                result = session.run(query)
                count = result.single()['count']
                if count > 0:
                    print(f"  • {rel}: {count:,}")

        print("\n" + "="*70 + "\n")

    def importar_tudo(self):
        """Importa todos os dados disponíveis"""
        print("="*70)
        print("🚀 IMPORTAÇÃO PARA NEO4J AURA")
        print("="*70)
        print()

        self.criar_constraints()
        self.criar_ufs()
        self.importar_partidos()
        self.importar_deputados()
        self.importar_frentes()
        self.importar_membros_frentes()

        self.estatisticas()

        print("✅ IMPORTAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*70)
        print("\n💡 Próximos passos:")
        print("  1. Abra o Neo4j Browser")
        print("  2. Execute: MATCH (n) RETURN n LIMIT 25")
        print("  3. Visualize seu grafo!\n")


if __name__ == "__main__":
    import sys

    try:
        importador = ImportadorNeo4jAura()

        # Limpar banco automaticamente se for passado --limpar
        if '--limpar' in sys.argv or len(sys.argv) == 1:
            importador.limpar_banco()

        # Importar tudo
        importador.importar_tudo()

    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
        print("\nVerifique se:")
        print("  1. Você instalou o driver: pip install neo4j~=5.28.0")
        print("  2. As credenciais estão corretas")
        print("  3. Sua conexão com internet está ativa")
        print("  4. Os arquivos JSON existem em dados_camara/")

    finally:
        try:
            importador.close()
        except:
            pass
