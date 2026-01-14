from flask import Blueprint, jsonify, request, render_template, session
import google.generativeai as genai
from datetime import datetime, timedelta
from database import postgres_chatwoot, postgres_site
import json
import os
import requests
from dotenv import load_dotenv
import tempfile
import urllib.request
import bcrypt

load_dotenv()
login_bp = Blueprint('login', __name__)

@login_bp.route('/api/login/change_password', methods=['POST'])
def change_password():
    try:
        data = request.json
        email = data.get('email') if data else None
        password = data.get('password') if data else None
        if not email or not password:
            return jsonify({"status": "error", "message": "Email and password are required"}), 400
        email = email.strip().lower()
        conn, cur = postgres_chatwoot()
        
        query = f"""
            select id from users where uid = '{email}';
        """
        cur.execute(query)
        if cur.rowcount == 0:
            return jsonify({"status": "error", "message": "User not found"}), 404
        user_id = cur.fetchone()[0]
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        senha_hashed = bcrypt.hashpw(password_bytes, salt)
        str_password = senha_hashed.decode('utf-8')
        query = f"""
            update users set encrypted_password = '{str_password}', reset_password_token = NULL, reset_password_sent_at = NULL, confirmed_at = NOW() where id = {user_id};
        """
        cur.execute(query)
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "success", "message": "Password changed successfully"}), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": "Invalid JSON format"}), 400
    