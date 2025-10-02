from flask import Flask, session, redirect, url_for, render_template, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from database import postgres_chatwoot, postgres_site
from datetime import datetime, timedelta, timezone
from functools import wraps
import bcrypt
from dotenv import load_dotenv
import os
import requests
import json
import pytz
import jwt

load_dotenv()
app = Flask(__name__)

# configura pasta static
app = Flask(__name__, static_url_path='/static', static_folder='static')
app.secret_key = os.environ.get('SECRET_KEY_BASE')
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[]
)

BRAZIL_TZ = pytz.timezone('America/Sao_Paulo')  # UTC-3
def get_brazil_now():
    """Retorna datetime atual no timezone do Brasil"""
    return datetime.now(BRAZIL_TZ)

views_dir = os.path.join(os.path.dirname(__file__), 'views')
for filename in os.listdir(views_dir):
    if filename.endswith('.py') and filename != '__init__.py':
        module_name = filename[:-3]  # Remove a extensão .py
        module = __import__('views.' + module_name, fromlist=['views'])
        blueprint = getattr(module, module_name + '_bp')
        app.register_blueprint(blueprint)


def check_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            token_parts = auth_header.split(' ')
            
            if len(token_parts) == 2 and token_parts[0] == 'Bearer':
                token = token_parts[1]

        if not token:
            return jsonify({'message': 'Usuário não autenticado!'}), 401

        try:
            fuso_horario_offset = timedelta(hours=-3)
            fuso_horario = timezone(fuso_horario_offset)
            token = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
            # print(token)
            data_expiracao = datetime.fromtimestamp(token['exp'])
            agora = datetime.now(fuso_horario).timestamp()
            agora = datetime.fromtimestamp(agora)
            agora = agora.strftime('%Y-%m-%d %H:%M:%S %Z')
            if float(token['exp']) < (datetime.now(fuso_horario).timestamp()):
                return jsonify({'message': 'Token expirado!'}), 401
        except Exception as e:
            # print(e)
            return jsonify({f"message": 'Token Inválido!'}), 401

        setattr(request, 'token_data', token)  # Adiciona os dados decodificados ao objeto request

        return f(*args, **kwargs)

    return decorated

# add 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def access_denied(e):
    return render_template('403.html'), 403

@app.route('/', methods=['GET'])
def home():
    # Checa se o token está na sessão e é válido
    token = session.get('token')
    if not token or not token_valido(token):
        return redirect(url_for('login_page'))  # Corrigido aqui
    return render_template('dashboard.html')

@app.route('/api/webhookwhatsapp', methods=['GET'])
def webhook_verification():
    """
    Verifica o webhook do Facebook.
    """
    VERIFY_TOKEN = "s7b36a716076a5c7e33774842b5c89914"
    # if request.method == 'GET':
        # Extrai os parâmetros da solicitação
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

        # Verifica se o modo e o token estão presentes e são válidos
        # if mode == 'subscribe' and token == VERIFY_TOKEN:
            # Responde com o challenge e um status 200 (OK)
            # print("WEBHOOK_VERIFIED")
    return challenge, 200
        # else:
            # Responde com 403 (Proibido) se a verificação falhar
            # abort(403)

@app.route('/api/webtolead', methods=['POST'])
def post_webtolead():
    try:        
        try:
            payload = request.get_json()
            query = f"""
                insert into form_site(created_at, updated_at, status, body)
                values (now(), now(), 'formulario_valido', '{json.dumps(payload)}')
            """
            # return str(query)
            conn_site, cur_site = postgres_site()
            cur_site.execute(query)
            conn_site.commit()
            url = "https://webto.salesforce.com/servlet/servlet.WebToLead?encoding=UTF-8"
            # payload = f'retURL=https%3A%2F%2Fhondacaiuas.com.br&lead_source=WebSite%20Concession%C3%A1ria&sub_source_media__c=Site&dealer_code_interest__c=1018523&model_interest__c=Accord%20Touring&first_name=Pablo%20Eduardo&last_name=Lima%20Celestino&cpf__c=73141453187&email=pablo%40pabloedu.com&mobile=15988272755&type__c=HAB%20-%20Autom%C3%B3veis&opt_in_email__c=1&opt_in_phone__c=1&oid=00D61000000HSuF&priority=M%C3%A9dia'
            payload_parts = []
            for key, value in payload.items():
                payload_parts.append(f"{key}={value}")
            payload = "&".join(payload_parts)
            headers = {
                    'Content-Type': 'application/x-www-form-urlencoded'
                    }
            response = requests.request("POST", url, headers=headers, data=payload)
            
        except Exception as e:
            query = f"""
                insert into form_site(created_at, updated_at, status)
                values (now(), now(), 'formulario_invalido')
            """
            
            conn_site, cur_site = postgres_site()
            cur_site.execute(query)
            conn_site.commit()
            return json.dumps({'message': 'Invalid JSON payload'}), 400
        
        return json.dumps({'message': 'Form submitted successfully'}), 200
    except Exception as e:
        return json.dumps({'message': str(e)}), 400

@app.route('/api/webtolead', methods=['GET'])
def get_webtolead():
    try:
        retorno = {}
        initial_date = request.args.get('initial_date', None)
        final_date = request.args.get('final_date', None)
        status = request.args.get('status', None)
        current_page = request.args.get('current_page', default=1, type=int)
        search = request.args.get('search', default=None, type=str)
        limit = request.args.get('limit', default=100, type=int)
        
        initial_date = request.args.get('initial_date', type=str, default=None)
        final_date = request.args.get('final_date', type=str, default=None)
        
        conn_site, cur_site = postgres_site()

        filter_search = ''
        if search:
            search = str(search).lower()
            filter_search = f""" and (
                lower(fs2.body::text) like '%{search}%'
            )"""
        
        filter_initial_date = ''
        if initial_date:
            try:
                initial_date = datetime.strptime(initial_date, '%Y-%m-%d')
                filter_initial_date = f"and fs2.created_at::date >= '{initial_date.date()}'"
                filter_initial_date_saldo = f" and fs2.created_at::date < '{initial_date.date()}'"
            except ValueError:
                retorno['message'] = 'Data inicial inválida'
                return jsonify(retorno), 400

        filter_final_date = ''
        if final_date:
            try:
                final_date = datetime.strptime(final_date, '%Y-%m-%d')
                filter_final_date = f"and fs2.created_at::date <= '{final_date.date()}'"
            except ValueError:
                retorno['message'] = 'Data final inválida'
                return jsonify(retorno), 400

        filter_status = ''
        if status:
            status = str(status).lower()
            filter_status = f"and lower(fs2.status) = '{status}'"
        
        offset = (current_page - 1) * limit
        
        query = f"""
            select 
                count(*) as total
            from form_site fs2
            where 1=1
            {filter_status}
            {filter_initial_date}
            {filter_final_date}
            {filter_search}
        """
        # return query
        cur_site.execute(query)

        total_count = cur_site.fetchone()[0]
        if total_count == 0:
            return json.dumps({'message': 'No records found'}), 404
        
        total_pages = (total_count + limit - 1) // limit
        retorno['total_count'] = total_count
        retorno['total_pages'] = total_pages
        retorno['current_page'] = current_page
        retorno['limit'] = limit
        if current_page > total_pages:
            retorno = {}
            retorno['message'] = 'Current page exceeds total pages'
            return jsonify(retorno), 404
        
        query = f"""
            select 
                fs2.id_form_site, 
                fs2.status, 
                fs2.created_at , 
                fs2.updated_at, 
                fs2.body 
            from form_site fs2
            where 1=1
            {filter_status}
            {filter_initial_date}
            {filter_final_date}
            {filter_search}
            order by fs2.created_at desc
            offset {offset} limit {limit}
            
        """
        cur_site.execute(query)
        results = cur_site.fetchall()
        forms = []
        for row in results:
            form = {
                'id_form_site': row['id_form_site'],
                'status': row['status'],
                'created_at': row['created_at'].strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': row['updated_at'].strftime('%Y-%m-%d %H:%M:%S'),
                'body': json.loads(row['body']) if isinstance(row['body'], str) else (row['body'] or {})
            }
            forms.append(form)
        retorno['forms'] = forms
        return jsonify(retorno), 200
            
    except Exception as e:
        return json.dumps({'message': str(e)}), 400

@app.route('/api/webtolead/<int:id_form_site>', methods=['GET'])
def show_get_webtolead(id_form_site):
    try:
        retorno = {}
        conn_site, cur_site = postgres_site()
        
        query = f"""
            select 
                fs2.id_form_site, 
                fs2.status, 
                fs2.created_at , 
                fs2.updated_at, 
                fs2.body 
            from form_site fs2
            where 1=1
                and fs2.id_form_site = {id_form_site}
        """
        cur_site.execute(query)
        results = cur_site.fetchall()
        if cur_site.rowcount == 0:
            return json.dumps({'message': 'No records found'}), 404
        forms = []
        for row in results:
            form = {
                'id_form_site': row['id_form_site'],
                'status': row['status'],
                'created_at': row['created_at'].strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': row['updated_at'].strftime('%Y-%m-%d %H:%M:%S'),
                'body': json.loads(row['body']) if isinstance(row['body'], str) else (row['body'] or {})
            }
            forms.append(form)
        retorno = forms[0]
        return jsonify(retorno), 200
            
    except Exception as e:
        return json.dumps({'message': str(e)}), 400

@app.route('/agendamento', methods=['GET'])
def agendamento():
    token = session.get('token')
    if not token or not token_valido(token):
        return redirect(url_for('login_page'))
    try:
        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d')
        date = request.args.get('date', None)
        cod_empresa = request.args.get('cod_empresa', '11')
        # try:
        #     date = datetime.strptime(date, '%d/%m/%Y') if date else None
        #     if date:
        #         date = date.strftime('%Y-%m-%d')
        # except ValueError:
        #     date = None
        # if date == None:
        #     date = formatted_date
        if date:
            try:
                date = datetime.strptime(date, '%Y-%m-%d')
                date = date.strftime('%Y-%m-%d')
            except ValueError:
                date = None
        else:
            date = formatted_date
            # return str(date)
        
        url = f'https://backend.caiuas.com.br/api/agenda?cod_empresa={cod_empresa}&date={date}'
        # return url
        response = requests.get(url, timeout=10)
        response = response.json()
        agendamentos = response['agendamentos']
        
        
        context = {}
        context['token'] = token
        context['title'] = 'Agendamento de serviços'
        context['date'] = date if date else None
        context['main_menu'] = 'agendamento'
        context['agendamentos'] = agendamentos
        context['parametros'] = response['parametros']
        # return context
        return render_template('agendamento.html', context=context)
    except Exception as e:
        return render_template('500.html', error=str(e))

@app.route('/relatorios', methods=['GET'])
def relatorios():
    token = session.get('token')
    if not token or not token_valido(token):
        return redirect(url_for('login_page'))
    
    context = {}
    context['title'] = 'Relatórios'
    context['main_menu'] = 'relatorios'
    return render_template('relatorios.html', context=context)

@app.route('/relatorios/fechamento_agendamento', methods=['GET'])
def relatorios_fechamento_agendamento():
    token = session.get('token')
    if not token or not token_valido(token):
        return redirect(url_for('login_page'))

    context = {}
    context['title'] = 'Fechamento - CRM Agendamentos'
    context['main_menu'] = 'relatorios'
    return render_template('relatorios/fechamento_agendamento.html', context=context)

@app.route('/relatorios/pesquisa_satisfacao', methods=['GET'])
def relatorios_pesquisa_satisfacao():
    token = session.get('token')
    if not token or not token_valido(token):
        return redirect(url_for('login_page'))

    context = {}
    context['title'] = 'Pesquisa de Satisfação'
    context['main_menu'] = 'relatorios'
    return render_template('relatorios/pesquisa_satisfacao.html', context=context)

@app.route('/relatorios/faturamento_veiculos', methods=['GET'])
def relatorios_faturamento_veiculos():
    token = session.get('token')
    if not token or not token_valido(token):
        return redirect(url_for('login_page'))

    context = {}
    context['title'] = 'Faturamento de Veículos'
    context['main_menu'] = 'relatorios'
    return render_template('relatorios/faturamento_veiculos.html', context=context)

@app.route('/relatorios/estoque_veiculos', methods=['GET'])
def relatorios_estoque_veiculos():
    token = session.get('token')
    if not token or not token_valido(token):
        return redirect(url_for('login_page'))

    context = {}
    context['title'] = 'Estoque de veículos'
    context['main_menu'] = 'relatorios'
    return render_template('relatorios/estoque_veiculos.html', context=context)

@app.route('/veiculos/estoque', methods=['GET'])
def estoque_veiculos():
    token = session.get('token')
    if not token or not token_valido(token):
        return redirect(url_for('login_page'))
    url = "https://backend.caiuas.com.br/api/veiculos/estoque"

    payload = {}
    headers = {
            "Authorization": f"Bearer {token}"
        }

    response = requests.request("GET", url, headers=headers, data=payload)
    
    context = {}
    context['title'] = 'Estoque de veículos'
    context['main_menu'] = 'relatorios'
    context['veiculos'] = response.json()['veiculos']
    context['parametros'] = {'cod_empresa': 11}
    return render_template('veiculos/estoque.html', context=context)

@app.route('/veiculos/aguardando_faturamento', methods=['GET'])
def estoque_aguardando_faturamento():
    token = session.get('token')
    if not token or not token_valido(token):
        return redirect(url_for('login_page'))
    url = "https://backend.caiuas.com.br/api/veiculos/aguardando_faturamento"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    
    context = {}
    context['title'] = 'Estoque aguardando faturamento'
    context['main_menu'] = 'relatorios'
    context['veiculos'] = response.json()['veiculos']
    context['parametros'] = {'cod_empresa': 11}
    return render_template('veiculos/aguardando_faturamento.html', context=context)

@app.route('/veiculos/faturados', methods=['GET'])
def veiculos_faturados():
    try:
        token = session.get('token')
        if not token or not token_valido(token):
            return redirect(url_for('login_page'))
        url = "https://backend.caiuas.com.br/api/veiculos/faturados"
        initial_date = request.args.get('initial_date', None)
        final_date = request.args.get('final_date', None)
        # se initial_date não for enviado é igual a primerio dia do mes e se final_date naõ for enviado, é igual a ultimo dia do mês
        if not initial_date:
            now = datetime.now()
            initial_date = now.replace(day=1).strftime('%Y-%m-%d')
        if not final_date:
            now = datetime.now()
            final_date = now.replace(day=28) + timedelta(days=4)  # Vai para o próximo mês
            final_date = final_date - timedelta(days=final_date.day)  # Volta para o último dia do mês atual
            final_date = final_date.strftime('%Y-%m-%d')
        url = f"{url}?initial_date={initial_date}&final_date={final_date}"

        payload = {}
        headers = {
                "Authorization": f"Bearer {token}"
            }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            context = {}
            context['title'] = 'Veículos faturados'
            context['main_menu'] = 'relatorios'
            context['veiculos'] = response.json()['veiculos']
        
            return render_template('veiculos/faturados.html', context=context)
        else:
            context = {}
            context['title'] = 'Veículos faturados'
            context['main_menu'] = 'relatorios'
            context['veiculos'] = []
            return render_template('veiculos/faturados.html', context=context)
    except Exception as e:
        return render_template('500.html', error=str(e))


@app.route('/forms/form_site', methods=['GET'])
def form_site_veiculos():
    token = session.get('token')
    if not token or not token_valido(token):
        return redirect(url_for('login_page'))

    # Parâmetros de filtro e paginação da URL
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=100, type=int)
    search = request.args.get('search', default=None, type=str)
    initial_date = request.args.get('initial_date', default=None, type=str)
    final_date = request.args.get('final_date', default=None, type=str)
    status = request.args.get('status', default=None, type=str)

    # Constrói a URL da API com os parâmetros
    api_url = f"{request.url_root}api/webtolead"
    params = {
        'current_page': page,
        'limit': limit,
        'search': search,
        'initial_date': initial_date,
        'final_date': final_date,
        'status': status
    }
    # Remove parâmetros nulos para não poluir a URL
    query_params = {k: v for k, v in params.items() if v is not None}

    context = {}
    try:
        response = requests.get(api_url, params=query_params)
        # Verifica se a resposta foi bem-sucedida (status 2xx)
        if response.status_code == 200:
            context = response.json()
        else:
            # Tenta decodificar o JSON de erro, se houver
            try:
                context = response.json()
            except json.JSONDecodeError:
                context = {'message': response.text}

    except requests.exceptions.RequestException as e:
        context = {'message': str(e)}

    # Garante que as chaves de paginação existam no contexto, mesmo em caso de erro ou resposta vazia
    context.setdefault('forms', [])
    context.setdefault('total_count', 0)
    context.setdefault('total_pages', 1)
    context.setdefault('current_page', page)
    context.setdefault('limit', limit)
    
    context['title'] = 'Form Site'
    context['main_menu'] = 'relatorios'
    
    return render_template('form_site.html', context=context, request=request)

@app.route('/forms/form_site/<int:id_form_site>', methods=['GET'])
def show_form_site_veiculos(id_form_site):
    token = session.get('token')
    if not token or not token_valido(token):
        return redirect(url_for('login_page'))
    url = f"{request.url_root}api/webtolead/{id_form_site}"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    
    context = response.json()
    context['title'] = 'Form Site'
    context['main_menu'] = 'relatorios'
    # context['forms'] = response.json()
    # context['parametros'] = {'cod_empresa': 11}
    return render_template('form_site_show.html', context=context)

@app.route('/login', methods=['GET'])
def login_page():
    if 'token' in session:
        session.pop('token', None)
        return redirect(url_for('home'))
    context = {}
    if 'error' in request.args:
        context['error'] = request.args['error']
    return render_template('login.html')
    
@app.route('/login', methods=['POST'])
@limiter.limit("20 per minute")
def login_page_post():
    email = request.form.get('email')
    password = request.form.get('password')
    
    query = f"""
        select name,encrypted_password 
        from users
        where 1=1
            and lower(email) = '{str(email).lower()}'
    """
    conn_chatwoot, cur_chatwoot = postgres_chatwoot()
    cur_chatwoot.execute(query)
    if cur_chatwoot.rowcount == 0:
        return render_template('login.html', error='Usuário não encontrado. Tente novamente.')
    result = cur_chatwoot.fetchone()
    name = result['name']
    password_encripted = result['encrypted_password']
    
    if check_password(password, password_encripted):
        # generate token
        now_brazil = get_brazil_now()
        exp_time = now_brazil + timedelta(days=1)
        payload = {
            "email": email,
            "name": name,
            'exp': int(exp_time.timestamp()),
            'iat': int(now_brazil.timestamp()),
            'nbf': int(now_brazil.timestamp()),
            'iss': os.environ.get('APP_URL'),
        }
        token = jwt.encode(payload, os.environ.get('SECRET_KEY_BASE'), algorithm='HS256')

        session['token'] = token
        session['email'] = email
        return redirect(url_for('home'))
    else:
        return render_template('login.html', error='Senha incorreta! Tente novamente.')

@app.route('/api/login', methods=['POST'])
@limiter.limit("20 per minute")
def api_login():
    data = request.get_json()
    # email = request.form.get('email')
    # password = request.form.get('password')
    email = data.get('email', None)
    password = data.get('password', None)
    if not email or not password:
        retorno = {}
        retorno['message'] = 'Email e senha são obrigatórios.'
        return jsonify(retorno), 400
    retorno = {}
    query = f"""
        select name,encrypted_password 
        from users
        where 1=1
            and lower(email) = '{str(email).lower()}'
    """
    conn_chatwoot, cur_chatwoot = postgres_chatwoot()
    cur_chatwoot.execute(query)
    if cur_chatwoot.rowcount == 0:
        retorno['message'] = 'Usuário não encontrado. Tente novamente.'
        return jsonify(retorno), 404
    result = cur_chatwoot.fetchone()
    name = result['name']
    password_encripted = result['encrypted_password']
    
    if check_password(password, password_encripted):
        # generate token
        now_brazil = get_brazil_now()
        exp_time = now_brazil + timedelta(days=1)
        payload = {
            "email": email,
            "name": name,
            'exp': int(exp_time.timestamp()),
            'iat': int(now_brazil.timestamp()),
            'nbf': int(now_brazil.timestamp()),
            'iss': os.environ.get('APP_URL'),
        }
        token = jwt.encode(payload, os.environ.get('SECRET_KEY_BASE'), algorithm='HS256')

        # session['token'] = token
        # session['email'] = email
        
        retorno['token'] = token
        return jsonify(retorno), 200
    else:
        retorno['message'] = 'Senha incorreta! Tente novamente.'
        return jsonify(retorno), 403

@app.route('/logout')
def logout():
    session.pop('token', None)
    return redirect(url_for('login_page'))

def token_valido(token):
    try:
        if token == 'meutoken':
            session.pop('token', None)
            return redirect(url_for('home'))
        decoded = jwt.decode(token, os.environ.get('SECRET_KEY_BASE'), algorithms=['HS256'], options={"require": ["exp", "iat", "nbf" ]})
        return True
        # Verifica se o emissor é válido
    except jwt.ExpiredSignatureError:
        return False
    return token == 'meutoken'

if __name__ == '__main__':
    # O aplicativo vai escutar em todas as interfaces na porta 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
