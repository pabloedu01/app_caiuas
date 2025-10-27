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
oficina_bp = Blueprint('oficina', __name__)

@oficina_bp.route('/oficina/list_os', methods=['GET'])
@token_required
def list_os():
    try:
        initial_date = request.args.get('initial_date', None)
        final_date = request.args.get('final_date', None)
        current_page = request.args.get('current_page', None)
        search = request.args.get('search', None)
        limit = request.args.get('limit', None)
        
        context = {}
        context['token_data'] = request.token_data
        context['title'] = "Eventos Showroom"
        
        token = session.get('token')
        url = f"https://backend.caiuas.com.br/api/oficina/list_os"
        context['current_page'] = f'https://app.caiuas.com.br/oficina/list_os'
        payload = {}
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        
        data = response.json()
        context['token'] = token
        context['status_response'] = response.status_code
        context['data'] = data
        return render_template('oficina/list_os.html', context=context)
    except Exception as e:
        return render_template('500.html', error=str(e))
    