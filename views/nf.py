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
nf_bp = Blueprint('nf', __name__)

@nf_bp.route('/nf/list', methods=['GET'])
@token_required
def list_os():
    try:
        initial_date = request.args.get('initial_date', None)
        final_date = request.args.get('final_date', None)
        current_page = request.args.get('current_page', None)
        search = request.args.get('search', None)
        numero_os = request.args.get('numero_os', None)
        limit = request.args.get('limit', None)
        
        context = {}
        context['token_data'] = request.token_data
        context['title'] = "Notas Fiscais"
        
        token = session.get('token')
        params = []
        if initial_date:
            params.append(f'initial_date={initial_date}')
        if final_date:
            params.append(f'final_date={final_date}')
        if current_page:
            params.append(f'current_page={current_page}')
        if search:
            params.append(f'search={search}')
        if numero_os:
            params.append(f'numero_os={numero_os}')
        if limit:
            params.append(f'limit={limit}')
        
        
        query_string = '&'.join(params)
        url = f"https://backend.caiuas.com.br/api/nf/list?{query_string}"
        # return str(url)
        context['current_page'] = f'https://app.caiuas.com.br/nf/list'
        payload = {}
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 204:
            context['token'] = token
            context['status_response'] = response.status_code
            context['data'] = []
            return render_template('nf/list.html', context=context)
        # return (str(url))
        data = response.json()
        context['token'] = token
        context['status_response'] = response.status_code
        context['data'] = data
        return render_template('nf/list.html', context=context)
    except Exception as e:
        # return str(e)
        return render_template('500.html', error=str(e))
    