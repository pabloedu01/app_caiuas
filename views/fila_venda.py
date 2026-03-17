from flask import Blueprint, jsonify, render_template, request
from database import postgres_site

fila_venda_bp = Blueprint('fila_venda', __name__)

@fila_venda_bp.route('/fila_venda', methods=['GET'])
def fila_venda():
    try:
        conn, cur = postgres_site()
        grupos = ['sorocaba', 'indaiatuba', 'sorocaba_direta', 'indaiatuba_direta']
        listas = {}
        for grupo in grupos:
            cur.execute("SELECT id, nome, ordem, grupo FROM vendedores_vez WHERE grupo = %s ORDER BY ordem", (grupo,))
            vendedores = cur.fetchall()
            listas[grupo] = [dict(row) for row in vendedores]
        cur.close()
        conn.close()
        return render_template('fila_venda.html', listas=listas)
    except Exception as e:
        return f"Erro ao buscar fila: {e}", 500

@fila_venda_bp.route('/api/fila_venda', methods=['GET', 'POST'])
def api_fila_venda():
    if request.method == 'GET':
        try:
            conn, cur = postgres_site()
            grupos = ['sorocaba', 'indaiatuba', 'sorocaba_direta', 'indaiatuba_direta']
            listas = {}
            for grupo in grupos:
                cur.execute("SELECT id, nome, ordem, grupo FROM vendedores_vez WHERE grupo = %s ORDER BY ordem", (grupo,))
                vendedores = cur.fetchall()
                listas[grupo] = [dict(row) for row in vendedores]
            cur.close()
            conn.close()
            return jsonify(listas)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    elif request.method == 'POST':
        data = request.get_json()
        nome = data.get('nome')
        grupo = data.get('grupo')
        if not nome or not grupo:
            return jsonify({'error': 'Nome e grupo são obrigatórios'}), 400
        try:
            conn, cur = postgres_site()
            cur.execute("SELECT COALESCE(MAX(ordem), 0) + 1 FROM vendedores_vez WHERE grupo = %s", (grupo,))
            ordem = cur.fetchone()[0]
            cur.execute("INSERT INTO vendedores_vez (nome, ordem, grupo) VALUES (%s, %s, %s)", (nome, ordem, grupo))
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({'message': 'Vendedor adicionado'}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@fila_venda_bp.route('/api/fila_venda/<int:id>', methods=['DELETE'])
def api_remover_vendedor(id):
    try:
        conn, cur = postgres_site()
        cur.execute("DELETE FROM vendedores_vez WHERE id = %s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'message': 'Vendedor removido'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Nova rota para salvar a ordem dos vendedores
@fila_venda_bp.route('/api/fila_venda/ordenar', methods=['POST'])
def api_ordenar_vendedores():
    data = request.get_json()
    grupo = data.get('grupo')
    nova_ordem = data.get('ordem')  # Lista de IDs na nova ordem
    if not grupo or not isinstance(nova_ordem, list):
        return jsonify({'error': 'Grupo e ordem são obrigatórios'}), 400
    try:
        conn, cur = postgres_site()
        for idx, vendedor_id in enumerate(nova_ordem, start=1):
            cur.execute("UPDATE vendedores_vez SET ordem = %s WHERE id = %s AND grupo = %s", (idx, vendedor_id, grupo))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'message': 'Ordem atualizada com sucesso'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
