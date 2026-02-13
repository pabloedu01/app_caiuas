from flask import Blueprint, jsonify, request
from database import postgres_site
from datetime import datetime
import os
import uuid
import boto3
from botocore.config import Config # Importante para assinatura v4
from dotenv import load_dotenv

load_dotenv()

files_bp = Blueprint('files', __name__)

@files_bp.route('/api/files/generate_presigned_url', methods=['POST'])
# @token_required # Descomente se for usar autenticação
def generate_presigned_url():
    try:
        # 1. Captura os dados
        file_name = request.json.get('file_name')
        file_size = request.json.get('file_size')
        file_type = request.json.get('file_type') # Recebe ex: "image/png"

        # Validações básicas
        if not file_name:
            return jsonify({"error": "file_name is required"}), 400
        
        # 2. Tratamento do Content-Type (O PULO DO GATO)
        # Se não vier tipo, usamos binário genérico.
        # JAMAIS formate isso como string "'content-type': ...", use o valor puro.
        if not file_type:
            file_type = 'application/octet-stream'

        # 3. Prepara o caminho do arquivo
        uuid_str = str(uuid.uuid4())
        now = datetime.now()
        date_path = now.strftime("%Y/%m/%d")
        # Nome final no S3
        full_file_name = f"{date_path}/{uuid_str}"

        # 4. Configura o Cliente S3 com Assinatura v4
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name='sa-east-1',
            config=Config(signature_version='s3v4') # Força padrão seguro
        )

        # 5. Gera a URL Assinada
        # O 'ContentType' aqui deve ser EXATAMENTE igual ao header do frontend
        presigned_url = s3.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': 'processos-caiuas', 
                'Key': full_file_name, 
                'ContentType': file_type 
            },
            ExpiresIn=3600
        )
        
        print(f"DEBUG - Gerado URL para: {full_file_name} | Tipo: {file_type}")

        return jsonify({
            "presigned_url": presigned_url,
            "key": full_file_name # Útil retornar a chave para salvar no banco depois
        }), 200

    except Exception as e:
        print(f"ERRO: {e}")
        return jsonify({"error": str(e)}), 500
    
@files_bp.route('/api/files/register_file', methods=['POST'])
# @token_required # Descomente se for usar autenticação
def register_file():
    try:
        # 1. Captura os dados
        file_key = request.json.get('file_key') # A chave gerada no S3 (ex: "2024/06/10/uuid")
        file_name = request.json.get('file_name') # O nome original do arquivo (ex: "foto.png")
        file_type = request.json.get('file_type') # O tipo do arquivo (ex: "image/png")
        file_size = request.json.get('file_size') # O tamanho do arquivo em bytes

        # Validações básicas
        if not file_key or not file_name or not file_type:
            return jsonify({"error": "file_key, file_name and file_type are required"}), 400

        # 2. Aqui você pode salvar as informações no banco de dados
        # Exemplo: Salvar na tabela 'files' com colunas (id, key, name, type, created_at)
        # db.execute("INSERT INTO files (key, name, type) VALUES (%s, %s, %s)", (file_key, file_name, file_type))
        
        query = f"""
            insert into files (filename, url, file_size, old_filename, created_at) values (
                '{file_key}', 
                'https://processos-caiuas.s3.sa-east-1.amazonaws.com/{file_key}', 
                {file_size}, 
                '{file_name}', 
                now()
            )
            RETURNING id_file
        """
        conn, cursor = postgres_site()
        cursor.execute(query)
        id_file = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        retorno = {}
        retorno['id_file'] = id_file
        retorno['filename'] = file_key
        retorno['url'] = f'https://processos-caiuas.s3.sa-east-1.amazonaws.com/{file_key}'
        retorno['file_size'] = file_size
        retorno['old_filename'] = file_name
        retorno['created_at'] = datetime.now().isoformat()
        retorno['message'] = "File registered successfully"

        print(f"DEBUG - Registrado arquivo: {file_key} | Nome: {file_name} | Tipo: {file_type}")

        return jsonify(retorno), 200

    except Exception as e:
        print(f"ERRO: {e}")
        return jsonify({"error": str(e)}), 500
    