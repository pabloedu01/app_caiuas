import os
import jwt
from functools import wraps
from flask import request, jsonify, render_template, session, redirect, url_for
from datetime import datetime, timedelta, timezone

def token_valido(token):
    try:
        if token == 'meutoken':
            return False
        decoded = jwt.decode(token, os.environ.get('SECRET_KEY_BASE'), algorithms=['HS256'], options={"require": ["exp", "iat", "nbf"]})
        return True
    except jwt.ExpiredSignatureError:
        return False
    except Exception:
        return False

def token_required(f):
    @wraps(f) 
    def decorated(*args, **kwargs):
        # Verifica o token da sessão (como na rota /agendamento)
        token = session.get('token')
        
        if not token or not token_valido(token):
            return redirect(url_for('login_page'))

        try:
            # Decodifica o token para adicionar os dados ao request
            fuso_horario = timezone(timedelta(hours=-3))
            token_data = jwt.decode(token, os.getenv('SECRET_KEY_BASE'), algorithms=["HS256"])
            
            # Verifica a expiração
            if token_data['exp'] < datetime.now(fuso_horario).timestamp():
                return redirect(url_for('login_page'))
        
        except jwt.ExpiredSignatureError:
            return redirect(url_for('login_page'))
        except jwt.InvalidTokenError:
            return redirect(url_for('login_page'))
        except Exception as e:
            return redirect(url_for('login_page'))

        # Adiciona os dados decodificados ao objeto request para uso na rota
        setattr(request, 'token_data', token_data)  

        return f(*args, **kwargs)

    return decorated