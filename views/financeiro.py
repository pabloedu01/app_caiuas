from flask import Blueprint, jsonify, request, render_template, session
from datetime import datetime, timedelta
from database import postgres_chatwoot, postgres_site
import json
import os
import requests
from dotenv import load_dotenv
import tempfile
import urllib.request
from auth import token_required

load_dotenv()
financeiro_bp = Blueprint('financeiro', __name__)
@financeiro_bp.route('/financeiro/lcontas', methods=['GET'])
@token_required
def list_lcontas():
    try:
        # Capturar todos os parâmetros da URL
        initial_date = request.args.get('initial_date', None)
        final_date = request.args.get('final_date', None)
        current_page = request.args.get('current_page', None)
        search = request.args.get('search', None)
        limit = request.args.get('limit', None)
        consiliado = request.args.get('consiliado', None)
        
        context = {}
        context['token_data'] = request.token_data
        context['title'] = "Lançamentos de Contas"
        
        token = session.get('token')
        headers = {
            "Authorization": f"Bearer {token}"
        }

        # Construir URL de forma mais limpa
        base_url = "https://backend.caiuas.com.br/api/financeiro/lcontas"
        params = []
        
        if search:
            params.append(f"search={search}")
        if limit:
            params.append(f"limit={limit}")
        if current_page:
            params.append(f"current_page={current_page}")
        if initial_date:
            params.append(f"initial_date={initial_date}")
        if final_date:
            params.append(f"final_date={final_date}")
        if consiliado:
            params.append(f"consiliado={consiliado}")
        
        url = base_url + ("?" + "&".join(params) if params else "")
        
        payload = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        
        data = response.json()
        
        # Buscar dados auxiliares para os selects do modal
        try:
            # Buscar empresas
            empresas_response = requests.get("https://backend.caiuas.com.br/api/empresas", headers=headers)
            if empresas_response.status_code == 200:
                data['empresas'] = empresas_response.json().get('data', [])
            
            # Buscar centros de custo
            centros_response = requests.get("https://backend.caiuas.com.br/api/centros_custo", headers=headers)
            if centros_response.status_code == 200:
                data['centros_custo'] = centros_response.json().get('data', [])
            
            # Buscar classificações
            classificacoes_response = requests.get("https://backend.caiuas.com.br/api/classificacoes", headers=headers)
            if classificacoes_response.status_code == 200:
                data['classificacoes'] = classificacoes_response.json().get('data', [])
            
        except Exception as e:
            print(f"Erro ao buscar dados auxiliares: {e}")
            # Se não conseguir buscar, inicializa arrays vazios
            data['empresas'] = []
            data['centros_custo'] = []
            data['classificacoes'] = []
        
        context['token'] = token
        context['status_response'] = response.status_code
        context['data'] = data
        return render_template('financeiro/lcontas.html', context=context)
    except Exception as e:
        return render_template('500.html', error=str(e))
    