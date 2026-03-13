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

load_dotenv()
chat_bp = Blueprint('chat', __name__)    

def download_audio_file(url, headers=None):
    """Baixa arquivo de áudio da URL"""
    try:
        req = urllib.request.Request(url, headers=headers or {})
        with urllib.request.urlopen(req) as response:
            # Cria arquivo temporário
            with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as temp_file:
                temp_file.write(response.read())
                return temp_file.name
    except Exception as e:
        print(f"Erro ao baixar áudio: {e}")
        return None

@chat_bp.route('/api/chat', methods=['POST'])
def chat_api():
    try:
        data = request.get_json()
        now = datetime.now() - timedelta(hours=3)
        now_iso = now.isoformat()
        conn_site, cur_site = postgres_site()
        now = datetime.now() - timedelta(hours=3)
        GOOGLE_API_KEY = os.getenv("GOOGLE_AI_STUDIO_KEY")
        genai.configure(api_key=GOOGLE_API_KEY)
        
        
        numeros_teste = [
            # '+5515988272755', # Pablo
            '+5515991057976', # Marcelo
            '+5515991286831', # Andrea
            '+5515991549353',  # Doca
            '+5515988140625',  # Mario
            '+5515991550164'
        ]
        
        # system_instruction = """
        #     **1. PERSONA E IDENTIDADE**

        #     * **Seu nome é Paulo.** Você é um assistente virtual e sua função é a de recepcionista digital da Concessionária Honda Honda Caiuás.
        #     * **Seu tom de voz é profissional, cordial e muito prestativo.** Você deve ser paciente e claro em suas explicações, como se fosse o primeiro contato de um cliente com a nossa empresa.
        #     * **Seu objetivo principal** é ajudar os clientes com dúvidas sobre os produtos e serviços da Honda Automóveis, qualificá-los e direcioná-los para o departamento correto.
        #     * **Você pode processar mensagens de texto e áudio.** Quando receber áudio, responda naturalmente como se fosse uma conversa falada.

        #     **2. CONTEXTO E ESCOPO DE ATUAÇÃO**

        #     * Você trabalha para uma concessionária autorizada Honda.
        #     * **Seu conhecimento é estritamente limitado aos produtos e serviços relacionados à marca HONDA AUTOMÓVEIS.**
        #     * Você **DEVE** recusar educadamente qualquer pergunta que não esteja relacionada a este escopo.

        #     **3. PROCESSAMENTO DE ÁUDIO**
        #     * Quando receber uma mensagem de áudio, ouça com atenção e responda normalmente.
        #     * Se não conseguir entender claramente o áudio, peça educadamente para repetir.
        #     * Mantenha o mesmo tom profissional e cordial, seja para texto ou áudio.

        #     **4. PRODUTOS E SERVIÇOS AUTORIZADOS PARA DISCUSSÃO**

        #     Você está autorizado a fornecer informações sobre:

        #     * **a) Venda de Veículos Novos Honda:**
        #         * Modelos disponíveis (CR-V, ZR-V, Accord, Civic, Civic Type-R, New City, New City Hatchback, HR-V).
        #         * Versões, preços sugeridos e principais características de cada modelo.
        #         * Disponibilidade de test-drive e como agendá-lo.
        #         * Informações sobre financiamento e consórcio (de forma geral, direcionando para um vendedor).

        #     * **b) Venda de Veículos Seminovos:**
        #         * Você pode informar que a concessionária trabalha com veículos seminovos de diversas marcas.
        #         * **IMPORTANTE:** Você não deve fornecer detalhes técnicos ou comparar modelos de outras marcas.

        #     * **c) Venda de Peças Genuínas Honda:**
        #         * Confirmar se temos um departamento de peças.
        #         * Explicar a importância de usar peças genuínas Honda.
        #         * Ajudar o cliente a solicitar um orçamento.

        #     * **d) Serviços de Oficina Honda:**
        #         * Agendamento de revisões periódicas.
        #         * Orçamentos para manutenções.
        #         * Informações sobre garantia e serviços cobertos.

        #     **5. REGRAS DE COMPORTAMENTO**

        #     * **Saudação Inicial:** Sempre comece a conversa se apresentando.
        #     * **Para transferir para atendente:** Sempre colete nome completo e email primeiro.
        #     * **Horário de atendimento:** Segunda a sexta das 08:00 às 18:00.

        #     **6. QUANDO USAR A FERRAMENTA forward_to_agent:**
        #     - APENAS após coletar nome completo e email do cliente
        #     - Cliente se recusa a fornecer dados E insiste em falar com atendente
        #     - Após 2 tentativas sem sucesso de resolver uma dúvida
        #     - Quando cliente solicitar agendamento de serviços
        # """
        # system_instruction = {
        #     "persona_e_identidade": {
        #         "nome": "Paulo",
        #         "descricao": "Assistente virtual e recepcionista digital da Concessionária Honda Honda Caiuás.",
        #         "tom_de_voz": [
        #             "profissional",
        #             "cordial",
        #             "muito prestativo",
        #             "paciente",
        #             "claro nas explicações"
        #         ],
        #         "objetivo_principal": "Ajudar os clientes com dúvidas sobre os produtos e serviços da Honda Automóveis, qualificá-los e direcioná-los para o departamento correto.",
        #         "capacidades": [
        #             "processar mensagens de texto",
        #             "processar mensagens de áudio"
        #         ]
        #     },
        #     "contexto_e_escopo": {
        #         "local": "Concessionária autorizada Honda.",
        #         "escopo_de_conhecimento": "Produtos e serviços relacionados à marca HONDA AUTOMÓVEIS.",
        #         "regra_fora_de_escopo": "Deve recusar educadamente qualquer pergunta que não esteja relacionada a este escopo."
        #     },
        #     "processamento_de_audio": {
        #         "instrucoes": [
        #             "Ao receber uma mensagem de áudio, ouvir com atenção e responder normalmente.",
        #             "Se não conseguir entender claramente o áudio, pedir educadamente para repetir.",
        #             "Manter o mesmo tom profissional e cordial, seja para texto ou áudio."
        #         ]
        #     },
        #     "produtos_e_servicos_autorizados": {
        #         "venda_veiculos_novos": {
        #             "descricao": "Informações sobre a venda de veículos novos da marca Honda.",
        #             "modelos_disponiveis": [
        #                 "CR-V", "ZR-V", "Accord", "Civic", "Civic Type-R",
        #                 "New City", "New City Hatchback", "HR-V"
        #             ],
        #             "informacoes_fornecidas": [
        #                 "Versões, preços sugeridos e principais características de cada modelo.",
        #                 "Disponibilidade de test-drive e como agendá-lo.",
        #                 "Informações gerais sobre financiamento e consórcio (direcionando para um vendedor)."
        #             ]
        #         },
        #         "venda_veiculos_seminovos": {
        #             "descricao": "A concessionária trabalha com veículos seminovos de diversas marcas.",
        #             "restricao_importante": "Não fornecer detalhes técnicos ou comparar modelos de outras marcas."
        #         },
        #         "venda_pecas_genuinas_honda": {
        #             "acoes_permitidas": [
        #                 "Confirmar a existência de um departamento de peças.",
        #                 "Explicar a importância de usar peças genuínas Honda.",
        #                 "Ajudar o cliente a solicitar um orçamento."
        #             ]
        #         },
        #         "servicos_de_oficina_honda": {
        #             "acoes_permitidas": [
        #                 "Agendamento de revisões periódicas.",
        #                 "Orçamentos para manutenções.",
        #                 "Informações sobre garantia e serviços cobertos."
        #             ]
        #         }
        #     },
        #     "regras_de_comportamento": {
        #         "saudacao_inicial": "Sempre começar a conversa se apresentando.",
        #         "procedimento_transferencia": "Sempre coletar nome completo e email do cliente antes de transferir.",
        #         "horario_atendimento": "Segunda a sexta das 08:00 às 18:00."
        #     },
        #     "regras_de_ferramentas": {
        #         "forward_to_agent": {
        #             "condicoes_de_uso": [
        #                 "APENAS após coletar nome completo e email do cliente.",
        #                 "Cliente se recusa a fornecer dados E insiste em falar com atendente.",
        #                 "Após 2 tentativas sem sucesso de resolver uma dúvida.",
        #                 "Quando cliente solicitar agendamento de serviços."
        #             ]
        #         }
        #     }
        # }
        
        query = f"""
            select json_instructions, json_controller  
            from chatbots
            where id_chatbot = 1
        """
        cur_site.execute(query)
        r = cur_site.fetchone()
        if len(r) == 0:
            retorno = {
                'message': 'Chat data not processed due to conditions not met.'
            }
            return jsonify(retorno), 200
        system_instruction = r[0]
        controller = r[1]
        if controller != None or controller != '':
            system_instruction['controller_tools'] = controller
        cur_site.close()
        conn_site.close()
        


        def parts_information(question: str):
            """Consulta informações como preço e outras informações sobre peças e acessórios de veículos."""
            if 'kit1' in question.lower():
                return {
                    "status": "success",
                    "price": 20.0,
                    "kit_name": "Kit Básico para lubrificação",
                    "cod_item": "kit1",
                    "aplicacao": "Lubrificação de peças móveis",
                    "outras_informacoes": "Para mais informações, é necessário falar com um atendente sobre o assunto para mais detalhamentos.",
                    "message": "O kit1 é um kit básico para lubrificação, ideal para iniciantes. Inclui graxa e óleo lubrificante."
                }
            else:
                return {
                    "status": "error",
                    "message": f"Não foi possível obter informações sobre '{question}', talvez o código do item esteja incorreto."
                }

        def forward_to_agent(user_query: str):
            """Encaminha a conversa para um atendente humano quando o cliente solicita especificamente falar com um vendedor, consultor ou atendente humano."""
            # Extrair account_id e conversation_id dos dados recebidos
            account_id = data['inbox_id']  # Usando inbox_id como account_id
            conversation_id = data['id']
            
            url = f"https://chat.caiuas.com.br/api/v1/accounts/{account_id}/conversations/{conversation_id}/assignments"
            payload = {
                "assignee_id": 1
            }
            headers = {
                "api_access_token": os.environ.get("CHATWOOT_TOKEN"),
                "Content-Type": "application/json"
            }
            atendente_name = 'Pablo'
            
            try:
                response = requests.post(url, json=payload, headers=headers)
                print(f"[LOG: Encaminhando para atendente. Motivo: '{user_query}'] - Status: {response.status_code}")
                return {
                    "status": "success",
                    "message": f"Perfeito! Transferi nossa conversa para o atendente {atendente_name} que irá te ajudar pessoalmente. Aguarde um momento que ele já estará disponível para continuar o atendimento."
                }
            except Exception as e:
                print(f"[ERRO ao encaminhar para atendente: {str(e)}]")
                return {
                    "status": "error",
                    "message": f"Anoto seus dados e um atendente entrará em contato em breve. Dados: {user_query}"
                }
            
        available_tools = {
            "parts_information": parts_information,
            "forward_to_agent": forward_to_agent,
        }
        
        model = genai.GenerativeModel(
            model_name='gemini-2.0-flash-exp',  # Usa a versão mais recente que suporta áudio
            system_instruction=json.dumps(system_instruction, ensure_ascii=False),
            tools=list(available_tools.values())
        )
        
        def run_conversation_gemini(conversation_history, user_message_parts):
            """Executa um turno da conversa gerenciando o histórico."""
            
            # Adiciona a mensagem do usuário ao histórico (pode ser texto ou áudio)
            conversation_history.append({'role': 'user', 'parts': user_message_parts})

            # Faz a primeira chamada à API com o histórico completo
            response = model.generate_content(conversation_history)
            response_part = response.candidates[0].content.parts[0]
            
            # Adiciona a resposta do modelo ao histórico
            conversation_history.append({'role': 'model', 'parts': [response_part]})
            
            # Verifica se o modelo quer chamar uma função
            if hasattr(response_part, 'function_call'):
                print(response_part)
                function_call = response_part.function_call
                function_name = function_call.name
                
                if function_name in available_tools:
                    function_to_call = available_tools[function_name]
                    function_args = {key: value for key, value in function_call.args.items()}
                    
                    # Executa a função real
                    function_response_data = function_to_call(**function_args)
                    
                    # Adiciona o resultado da função ao histórico
                    conversation_history.append({
                        'role': 'function',
                        'parts': [{
                            'function_response': {
                                'name': function_name,
                                'response': function_response_data,
                            }
                        }]
                    })
                    
                    # Envia o histórico atualizado de volta ao modelo para a resposta final
                    second_response = model.generate_content(conversation_history)
                    final_text = second_response.text
                    
                    # Adiciona a resposta final do assistente ao histórico
                    conversation_history.append({'role': 'model', 'parts': [{'text': final_text}]})
                    return final_text.strip()
                else:
                    return response.text.strip()
                    
            # Se não houve chamada de função, retorna o texto diretamente
            return response.text.strip()
        
        if data['meta']['sender']['phone_number'] in numeros_teste and data['messages'][0]['message_type']== 0:
            inbox_id = data['inbox_id']
            contact_id = data['contact_inbox']['contact_id']
            conversation_id = data['id']
            sender = data['meta']['sender']['phone_number']
            user_message = data['messages'][0]['content']
            
            with open(f'log/chat_{now_iso}.json', 'w') as f:
                f.write(json.dumps(data, indent=4, ensure_ascii=False))
            
            # Prepara as partes da mensagem (texto ou áudio)
            user_message_parts = []
            
            # Verifica se há conteúdo de texto
            if user_message:
                user_message_parts.append({'text': user_message})
            
            # Verifica se há anexos de áudio
            elif data['messages'][0]['content'] is None and 'attachments' in data['messages'][0]:
                # Processa anexos de áudio
                for attachment in data['messages'][0]['attachments']:
                    if attachment['file_type'] == 'audio':
                        print(f"Processando áudio: {attachment}")
                        
                        # Monta URL completa do áudio
                        audio_url = f"https://chat.caiuas.com.br{attachment['data_url']}"
                        
                        # Headers para autenticação no Chatwoot
                        headers = {
                            'api_access_token': os.getenv("CHATWOOT_TOKEN")
                        }
                        
                        # Baixa o arquivo de áudio
                        audio_path = download_audio_file(audio_url, headers)
                        
                        if audio_path:
                            try:
                                # Carrega o arquivo de áudio para o Gemini
                                audio_file = genai.upload_file(audio_path)
                                with open('log/chat_audio.log', 'a') as log_file:
                                    log_file.write(f"Áudio carregado: {audio_file.name}\n")
                                # Adiciona o áudio às partes da mensagem
                                user_message_parts.append(audio_file)
                                
                                print(f"Áudio carregado com sucesso: {audio_file.name}")
                                
                                # Remove arquivo temporário
                                os.unlink(audio_path)
                                
                            except Exception as e:
                                print(f"Erro ao processar áudio: {e}")
                                user_message_parts.append({
                                    'text': "Desculpe, houve um problema ao processar seu áudio. Poderia tentar novamente ou enviar uma mensagem escrita?"
                                })
                        else:
                            user_message_parts.append({
                                'text': "Desculpe, não consegui acessar seu áudio. Poderia tentar novamente?"
                            })
                        
                        break  # Processa apenas o primeiro áudio
                        
            else:
                # Se não há conteúdo nem áudio, envia mensagem padrão
                user_message_parts.append({
                    'text': "Desculpe, não consegui processar sua mensagem. Poderia tentar novamente?"
                })
            
            # Se não há partes da mensagem, pula o processamento
            if not user_message_parts:
                return jsonify({
                    'message': 'No message content to process.'
                }), 200
                        
            # Busca histórico de mensagens do banco
            conn, cur = postgres_chatwoot()
            
            query = f"""
            select 
                cw.phone_number,
                m.content, 
                case
                    when m.sender_type = 'Contact'
                    then 'user'
                    else 'model'
                end sender_type,
                asb.key, 
                asb.filename, 
                asb.content_type 
            from messages m
            left join attachments a on 1=1
                and m.id = a.message_id
            left join active_storage_attachments asa on 1=1
                and asa.record_id = a.id 
            left join active_storage_blobs asb on 1=1
                and asb.id = asa.blob_id 
            left join inboxes i on 1=1
                and i.id = m.inbox_id
            left join channel_whatsapp cw on 1=1
                and i.channel_id = cw.id 
            where 1=1
            and m.inbox_id = '{inbox_id}'
            and m.conversation_id = '{conversation_id}'
            order by m.id
            """
            
            cur.execute(query)
            mensagens = cur.fetchall()
            
            # Converte o histórico do banco para o formato do Gemini
            conversation_history = []
            for mensagem in mensagens:
                if mensagem[1] is not None:
                    role = 'user' if mensagem[2] == 'user' else 'model'
                    conversation_history.append({
                        'role': role,
                        'parts': [{'text': mensagem[1]}]
                    })
            
            cur.close()
            conn.close()
            
            # Gera resposta usando o Gemini
            gemini_response = run_conversation_gemini(conversation_history, user_message_parts)
            
            # Envia a resposta de volta para o Chatwoot
            url = f"https://chat.caiuas.com.br/api/v1/accounts/{inbox_id}/conversations/{conversation_id}/messages"
            
            payload = json.dumps({
                'content': gemini_response,
            })
            
            headers = {
                'api_access_token': f'{os.getenv("CHATWOOT_TOKEN")}',
                'Content-Type': 'application/json'
            }
            
            response = requests.request("POST", url, headers=headers, data=payload)
            
            retorno = {
                'chatwoot_response_status': response.status_code,
                'message': 'Chat processed and response sent.'
            }
            return jsonify(retorno), 200
        else:
            retorno = {
                'message': 'Chat data not processed due to conditions not met.'
            }
            return jsonify(retorno), 200
            
    except Exception as e:
        retorno = {
            'error': str(e)
        }
        with open(f'log/error_chat_{now_iso}.json', 'w') as f:
            f.write(json.dumps(retorno, indent=4, ensure_ascii=False))
        return jsonify(retorno), 400

@chat_bp.route('/api/chat_corretora', methods=['POST'])
def chat_corretora_api():
    try:
        data = request.get_json()
        now = datetime.now() - timedelta(hours=3)
        now_iso = now.isoformat()
        now = datetime.now() - timedelta(hours=3)
        
        with open(f'log/chat_corretora_{now_iso}.json', 'w') as f:
            f.write(json.dumps(data, indent=4, ensure_ascii=False))
        # return jsonify({'message': 'Recebido com sucesso'}), 200
        
        
        
        if 1==1:#data['meta']['sender']['phone_number'] in numeros_teste and data['messages'][0]['message_type']== 0:
            inbox_id = data['inbox_id']
            contact_id = data['contact_inbox']['contact_id']
            conversation_id = data['id']
            sender = data['meta']['sender']['phone_number']
            user_message = data['messages'][0]['content']
            
            
            # Envia a resposta de volta para o Chatwoot
            url = f"https://chat.caiuas.com.br/api/v1/accounts/{inbox_id}/conversations/{conversation_id}/messages"
            
            payload = json.dumps({
                'content': 'dsads',
            })
            
            headers = {
                'api_access_token': f'{os.getenv("CHATWOOT_TOKEN")}',
                'Content-Type': 'application/json'
            }
            
            response = requests.request("POST", url, headers=headers, data=payload)
            
            retorno = {
                'chatwoot_response_status': response.status_code,
                'message': 'Chat processed and response sent.'
            }
            return jsonify(retorno), 200
        else:
            retorno = {
                'message': 'Chat data not processed due to conditions not met.'
            }
            return jsonify(retorno), 200
            
    except Exception as e:
        retorno = {
            'error': str(e)
        }
        with open(f'log/error_chat_{now_iso}.json', 'w') as f:
            f.write(json.dumps(retorno, indent=4, ensure_ascii=False))
        return jsonify(retorno), 400


def get_chatbot_information(id_bot: int = 1):
    """Busca informações do chatbot diretamente no banco (evita chamada HTTP interna)."""
    try:
        conn_site, cur_site = postgres_site()
        query = """
            select json_instructions, json_controller  
            from chatbots
            where id_chatbot = %s
        """
        cur_site.execute(query, (id_bot,))
        r = cur_site.fetchone()
        cur_site.close()
        conn_site.close()
        if not r:
            return {}
        return {
            'id_bot': id_bot,
            'instructions': r[0],
            'controller': r[1]
        }
    except Exception:
        return {}

@chat_bp.route('/chatbot', methods=['GET'])
def view_chatbot():
    context = {}
    id_chatbot = 1
    data = get_chatbot_information(id_chatbot)
    context['chatbot_info'] = data if data else {}

    context['title'] = 'Atualização Chatbot'
    context['email'] = session.get('email')
    emails_autorizados = ['pablo.ti@caiuas.com.br','mario.ribeiro@caiuas.com.br']
    if context['email'] not in emails_autorizados:
        return render_template('403.html'), 403
    return render_template('chatbot.html', context=context)

@chat_bp.route('/api/chatbot_information', methods=['GET'])
def api_chatbot_information():
    try:
        id_bot = request.args.get('id_bot', default=1, type=int)
        retorno = get_chatbot_information(id_bot)
        if not retorno:
            return jsonify({'message': 'Chatbot não encontrado'}), 404
        return jsonify(retorno), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400

@chat_bp.route('/api/update_chatbot_information/<int:id_bot>', methods=['PUT'])
def update_chatbot_information(id_bot):
    try:
        data = request.get_json()
        system_instruction_update = data['system_instruction']
        controller_update = data['controller']
        conn_site, cur_site = postgres_site()
        query = f"""
        select json_instructions, json_controller  
            from chatbots
            where id_chatbot = {id_bot}
        """
        cur_site.execute(query)
        r = cur_site.fetchall()
        if len(r) == 0:
            return jsonify({'message': 'Chatbot not found'}), 400
        system_instruction = r[0][0]
        controller = r[0][1]
        if controller_update is not None and controller_update != '':
            controller = controller_update
        query = f"""
            UPDATE chatbots
            SET json_instructions = %s, json_controller = %s
            WHERE id_chatbot = %s
        """
        cur_site.execute(query, (system_instruction, controller, id_bot))
        conn_site.commit()
        return jsonify({'message': 'Chatbot information updated successfully.'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400

@chat_bp.route('/api/update_chatbot_information/<int:id_bot>', methods=['POST'])
def api_update_chatbot_information(id_bot):
    """Atualiza o JSON de instruções (e opcionalmente controller) do chatbot."""
    try:
        payload = request.get_json(silent=True) or {}
        instructions = payload.get('instructions')
        controller = payload.get('controller')  # opcional
        if instructions is None:
            return jsonify({'message': 'Campo instructions é obrigatório.'}), 400
        # Garante que instructions seja dict
        if not isinstance(instructions, dict):
            return jsonify({'message': 'instructions deve ser um objeto JSON.'}), 400
        conn_site, cur_site = postgres_site()
        # Atualiza apenas campos enviados
        if controller is not None:
            query = """
                update chatbots
                set json_instructions = %s, json_controller = %s, updated_at = NOW()
                where id_chatbot = %s
            """
            cur_site.execute(query, (json.dumps(instructions, ensure_ascii=False), json.dumps(controller, ensure_ascii=False), id_bot))
        else:
            query = """
                update chatbots
                set json_instructions = %s, updated_at = NOW()
                where id_chatbot = %s
            """
            cur_site.execute(query, (json.dumps(instructions, ensure_ascii=False), id_bot))
        conn_site.commit()
        cur_site.close()
        conn_site.close()
        return jsonify({'message': 'Chatbot atualizado com sucesso.', 'id_bot': id_bot}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400

@chat_bp.route('/api/webhookwhatsapp', methods=['POST'])
def webhook_whatsapp():
    try:
        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%dT%H:%M:%S')
        
        payload = request.get_json()
        numero = str(payload['entry'][0]['changes'][0]['value']['metadata']['display_phone_number'])
        
        if numero == '551530336400':
            with open(f"{formatted_date}_webhookwhatsapp.json", 'w') as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            try:
                pesquisa = payload['entry'][0]['changes'][0]['value']['messages'][0]['interactive']['nfm_reply']['response_json']
                pesquisa = json.loads(pesquisa)
                pesquisa_tratada = {}
                flow_token = pesquisa['flow_token']
                flow_token = str(flow_token).split('-')
                cod_form = flow_token[0]
                pesquisa_tratada['Nome do cliente'] = pesquisa['screen_0_Informe_seu_nome_0'].split("_")[-1] #faça um aplit por "_" e capture a ultima posição
                pesquisa_tratada['Tipo do atendimento'] = pesquisa['screen_0_Sel_seu_atendimento_1'].split("_")[-1]
                payload['entry'][0]['changes'][0]['value']['messages'][0]['text'] = {}
                payload['entry'][0]['changes'][0]['value']['messages'][0]['type'] = 'text'
                payload['entry'][0]['changes'][0]['value']['messages'][0]['text']['body'] = '\n'.join([f"{k}: {v}" for k, v in pesquisa_tratada.items()])
                body_lines = ["PRIMEIRO CONTATO!"] + [
                    f"{k}: {v}" for k, v in pesquisa_tratada.items()
                ]
                payload['entry'][0]['changes'][0]['value']['messages'][0]['text']['body'] = '\n'.join(body_lines)
                
            except Exception as e:
                pass

            url = "https://chat.caiuas.com.br/webhooks/whatsapp/+551530336400"
            headers = {
            'Content-Type': 'application/json'
            }
            payload = json.dumps(payload)
            
            response = requests.request("POST", url, headers=headers, data=payload)
        else:    
            try:
                # if pay

                pesquisa = payload['entry'][0]['changes'][0]['value']['messages'][0]['interactive']['nfm_reply']['response_json']
                pesquisa = json.loads(pesquisa)
                pesquisa_tratada = {}
                flow_token = pesquisa['flow_token']
                
                flow_token = str(flow_token).split('-')
                
                cod_form = flow_token[0]
                cod_empresa = flow_token[1]
                cod_evento = flow_token[2]
                
                if cod_form == 'PV':

                    pesquisa_tratada['evento'] = pesquisa['flow_token']

                    pesquisa_tratada['Como você avalia sua satisfação geral com nosso pós-vendas ?'] = pesquisa['screen_0_Escolha_uma_das_opes_0'].split("_")[-1] #faça um aplit por "_" e capture a ultima posição
                    pesquisa_tratada['Como avalia o agendamento de serviços ?'] = pesquisa['screen_1_Escolha_uma_das_opes_0'].split("_")[-1]
                    pesquisa_tratada['Como você avalia a recepção de serviços ?'] = pesquisa['screen_2_Escolha_uma_das_opes_0'].split("_")[-1]
                    pesquisa_tratada['Como você avalia nossas instalações ?'] = pesquisa['screen_3_Escolha_uma_das_opes_0'].split("_")[-1]
                    pesquisa_tratada['Como você avalia o atendimento do nosso consultor de serviços ?'] = pesquisa['screen_4_Escolha_uma_das_opes_0'].split("_")[-1]
                    pesquisa_tratada['Como você avalia a qualidade do serviço realizado ?'] = pesquisa['screen_5_Escolha_uma_das_opes_0'].split("_")[-1]
                    pesquisa_tratada['Como você avalia o custo-benefício ?'] = pesquisa['screen_6_Escolha_uma_das_opes_0'].split("_")[-1]
                    pesquisa_tratada['Recomendaria a concessionaria a um amigo ou familiar ?'] = pesquisa['screen_7_Escolha_uma_das_opes_0'].split("_")[-1]
                    payload['entry'][0]['changes'][0]['value']['messages'][0]['text'] = {}
                    payload['entry'][0]['changes'][0]['value']['messages'][0]['type'] = 'text'
                    # # adiciona em uma mensagem só todas as respostas das perguntas
                    payload['entry'][0]['changes'][0]['value']['messages'][0]['text']['body'] = '\n'.join([f"{k}: {v}" for k, v in pesquisa_tratada.items()])
                    body_lines = ["Resposta sobre pesquisa de satisfação Pós Vendas"] + [
                        f"{k}: {v}" for k, v in pesquisa_tratada.items()
                    ]
                    payload['entry'][0]['changes'][0]['value']['messages'][0]['text']['body'] = '\n'.join(body_lines)
                    
                elif cod_form == 'SW':
                    pesquisa_tratada['evento'] = pesquisa['flow_token']
                    pesquisa_tratada['Instalações'] = pesquisa.get('screen_0_Nossas_instalaes_0', '').split("_")[-1]
                    pesquisa_tratada['Atendimento Vendedor'] = pesquisa.get('screen_0_Atendimento_Vendedor_1', '').split("_")[-1]
                    pesquisa_tratada['Entrega Veículo'] = pesquisa.get('screen_0_Entrega_do_Veculo_2', '').split("_")[-1]
                    pesquisa_tratada['Oferecido Teste Drive'] = pesquisa.get('screen_0_Foi_oferecido_teste_drive_3', '').split("_")[-1]
                    pesquisa_tratada['Realizou Teste Drive'] = pesquisa.get('screen_0_Realizou_o_teste_drive_4', '').split("_")[-1]
                    pesquisa_tratada['Exp. Teste Drive'] = pesquisa.get('screen_0_Exp_Teste_Drive_5', '').split("_")[-1]
                    pesquisa_tratada['Recomendaria'] = pesquisa.get('screen_0_Recomendaria_a_concessionria__6', '').split("_")[-1]
                    pesquisa_tratada['Gerente Participou'] = pesquisa.get('screen_0_O_gerente_participou_7', '').split("_")[-1]
                    
                    payload['entry'][0]['changes'][0]['value']['messages'][0]['text'] = {}
                    payload['entry'][0]['changes'][0]['value']['messages'][0]['type'] = 'text'
                    
                    body_lines = ["📋 Pesquisa Showroom"] + [
                        f"{k}: {v}" for k, v in pesquisa_tratada.items() if v
                    ]
                    payload['entry'][0]['changes'][0]['value']['messages'][0]['text']['body'] = '\n'.join(body_lines)
                    
            except Exception as e:
                pass

            url = "https://chat.caiuas.com.br/webhooks/whatsapp/+551533315555"
            headers = {
            'Content-Type': 'application/json'
            }
            payload = json.dumps(payload)
            
            response = requests.request("POST", url, headers=headers, data=payload)
            print (str(response))

        return json.dumps({'status': 'success', 'message': 'Webhook processed successfully'}), 200
    except Exception as e:
        return json.dumps({'error': 'Invalid JSON payload'}), 400

@chat_bp.route('/api/chatwoot/open_chat/<int:number>', methods=['POST'])
def chatwoot_open_chat(number):
    try:
        retorno = {}
        data = request.get_json()
        name = data.get('name', 'Cliente')
        if len(str(number)) <= 12:
            retorno['message'] = "Número inválido"
            return jsonify(retorno), 400
        conn, cur = postgres_chatwoot()
        query = f"""
                    WITH update_result AS (
                    UPDATE contacts
                    SET
                        "name" = '{str(name).upper()}',
                        updated_at = now(),
                        last_activity_at = now()
                    WHERE phone_number = '+{number}'
                    RETURNING id
                ),
                insert_result AS (
                    INSERT INTO contacts
                    ("name", email, phone_number, account_id, created_at, updated_at, additional_attributes, identifier, custom_attributes, last_activity_at, contact_type, middle_name, last_name, "location", country_code, "blocked")
                    SELECT
                        '{str(name).upper()}', NULL, '+{number}', 1, now(), now(), '{{}}'::jsonb, NULL, '{{}}'::jsonb, now(), 1, '', '', NULL, NULL, false
                    WHERE NOT EXISTS (SELECT 1 FROM update_result)
                    RETURNING id
                )
                SELECT id FROM update_result
                UNION ALL
                SELECT id FROM insert_result
                """
        cur.execute(query)
        conn.commit()
        r = cur.fetchone()
        if len(r) == 0:
            retorno = {
                'message': 'Contact not created/updated.'
            }
            cur.close()
            conn.close()
            return jsonify(retorno), 400
        contact_id = r[0]
        cur.close()
        conn.close()
        url = f"https://chat.caiuas.com.br/app/accounts/1/contacts/{contact_id}"
        retorno = {}
        retorno['url'] = url
        return jsonify(retorno), 200
        
    except Exception as e:
        return json.dumps({'error': 'Invalid JSON payload'}), 400
        