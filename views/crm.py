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
crm_bp = Blueprint('crm', __name__)

@crm_bp.route('/crm/eventos_showroom', methods=['GET'])
@token_required
def eventos_showroom():
    try:
        status = request.args.get('status', None)
        initial_date = request.args.get('initial_date', None)
        final_date = request.args.get('final_date', None)
        current_page = request.args.get('current_page', None)
        search = request.args.get('search', None)
        limit = request.args.get('limit', None)

        context = {}
        context['token_data'] = request.token_data
        context['title'] = "Eventos Showroom"
        
        token = session.get('token')

        url = f"https://backend.caiuas.com.br/api/crm/eventos?&tipo_evento=785,787,793,795,797,799{f'&search={search}' if search else ''}{f'&status={status}' if status else ''}{f'&limit={limit}' if limit else ''}{f'&current_page={current_page}' if current_page else ''}{f'&initial_date={initial_date}' if initial_date else ''}{f'&final_date={final_date}' if final_date else ''}{f'&search={search}' if search else ''}"
        context['current_page'] = f'https://app.caiuas.com.br/crm/eventos?&tipo_evento=785,787,793,795,797,799{f'&search={search}' if search else ''}{f'&status={status}' if status else ''}{f'&limit={limit}' if limit else ''}{f'&current_page={current_page}' if current_page else ''}{f'&initial_date={initial_date}' if initial_date else ''}{f'&final_date={final_date}' if final_date else ''}{f'&search={search}' if search else ''}'
        payload = {}
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        
        data = response.json()
        context['token'] = token
        context['status_response'] = response.status_code
        context['data'] = data
        return render_template('crm/eventos_showroom.html', context=context)
    except Exception as e:
        return render_template('500.html', error=str(e))

@crm_bp.route('/crm/eventos', methods=['GET'])
@token_required
def eventos():
    try:
        status = request.args.get('status', None)
        initial_date = request.args.get('initial_date', None)
        final_date = request.args.get('final_date', None)
        current_page = request.args.get('current_page', None)
        search = request.args.get('search', None)
        limit = request.args.get('limit', None)

        context = {}
        context['token_data'] = request.token_data
        context['title'] = "Eventos Showroom"
        
        token = session.get('token')

        url = f"https://backend.caiuas.com.br/api/crm/eventos?&{f'&search={search}' if search else ''}{f'&status={status}' if status else ''}{f'&limit={limit}' if limit else ''}{f'&current_page={current_page}' if current_page else ''}{f'&initial_date={initial_date}' if initial_date else ''}{f'&final_date={final_date}' if final_date else ''}{f'&search={search}' if search else ''}"
        context['current_page'] = f'https://app.caiuas.com.br/crm/eventos?&{f'&search={search}' if search else ''}{f'&status={status}' if status else ''}{f'&limit={limit}' if limit else ''}{f'&current_page={current_page}' if current_page else ''}{f'&initial_date={initial_date}' if initial_date else ''}{f'&final_date={final_date}' if final_date else ''}{f'&search={search}' if search else ''}'
        payload = {}
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        
        data = response.json()
        context['token'] = token
        context['status_response'] = response.status_code
        context['data'] = data
        return render_template('crm/eventos.html', context=context)
    except Exception as e:
        return render_template('500.html', error=str(e))


@crm_bp.route('/crm/eventos_showroom/<int:evento_id>', methods=['GET'])
@token_required
def show_eventos_showroom(evento_id):
    try:
        previous_page = request.args.get('previous_page', None)

        context = {}
        context['token_data'] = request.token_data
        context['title'] = "Detalhes do Evento Showroom"
        
        token = session.get('token')

        url = f"https://backend.caiuas.com.br/api/crm/eventos_showroom/{evento_id}"
        payload = {}
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            
            data = response.json()
            context['status_response'] = response.status_code
            context['data'] = data
            context['previous_page'] = previous_page
            return render_template('crm/eventos_showroom_detalhes.html', context=context)
        if response.status_code == 404:
            return render_template('404.html'), 404
        else:
            return render_template('500.html', error="Erro ao buscar detalhes do evento.")
    except Exception as e:
        return render_template('500.html', error=str(e))
    
@crm_bp.route('/crm/pesquisa_satisfacao', methods=['GET'])
@token_required
def list_pesquisa_satisfacao():
    try:
        status = request.args.get('status', None)
        initial_date = request.args.get('initial_date', None)
        final_date = request.args.get('final_date', None)
        current_page = request.args.get('current_page', None)
        search = request.args.get('search', None)
        limit = request.args.get('limit', None)

        context = {}
        context['token_data'] = request.token_data
        context['title'] = "Pesquisa de Satisfação"
        
        token = session.get('token')

        url = f"https://backend.caiuas.com.br/api/crm/eventos?&tipo_evento=38,180,30,22{f'&search={search}' if search else ''}{f'&status={status}' if status else ''}{f'&limit={limit}' if limit else ''}{f'&current_page={current_page}' if current_page else ''}{f'&initial_date={initial_date}' if initial_date else ''}{f'&final_date={final_date}' if final_date else ''}{f'&search={search}' if search else ''}"
        context['current_page'] = f'https://app.caiuas.com.br/crm/eventos?&tipo_evento=38,180,30,22{f'&search={search}' if search else ''}{f'&status={status}' if status else ''}{f'&limit={limit}' if limit else ''}{f'&current_page={current_page}' if current_page else ''}{f'&initial_date={initial_date}' if initial_date else ''}{f'&final_date={final_date}' if final_date else ''}{f'&search={search}' if search else ''}'
        payload = {}
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        
        data = response.json()
        context['token'] = token
        context['status_response'] = response.status_code
        context['data'] = data
        return render_template('crm/pesquisa_satisfacao.html', context=context)
    except Exception as e:
        return render_template('500.html', error=str(e))