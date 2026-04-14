from flask import Blueprint, jsonify, request, render_template, session, redirect
from datetime import datetime, timedelta
from database import postgres_chatwoot, postgres_site
import json
import os
import requests
from dotenv import load_dotenv
import tempfile
import urllib.request
import urllib.parse
import secrets
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
        created_at_min = request.args.get('created_at_min', None)
        created_at_max = request.args.get('created_at_max', None)
        limit = request.args.get('limit', None)

        context = {}
        context['token_data'] = request.token_data
        context['title'] = "Eventos Showroom"
        
        token = session.get('token')

        url = f"https://backend.caiuas.com.br/api/crm/eventos?&tipo_evento=785,787,793,795,797,799{f'&search={search}' if search else ''}{f'&status={status}' if status else ''}{f'&limit={limit}' if limit else ''}{f'&current_page={current_page}' if current_page else ''}{f'&initial_date={initial_date}' if initial_date else ''}{f'&final_date={final_date}' if final_date else ''}{f'&created_at_min={created_at_min}' if created_at_min else ''}{f'&created_at_max={created_at_max}' if created_at_max else ''}"
        context['current_page'] = f'https://app.caiuas.com.br/crm/eventos?&tipo_evento=785,787,793,795,797,799{f'&search={search}' if search else ''}{f'&status={status}' if status else ''}{f'&limit={limit}' if limit else ''}{f'&current_page={current_page}' if current_page else ''}{f'&initial_date={initial_date}' if initial_date else ''}{f'&final_date={final_date}' if final_date else ''}{f'&created_at_min={created_at_min}' if created_at_min else ''}{f'&created_at_max={created_at_max}' if created_at_max else ''}'
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
        tipo_evento = request.args.get('tipo_evento', None)
        cod_empresa = request.args.get('cod_empresa', None)
        search = request.args.get('search', None)
        responsible = request.args.get('responsible', None)
        limit = request.args.get('limit', None)
        created_at_min = request.args.get('created_at_min', None)
        created_at_max = request.args.get('created_at_max', None)

        token = session.get('token')

        url = f"https://backend.caiuas.com.br/api/crm/responsaveis"
        payload = {}
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        responsaveis_response = response.json()
        # Trata o retorno da API - busca a chave 'responsaveis' se existir
        users = responsaveis_response.get('responsaveis', []) if isinstance(responsaveis_response, dict) else responsaveis_response if isinstance(responsaveis_response, list) else []

        context = {}
        context['token_data'] = request.token_data
        context['title'] = "Eventos Showroom"

        url = f"https://backend.caiuas.com.br/api/crm/eventos?&{f'&search={search}' if search else ''}{f'&status={status}' if status else ''}{f'&limit={limit}' if limit else ''}{f'&current_page={current_page}' if current_page else ''}{f'&initial_date={initial_date}' if initial_date else ''}{f'&final_date={final_date}' if final_date else ''}{f'&tipo_evento={tipo_evento}' if tipo_evento else ''}{f'&responsible={responsible}' if responsible else ''}{f'&cod_empresa={cod_empresa}' if cod_empresa else ''}{f'&created_at_min={created_at_min}' if created_at_min else ''}{f'&created_at_max={created_at_max}' if created_at_max else ''}"
        context['current_page'] = f'https://app.caiuas.com.br/crm/eventos?&{f'&search={search}' if search else ''}{f'&status={status}' if status else ''}{f'&limit={limit}' if limit else ''}{f'&current_page={current_page}' if current_page else ''}{f'&initial_date={initial_date}' if initial_date else ''}{f'&final_date={final_date}' if final_date else ''}{f'&tipo_evento={tipo_evento}' if tipo_evento else ''}{f'&responsible={responsible}' if responsible else ''}{f'&cod_empresa={cod_empresa}' if cod_empresa else ''}{f'&created_at_min={created_at_min}' if created_at_min else ''}{f'&created_at_max={created_at_max}' if created_at_max else ''}'
        payload = {}
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        
        data = response.json()
        
        url = f"https://backend.caiuas.com.br/api/crm/eventos_tipo"
        payload = {}
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data_tipo_evento = response.json()
        context['data_tipo_evento'] = data_tipo_evento
        context['users'] = users
        
        context['token'] = token
        context['status_response'] = response.status_code
        context['data'] = data
        return render_template('crm/eventos.html', context=context)
    except Exception as e:
        return render_template('500.html', error=str(e))

@crm_bp.route('/crm/eventos_descartados', methods=['GET'])
@token_required
def eventos_descartados():
    try:
        context = {}
        context['token_data'] = request.token_data
        context['title'] = "Eventos Descartados"

        token = session.get('token')

        url = "https://backend.caiuas.com.br/api/crm/eventos_descartados"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.request("GET", url, headers=headers, data={})

        data = response.json()
        context['token'] = token
        context['status_response'] = response.status_code
        context['data'] = data
        return render_template('crm/eventos_descartados.html', context=context)
    except Exception as e:
        return render_template('500.html', error=str(e))

@crm_bp.route('/crm/eventos/<int:evento_id>', methods=['GET'])
@token_required
def show_eventos(evento_id):
    try:
        previous_page = request.args.get('previous_page', None)

        context = {}
        context['token_data'] = request.token_data
        context['title'] = "Detalhes do Evento Showroom"
        
        token = session.get('token')

        url = f"https://backend.caiuas.com.br/api/crm/eventos/{evento_id}"
        payload = {}
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            url_responsaveis = f"https://backend.caiuas.com.br/api/crm/responsaveis"
            payload = {}
            headers = {
                "Authorization": f"Bearer {token}"
            }
            response_responsaveis = requests.request("GET", url_responsaveis, headers=headers, data=payload)
            responsaveis_response = response_responsaveis.json()
            # Trata o retorno da API - busca a chave 'responsaveis' se existir
            users = responsaveis_response.get('responsaveis', []) if isinstance(responsaveis_response, dict) else responsaveis_response if isinstance(responsaveis_response, list) else []
            data = response.json()
            context['status_response'] = response.status_code
            context['data'] = data
            context['users'] = users
            context['previous_page'] = previous_page
            return render_template('crm/eventos_detalhes.html', context=context)
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
    
@crm_bp.route('/crm/open_whatsapp', methods=['POST'])
def open_whatsapp():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON inválido ou ausente'}), 400

        url = data.get('url')
        phone = data.get('phone', '')
        cod_atendimento = data.get('cod_atendimento')

        if not url:
            return jsonify({'error': 'O campo "url" é obrigatório'}), 400

        conn, cur = postgres_chatwoot()
        try:
            # Gera hash único de ~8 caracteres
            for _ in range(10):
                hash_code = secrets.token_urlsafe(6)  # 6 bytes → 8 chars base64url
                cur.execute("SELECT id FROM whatsapp_links WHERE hash = %s", (hash_code,))
                if cur.fetchone() is None:
                    break
            else:
                return jsonify({'error': 'Não foi possível gerar um hash único'}), 500

            cur.execute(
                "INSERT INTO whatsapp_links (hash, url, phone, cod_atendimento) VALUES (%s, %s, %s, %s)",
                (hash_code, url, phone, cod_atendimento)
            )
            conn.commit()
        finally:
            cur.close()
            conn.close()

        short_url = f"https://app.caiuas.com.br/r/{hash_code}"
        message = f"Atendimento #{hash_code}: Olá, gostaria de dar continuidade a meu atendimento por aqui!"
        whatsapp_url = f"https://api.whatsapp.com/send?phone={phone}&text={urllib.parse.quote(message)}"

        return jsonify({
            'whatsapp_url': whatsapp_url,
            'short_url': short_url,
            'hash': hash_code,
            'cod_atendimento': cod_atendimento
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@crm_bp.route('/r/<string:hash_code>', methods=['GET'])
def redirect_whatsapp_link(hash_code):
    try:
        conn, cur = postgres_chatwoot()
        try:
            cur.execute("SELECT url FROM whatsapp_links WHERE hash = %s", (hash_code,))
            row = cur.fetchone()
        finally:
            cur.close()
            conn.close()

        if row is None:
            return render_template('404.html'), 404

        return redirect(row['url'], code=302)
    except Exception as e:
        return render_template('500.html', error=str(e))

@crm_bp.route('/crm/delete', methods=['GET'])
@token_required
def delete_eventos_page():
    try:
        context = {}
        context['token_data'] = request.token_data
        context['title'] = "Deletar Eventos em Massa"
        
        token = session.get('token')
        context['token'] = token
        
        return render_template('crm/delete.html', context=context)
    except Exception as e:
        return render_template('500.html', error=str(e))

@crm_bp.route('/crm/descartar', methods=['GET'])
@token_required
def descartar_eventos_page():
    try:
        context = {}
        context['token_data'] = request.token_data
        context['title'] = "Descartar Eventos em Massa"
        
        token = session.get('token')
        context['token'] = token
        
        return render_template('crm/descartar.html', context=context)
    except Exception as e:
        return render_template('500.html', error=str(e))

@crm_bp.route('/crm/contato_perdido', methods=['GET'])
@token_required
def contato_perdido_page():
    try:
        context = {}
        context['token_data'] = request.token_data
        context['title'] = "Contato Perdido em Massa"
        
        token = session.get('token')
        context['token'] = token
        
        return render_template('crm/contato_perdido.html', context=context)
    except Exception as e:
        return render_template('500.html', error=str(e))
