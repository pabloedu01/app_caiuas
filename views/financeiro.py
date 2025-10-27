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
        initial_date = request.args.get('initial_date', None)
        final_date = request.args.get('final_date', None)
        current_page = request.args.get('current_page', None)
        search = request.args.get('search', None)
        limit = request.args.get('limit', None)
        
        context = {}
        context['token_data'] = request.token_data
        context['title'] = "Lançamentos de Contas"
        
        token = session.get('token')

        url = f"https://backend.caiuas.com.br/api/financeiro/lcontas{f'?search={search}' if search else '?'}{f'&limit={limit}' if limit else ''}{f'&current_page={current_page}' if current_page else ''}{f'&initial_date={initial_date}' if initial_date else ''}{f'&final_date={final_date}' if final_date else ''}"
        payload = {}
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        
        data = response.json()
        context['token'] = token
        context['status_response'] = response.status_code
        context['data'] = data
        return render_template('financeiro/lcontas.html', context=context)
    except Exception as e:
        return render_template('500.html', error=str(e))
    