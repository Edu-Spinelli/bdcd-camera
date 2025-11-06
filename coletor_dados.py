import requests
import json
import time
from datetime import datetime
from typing import List, Dict, Optional
import os

class ColetorDadosCamara:
    """
    Classe para coletar dados da API da Câmara dos Deputados
    """

    def __init__(self, output_dir='dados_camara'):
        self.base_url = "https://dadosabertos.camara.leg.br/api/v2"
        self.headers = {'accept': 'application/json'}
        self.output_dir = output_dir
        self.request_count = 0
        self.max_requests_per_minute = 100

        # Criar diretório de saída se não existir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"✓ Diretório '{output_dir}' criado")

    def _rate_limit(self):
        """Controla rate limiting das requisições"""
        self.request_count += 1
        if self.request_count % self.max_requests_per_minute == 0:
            print("⏸  Rate limit: aguardando 60 segundos...")
            time.sleep(60)
        else:
            time.sleep(0.5)  # Pequeno delay entre requisições

    def _fazer_requisicao(self, url, params=None, max_retries=3):
        """Faz requisição com retry automático"""
        for tentativa in range(max_retries):
            try:
                self._rate_limit()
                response = requests.get(url, headers=self.headers, params=params, timeout=30)

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Too many requests
                    print(f"⚠ Rate limit atingido, aguardando 60 segundos...")
                    time.sleep(60)
                    continue
                else:
                    if tentativa == 0:  # Só mostra URL na primeira tentativa
                        print(f"⚠ Status code {response.status_code} - URL: {response.url}")
                    else:
                        print(f"⚠ Status code {response.status_code} na tentativa {tentativa + 1}")

            except requests.exceptions.RequestException as e:
                print(f"⚠ Erro na tentativa {tentativa + 1}: {str(e)}")
                if tentativa < max_retries - 1:
                    time.sleep(5)
                    continue

        return None

    def _paginar_requisicao(self, url, params=None, max_items=None):
        """Faz paginação automática de requisições"""
        todos_dados = []
        pagina = 1

        if params is None:
            params = {}

        params['itens'] = 100  # Tamanho da página

        while True:
            params['pagina'] = pagina
            print(f"  → Coletando página {pagina}...", end='\r')

            data = self._fazer_requisicao(url, params)

            if not data or 'dados' not in data:
                break

            dados_pagina = data['dados']

            if not dados_pagina:
                break

            todos_dados.extend(dados_pagina)

            if max_items and len(todos_dados) >= max_items:
                todos_dados = todos_dados[:max_items]
                break

            # Verificar se há mais páginas
            links = data.get('links', [])
            tem_proxima = any(link.get('rel') == 'next' for link in links)

            if not tem_proxima:
                break

            pagina += 1

        print(f"  ✓ {len(todos_dados)} itens coletados" + " " * 20)
        return todos_dados
        
    def get_partidos(self, data_inicio="2019-01-01", data_fim="2024-12-31"):
        """
        Coleta dados de partidos
        """
        print(f"\n📋 Coletando partidos...")
        url = f"{self.base_url}/partidos"
        params = {
            'dataInicio': data_inicio,
            'dataFim': data_fim,
            'ordem': 'ASC',
            'ordenarPor': 'sigla'
        }

        partidos = self._paginar_requisicao(url, params)
        print(f"✓ {len(partidos)} partidos coletados")
        return partidos
    
    def get_deputados(self, data_inicio="2019-01-01", data_fim="2024-12-31"):
        """
        Coleta dados básicos de deputados
        """
        print(f"\n👤 Coletando deputados...")
        url = f"{self.base_url}/deputados"
        params = {
            'dataInicio': data_inicio,
            'dataFim': data_fim,
            'ordem': 'ASC',
            'ordenarPor': 'nome'
        }

        deputados = self._paginar_requisicao(url, params)
        print(f"✓ {len(deputados)} deputados coletados")
        return deputados

    def get_detalhes_deputado(self, id_deputado):
        """
        Coleta informações detalhadas de um deputado específico
        """
        url = f"{self.base_url}/deputados/{id_deputado}"
        data = self._fazer_requisicao(url)
        return data.get('dados', {}) if data else {}
    
    def get_frentes(self, legislatura=None):
        """
        Coleta dados de frentes parlamentares
        Se legislatura não especificada, coleta todas as legislaturas
        """
        print(f"\n🤝 Coletando frentes parlamentares...")
        url = f"{self.base_url}/frentes"
        params = {}  # API de frentes não aceita ordenação

        frentes = self._paginar_requisicao(url, params)

        # Filtrar por legislatura se especificado
        if legislatura:
            frentes = [f for f in frentes if f.get('idLegislatura') == legislatura]
            print(f"✓ {len(frentes)} frentes coletadas (legislatura {legislatura})")
        else:
            print(f"✓ {len(frentes)} frentes coletadas (todas as legislaturas)")

        return frentes

    def get_membros_frente(self, id_frente):
        """
        Coleta membros de uma frente específica
        """
        url = f"{self.base_url}/frentes/{id_frente}/membros"
        data = self._fazer_requisicao(url)
        return data.get('dados', []) if data else []
    
    def get_proposicoes(self, data_inicio="2019-01-01", data_fim="2024-12-31", max_items=5000):
        """
        Coleta dados de proposições (limitado para não sobrecarregar)
        """
        print(f"\n📜 Coletando proposições (max: {max_items})...")
        url = f"{self.base_url}/proposicoes"
        params = {
            'dataInicio': data_inicio,
            'dataFim': data_fim,
            'ordem': 'DESC',
            'ordenarPor': 'id'
        }

        proposicoes = self._paginar_requisicao(url, params, max_items=max_items)
        print(f"✓ {len(proposicoes)} proposições coletadas")
        return proposicoes

    def get_autores_proposicao(self, id_proposicao):
        """
        Coleta autores de uma proposição específica
        """
        url = f"{self.base_url}/proposicoes/{id_proposicao}/autores"
        data = self._fazer_requisicao(url)
        return data.get('dados', []) if data else []

    def get_votacoes_proposicao(self, id_proposicao):
        """
        Coleta votações de uma proposição específica
        """
        url = f"{self.base_url}/proposicoes/{id_proposicao}/votacoes"
        data = self._fazer_requisicao(url)
        return data.get('dados', []) if data else []

    def get_votacoes(self, data_inicio="2019-01-01", data_fim="2024-12-31", max_items=1000):
        """
        Coleta votações diretamente
        """
        print(f"\n🗳️  Coletando votações (max: {max_items})...")
        url = f"{self.base_url}/votacoes"
        params = {
            'dataInicio': data_inicio,
            'dataFim': data_fim,
            'ordem': 'DESC',
            'ordenarPor': 'dataHoraRegistro'
        }

        votacoes = self._paginar_requisicao(url, params, max_items=max_items)
        print(f"✓ {len(votacoes)} votações coletadas")
        return votacoes

    def get_votos_votacao(self, id_votacao):
        """
        Coleta votos de uma votação específica
        """
        url = f"{self.base_url}/votacoes/{id_votacao}/votos"
        data = self._fazer_requisicao(url)
        return data.get('dados', []) if data else []
    
    def get_orgaos(self):
        """
        Coleta dados de órgãos (comissões, etc)
        """
        print(f"\n🏛️  Coletando órgãos/comissões...")
        url = f"{self.base_url}/orgaos"
        params = {
            'ordem': 'ASC',
            'ordenarPor': 'id'
        }

        orgaos = self._paginar_requisicao(url, params)
        print(f"✓ {len(orgaos)} órgãos coletados")
        return orgaos

    def get_membros_orgao(self, id_orgao):
        """
        Coleta membros de um órgão específico
        """
        url = f"{self.base_url}/orgaos/{id_orgao}/membros"
        data = self._fazer_requisicao(url)
        return data.get('dados', []) if data else []

    def salvar_json(self, dados, nome_arquivo):
        """
        Salva dados em arquivo JSON
        """
        caminho_completo = os.path.join(self.output_dir, nome_arquivo)
        with open(caminho_completo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        print(f"  ✓ Dados salvos em {caminho_completo}")

    def coletar_dados_completos(self, incluir_detalhes_deputados=True,
                                 incluir_membros_frentes=True,
                                 incluir_autores_proposicoes=True,
                                 incluir_votos_votacoes=True,
                                 max_proposicoes=3000,
                                 max_votacoes=500):
        """
        Coleta todos os dados necessários para a análise
        """
        print("\n" + "="*70)
        print("🚀 COLETA COMPLETA DE DADOS - CÂMARA DOS DEPUTADOS")
        print("="*70)

        dados = {}

        # 1. Partidos
        dados['partidos'] = self.get_partidos()
        self.salvar_json(dados['partidos'], 'partidos.json')

        # 2. Deputados básicos
        dados['deputados'] = self.get_deputados()
        self.salvar_json(dados['deputados'], 'deputados.json')

        # 3. Detalhes de deputados (opcional, mas recomendado)
        if incluir_detalhes_deputados:
            print(f"\n📊 Coletando detalhes de {len(dados['deputados'])} deputados...")
            deputados_detalhados = []
            for i, dep in enumerate(dados['deputados'], 1):
                print(f"  → Deputado {i}/{len(dados['deputados'])}: {dep.get('nome', 'N/A')[:30]}", end='\r')
                detalhes = self.get_detalhes_deputado(dep['id'])
                if detalhes:
                    deputados_detalhados.append(detalhes)

            print(f"\n  ✓ {len(deputados_detalhados)} deputados detalhados coletados" + " "*30)
            dados['deputados_detalhados'] = deputados_detalhados
            self.salvar_json(deputados_detalhados, 'deputados_detalhados.json')

        # 4. Frentes Parlamentares
        dados['frentes'] = self.get_frentes()
        self.salvar_json(dados['frentes'], 'frentes.json')

        # 5. Membros de Frentes (relacionamento importante)
        if incluir_membros_frentes and dados['frentes']:
            print(f"\n🔗 Coletando membros de {len(dados['frentes'])} frentes...")
            membros_frentes = []
            for i, frente in enumerate(dados['frentes'], 1):
                print(f"  → Frente {i}/{len(dados['frentes'])}: {frente.get('titulo', 'N/A')[:40]}", end='\r')
                membros = self.get_membros_frente(frente['id'])
                for membro in membros:
                    membros_frentes.append({
                        'idFrente': frente['id'],
                        'tituloFrente': frente.get('titulo'),
                        'idDeputado': membro.get('id'),
                        'nomeDeputado': membro.get('nome'),
                        'titulo': membro.get('titulo', 'Membro')
                    })

            print(f"\n  ✓ {len(membros_frentes)} membros de frentes coletados" + " "*30)
            dados['membros_frentes'] = membros_frentes
            self.salvar_json(membros_frentes, 'membros_frentes.json')

        # 6. Proposições
        dados['proposicoes'] = self.get_proposicoes(max_items=max_proposicoes)
        self.salvar_json(dados['proposicoes'], 'proposicoes.json')

        # 7. Autores de Proposições
        if incluir_autores_proposicoes and dados['proposicoes']:
            print(f"\n✍️  Coletando autores de {len(dados['proposicoes'])} proposições...")
            autores_proposicoes = []
            for i, prop in enumerate(dados['proposicoes'], 1):
                print(f"  → Proposição {i}/{len(dados['proposicoes'])}: {prop.get('id')}", end='\r')
                autores = self.get_autores_proposicao(prop['id'])
                for autor in autores:
                    autores_proposicoes.append({
                        'idProposicao': prop['id'],
                        'tipoProposicao': prop.get('siglaTipo'),
                        'idAutor': autor.get('id'),
                        'nomeAutor': autor.get('nome'),
                        'tipo': autor.get('tipo'),
                        'uriAutor': autor.get('uri')
                    })

            print(f"\n  ✓ {len(autores_proposicoes)} autores de proposições coletados" + " "*30)
            dados['autores_proposicoes'] = autores_proposicoes
            self.salvar_json(autores_proposicoes, 'autores_proposicoes.json')

        # 8. Votações
        dados['votacoes'] = self.get_votacoes(max_items=max_votacoes)
        self.salvar_json(dados['votacoes'], 'votacoes.json')

        # 9. Votos individuais (MUITOS DADOS!)
        if incluir_votos_votacoes and dados['votacoes']:
            print(f"\n🗳️  Coletando votos de {len(dados['votacoes'])} votações...")
            todos_votos = []
            for i, votacao in enumerate(dados['votacoes'], 1):
                id_votacao = votacao.get('id')
                print(f"  → Votação {i}/{len(dados['votacoes'])}: ID {id_votacao}", end='\r')
                votos = self.get_votos_votacao(id_votacao)
                for voto in votos:
                    todos_votos.append({
                        'idVotacao': id_votacao,
                        'dataVotacao': votacao.get('data'),
                        'idDeputado': voto.get('deputado_', {}).get('id'),
                        'nomeDeputado': voto.get('deputado_', {}).get('nome'),
                        'siglaPartido': voto.get('deputado_', {}).get('siglaPartido'),
                        'siglaUf': voto.get('deputado_', {}).get('siglaUf'),
                        'voto': voto.get('tipoVoto')
                    })

            print(f"\n  ✓ {len(todos_votos)} votos individuais coletados" + " "*30)
            dados['votos'] = todos_votos
            self.salvar_json(todos_votos, 'votos.json')

        # 10. Órgãos/Comissões
        dados['orgaos'] = self.get_orgaos()
        self.salvar_json(dados['orgaos'], 'orgaos.json')

        # Resumo final
        print("\n" + "="*70)
        print("✅ COLETA CONCLUÍDA COM SUCESSO!")
        print("="*70)
        print(f"\n📊 RESUMO DOS DADOS COLETADOS:")
        print(f"  • Partidos: {len(dados.get('partidos', []))}")
        print(f"  • Deputados: {len(dados.get('deputados', []))}")
        if 'deputados_detalhados' in dados:
            print(f"  • Deputados (detalhados): {len(dados['deputados_detalhados'])}")
        print(f"  • Frentes Parlamentares: {len(dados.get('frentes', []))}")
        if 'membros_frentes' in dados:
            print(f"  • Membros de Frentes: {len(dados['membros_frentes'])}")
        print(f"  • Proposições: {len(dados.get('proposicoes', []))}")
        if 'autores_proposicoes' in dados:
            print(f"  • Autores de Proposições: {len(dados['autores_proposicoes'])}")
        print(f"  • Votações: {len(dados.get('votacoes', []))}")
        if 'votos' in dados:
            print(f"  • Votos Individuais: {len(dados['votos'])}")
        print(f"  • Órgãos/Comissões: {len(dados.get('orgaos', []))}")
        print(f"\n💾 Todos os arquivos salvos em: {self.output_dir}/")
        print("="*70 + "\n")

        return dados


# Script principal
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Coletor de Dados da Câmara dos Deputados')
    parser.add_argument('--modo', choices=['completo', 'teste', 'rapido'],
                        default='completo',
                        help='Modo de coleta: completo (tudo), teste (poucos dados), rapido (sem detalhes)')
    parser.add_argument('--output', default='dados_camara',
                        help='Diretório de saída dos arquivos JSON')
    parser.add_argument('--max-proposicoes', type=int, default=3000,
                        help='Número máximo de proposições a coletar')
    parser.add_argument('--max-votacoes', type=int, default=500,
                        help='Número máximo de votações a coletar')

    args = parser.parse_args()

    # Criar instância do coletor
    coletor = ColetorDadosCamara(output_dir=args.output)

    if args.modo == 'teste':
        # Modo teste: coleta rápida para verificar se tudo funciona
        print("\n🧪 MODO TESTE - Coleta mínima de dados")
        print("="*70)
        partidos = coletor.get_partidos()
        coletor.salvar_json(partidos, 'partidos.json')

        deputados = coletor.get_deputados()[:10]  # Apenas 10
        coletor.salvar_json(deputados, 'deputados_teste.json')

        frentes = coletor.get_frentes()[:5]  # Apenas 5
        coletor.salvar_json(frentes, 'frentes_teste.json')

        print("\n✅ Teste concluído! Verifique os arquivos no diretório", args.output)

    elif args.modo == 'rapido':
        # Modo rápido: sem detalhes extras
        coletor.coletar_dados_completos(
            incluir_detalhes_deputados=False,
            incluir_membros_frentes=True,
            incluir_autores_proposicoes=True,
            incluir_votos_votacoes=True,
            max_proposicoes=args.max_proposicoes,
            max_votacoes=args.max_votacoes
        )

    else:
        # Modo completo: tudo!
        coletor.coletar_dados_completos(
            incluir_detalhes_deputados=True,
            incluir_membros_frentes=True,
            incluir_autores_proposicoes=True,
            incluir_votos_votacoes=True,
            max_proposicoes=args.max_proposicoes,
            max_votacoes=args.max_votacoes
        )