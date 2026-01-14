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
veiculos_bp = Blueprint('veiculos', __name__)

@veiculos_bp.route('/veiculos/produtos', methods=['GET'])
@token_required
def list_veiculos_produtos():
    try:
        search = request.args.get('search', None)
        current_page = request.args.get('current_page', None)
        limit = request.args.get('limit', None)
        
        context = {}
        context['token_data'] = request.token_data
        context['title'] = "Cadastro de Veículos"
        token = session.get('token')
        
        url = f"https://backend.caiuas.com.br/api/veiculos/produtos?{f'&search={search}' if search else ''}{f'&limit={limit}' if limit else ''}{f'&current_page={current_page}' if current_page else ''}"
        context['current_page'] = f'https://backend.caiuas.com.br/api/veiculos/produtos?{f'&search={search}' if search else ''}{f'&limit={limit}' if limit else ''}{f'&current_page={current_page}' if current_page else ''}'
        payload = {}
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        
        data = response.json()
        
        context['token'] = token
        context['status_response'] = response.status_code
        context['data'] = data
        # return context
        return render_template('veiculos/produtos.html', context=context)
    except Exception as e:
        return render_template('500.html', error=str(e))

@veiculos_bp.route('/veiculos/produtos/<int:cod_modelo>', methods=['GET'])
@token_required
def show_veiculos_produtos(cod_modelo):
    try:
        search = request.args.get('search', None)
        current_page = request.args.get('current_page', None)
        limit = request.args.get('limit', None)
        
        context = {}
        context['token_data'] = request.token_data
        context['title'] = "Atualização de veículo"
        token = session.get('token')
        
        
        url = f"https://backend.caiuas.com.br/api/veiculos/produtos/{cod_modelo}"
        payload = {}
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        
        data = response.json()
        
        context['token'] = token
        context['status_response'] = response.status_code
        context['data'] = data
        # return context
        return render_template('veiculos/show_produtos.html', context=context)
    except Exception as e:
        return render_template('500.html', error=str(e))
    
@veiculos_bp.route('/veiculos/processos', methods=['GET'])
@token_required
def list_veiculos_processos():
    try:
        search = request.args.get('search', None)
        current_page = request.args.get('current_page', None)
        limit = request.args.get('limit', None)
        
        context = {}
        context['token_data'] = request.token_data
        context['title'] = "Processos"
        token = session.get('token')
        
        url = f"https://backend.caiuas.com.br/api/veiculos/processos?{f'&search={search}' if search else ''}{f'&limit={limit}' if limit else ''}{f'&current_page={current_page}' if current_page else ''}"
        context['current_page'] = f'https://backend.caiuas.com.br/api/veiculos/processos?{f'&search={search}' if search else ''}{f'&limit={limit}' if limit else ''}{f'&current_page={current_page}' if current_page else ''}'
        payload = {}
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        
        # Tratar resposta vazia ou sem conteúdo
        if response.status_code == 204 or not response.text:
            data = {'processos': [], 'total': 0}
        else:
            data = response.json()
        
        context['token'] = token
        context['status_response'] = response.status_code
        context['data'] = data
        context['processos'] = data.get('processos', []) if isinstance(data, dict) else []
        context['total'] = data.get('total', 0) if isinstance(data, dict) else 0
        # return context
        return render_template('veiculos/processos.html', context=context)
    except Exception as e:
        return render_template('500.html', error=str(e))