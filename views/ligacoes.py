from flask import Blueprint, request, render_template, flash, redirect, url_for
from datetime import datetime
import csv
import io
from auth import token_required
from database import postgres_site

ligacoes_bp = Blueprint('ligacoes', __name__)

ALLOWED_EXTENSIONS = {'csv'}

# Colunas obrigatórias do CSV
COLUNAS_OBRIGATORIAS = [
    'id da chamada',
    'Data/Hora Registro',
    'Data/Hora Início',
    'Bina',
    'Origem',
    'DID',
    'Destino',
    'Duração',
    'Duração em Horas',
    'Status',
    'Tipo',
    'Gravação',
    'Pincode'
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@ligacoes_bp.route('/ligacoes', methods=['GET', 'POST'])
@token_required
def get_ligacoes():
    try:
        if request.method == 'POST':
            if 'csvFile' not in request.files:
                flash('Nenhum arquivo foi enviado', 'error')
                return redirect(request.url)
            
            file = request.files['csvFile']
            
            if file.filename == '':
                flash('Nenhum arquivo foi selecionado', 'error')
                return redirect(request.url)
            
            if file and allowed_file(file.filename):
                # Valida e processa o CSV direto da memória
                try:
                    registros = []
                    erros = []
                    
                    # Lê o arquivo como texto
                    stream = io.StringIO(file.stream.read().decode('utf-8'))
                    
                    # Detecta o delimitador
                    sample = stream.read(1024)
                    stream.seek(0)
                    sniffer = csv.Sniffer()
                    delimiter = sniffer.sniff(sample).delimiter
                    
                    csv_reader = csv.DictReader(stream, delimiter=delimiter)
                    colunas_arquivo_raw = csv_reader.fieldnames
                    
                    # Limpa os nomes das colunas
                    colunas_arquivo = [col.strip().strip('"').strip("'") for col in colunas_arquivo_raw]
                    
                    # Atualiza o reader com colunas limpas
                    stream.seek(0)
                    csv_reader = csv.DictReader(stream, delimiter=delimiter, fieldnames=colunas_arquivo)
                    next(csv_reader)  # Pula o cabeçalho
                    
                    # Informa colunas encontradas
                    colunas_formatadas = '<br>• ' + '<br>• '.join(colunas_arquivo)
                    flash(f'Colunas encontradas no arquivo ({len(colunas_arquivo)}): {colunas_formatadas}', 'info')
                    
                    # Verifica se todas as colunas obrigatórias estão presentes
                    colunas_faltando = [col for col in COLUNAS_OBRIGATORIAS if col not in colunas_arquivo]
                    colunas_extras = [col for col in colunas_arquivo if col not in COLUNAS_OBRIGATORIAS]
                    
                    if colunas_faltando:
                        flash(f'Erro: Colunas faltando no arquivo: <br>• {" <br>• ".join(colunas_faltando)}', 'error')
                        return redirect(request.url)
                    
                    if colunas_extras:
                        flash(f'Aviso: Colunas extras encontradas: <br>• {" <br>• ".join(colunas_extras)}', 'warning')
                    
                    # Processa cada linha do CSV
                    linha_num = 1
                    for row in csv_reader:
                        linha_num += 1
                        
                        # 3º - Valida "id da chamada"
                        id_chamada = row.get('id da chamada', '').strip()
                        if not id_chamada:
                            erros.append(f'Linha {linha_num}: "id da chamada" está vazio')
                            continue
                        
                        # 4º - Converte "Data/Hora Registro" para datetime
                        try:
                            data_hora_registro_str = row.get('Data/Hora Registro', '').strip()
                            if not data_hora_registro_str:
                                erros.append(f'Linha {linha_num}: "Data/Hora Registro" está vazio')
                                continue
                            data_hora_registro = datetime.strptime(data_hora_registro_str, '%Y-%m-%d %H:%M:%S')
                        except ValueError as e:
                            erros.append(f'Linha {linha_num}: Erro ao converter "Data/Hora Registro" ({data_hora_registro_str})')
                            continue
                        
                        # 5º - Converte "Data/Hora Início" para datetime
                        try:
                            data_hora_inicio_str = row.get('Data/Hora Início', '').strip()
                            if not data_hora_inicio_str:
                                erros.append(f'Linha {linha_num}: "Data/Hora Início" está vazio')
                                continue
                            data_hora_inicio = datetime.strptime(data_hora_inicio_str, '%Y-%m-%d %H:%M:%S')
                        except ValueError as e:
                            erros.append(f'Linha {linha_num}: Erro ao converter "Data/Hora Início" ({data_hora_inicio_str})')
                            continue
                        
                        # 6º - Bina (null se vazio)
                        bina = row.get('Bina', '').strip() or None
                        
                        # 7º - Origem (null se vazio)
                        origem = row.get('Origem', '').strip() or None
                        
                        # 8º - DID (null se vazio)
                        did = row.get('DID', '').strip() or None
                        
                        # 9º - Destino (null se vazio)
                        destino = row.get('Destino', '').strip() or None
                        
                        # 10º - Duração (inteiro)
                        try:
                            duracao_str = row.get('Duração', '').strip()
                            duracao = int(duracao_str) if duracao_str else 0
                        except ValueError:
                            erros.append(f'Linha {linha_num}: "Duração" deve ser um número inteiro ({duracao_str})')
                            continue
                        
                        # 11º - Duração em Horas (mantém como está, null se vazio)
                        duracao_horas = row.get('Duração em Horas', '').strip() or None
                        
                        # 12º - Status (mantém o valor)
                        status = row.get('Status', '').strip()
                        
                        # 13º - Tipo (mantém o valor)
                        tipo = row.get('Tipo', '').strip()
                        
                        # 14º - Gravação (null se vazio)
                        gravacao = row.get('Gravação', '').strip() or None
                        # se final do arquivo não for .WAV é NOne
                        if gravacao and not gravacao.upper().endswith('.WAV'):
                            gravacao = None
                        
                        # 15º - Pincode (null se vazio)
                        pincode = row.get('Pincode', '').strip() or None
                        
                        # Adiciona o registro processado à lista
                        registros.append({
                            'id_chamada': id_chamada,
                            'data_hora_registro': data_hora_registro,
                            'data_hora_inicio': data_hora_inicio,
                            'bina': bina,
                            'origem': origem,
                            'did': did,
                            'destino': destino,
                            'duracao': duracao,
                            'duracao_horas': duracao_horas,
                            'status': status,
                            'tipo': tipo,
                            'gravacao': gravacao,
                            'pincode': pincode
                        })
                    
                    # Verifica se houve erros
                    if erros:
                        flash(f'Erros encontrados ({len(erros)}): <br>• {" <br>• ".join(erros[:10])}{"<br>... e mais " + str(len(erros) - 10) + " erros" if len(erros) > 10 else ""}', 'error')
                        return redirect(request.url)
                    
                    # Insere registros no banco de dados
                    if registros:
                        try:
                            conn, cur = postgres_site()
                            registros_inseridos = 0
                            
                            for reg in registros:
                                sql = """
                                    INSERT INTO voip 
                                    (uniqueid, calldate, start_date, bina, origem, destino, direcao, status, 
                                     canal, canal2, tempo_atendimento, tempo_total, created_at, status_audio, url_audio_operadora)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    on conflict (uniqueid, calldate, start_date, bina, origem, destino, direcao, canal, canal2, tempo_atendimento, tempo_total, url_audio_operadora) do nothing
                                """
                                values = (
                                    reg['id_chamada'],
                                    reg['data_hora_registro'],
                                    reg['data_hora_inicio'],
                                    reg['bina'],
                                    reg['origem'],
                                    reg['destino'],
                                    reg['tipo'],
                                    reg['status'],
                                    reg['origem'],
                                    reg['destino'],
                                    reg['duracao'],
                                    reg['duracao'],
                                    datetime.now(),
                                    None,
                                    reg['gravacao']
                                )
                                
                                cur.execute(sql, values)
                                registros_inseridos += 1
                            
                            conn.commit()
                            cur.close()
                            conn.close()
                            
                            flash(f'✓ Sucesso! {registros_inseridos} registros inseridos no banco de dados.', 'success')
                            
                        except Exception as e:
                            if 'conn' in locals():
                                conn.rollback()
                                cur.close()
                                conn.close()
                            
                            # Monta mensagem detalhada com SQL e valores
                            error_msg = f'Erro ao inserir no banco de dados: {str(e)}<br><br>'
                            error_msg += f'<strong>SQL:</strong><br>{sql}<br><br>'
                            error_msg += f'<strong>Valores:</strong><br>{values}'
                            
                            flash(error_msg, 'error')
                            return redirect(request.url)
                    else:
                        flash('Nenhum registro encontrado para inserir.', 'warning')
                    
                    return redirect(url_for('ligacoes.get_ligacoes'))
                    
                except Exception as e:
                    flash(f'Erro ao processar arquivo: {str(e)}', 'error')
                    return redirect(request.url)
            else:
                flash('Tipo de arquivo inválido. Apenas arquivos CSV são permitidos.', 'error')
                return redirect(request.url)
        
        return render_template('ligacoes.html')
            
    except Exception as e:
        return render_template('500.html', error=str(e))
    