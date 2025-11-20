from flask import Flask, jsonify, request, make_response

app = Flask(__name__)

# ==========================================
# ESTRUTURAS DE DADOS (Definição da Atividade)
# ==========================================

# Define os parâmetros de configuração aceites pela atividade.
# Estes campos correspondem aos "names" dos inputs no formulário HTML.
PARAMS_DEFINITION = [
    { "name": "modulos_ativos", "type": "text/plain" },
    { "name": "nivel_dificuldade", "type": "text/plain" },
    { "name": "nota_minima_aprovacao", "type": "integer" },
    { "name": "limite_tempo_minutos", "type": "integer" }
]

# Define a lista de métricas (analytics) que a atividade é capaz de registar.
# A Inven!RA usa esta lista para saber o que pode apresentar ao professor.
ANALYTICS_LIST_DEF = {
    "qualAnalytics": [
        { "name": "feedback_modulos", "type": "text/plain" },
        { "name": "erros_comuns", "type": "text/plain" }
    ],
    "quantAnalytics": [
        { "name": "modulos_concluidos", "type": "integer" },
        { "name": "tempo_total_minutos", "type": "integer" },
        { "name": "pontuacao_orcamento", "type": "integer" },
        { "name": "pontuacao_poupanca", "type": "integer" },
        { "name": "pontuacao_juros", "type": "integer" },
        { "name": "pontuacao_consumo", "type": "integer" }
    ]
}

# ==========================================
# ENDPOINTS (Interface com a Inven!RA)
# ==========================================

# 1. URL DE CONFIGURAÇÃO
# Retorna o código HTML do formulário de configuração.
# A Inven!RA apresenta este formulário ao utilizador para recolher preferências.
@app.route('/edu-financeira/config.html', methods=['GET'])
def get_config_ui():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Configuração da Atividade</title>
        <style>body { font-family: sans-serif; padding: 20px; } label { font-weight: bold; }</style>
    </head>
    <body>
        <h2>Configurar Atividade: Educação Financeira</h2>
        <form id="configForm">
            <label>Módulos a incluir (separados por vírgula):</label><br>
            <input type="text" name="modulos_ativos" value="orcamento,poupanca,juros,consumo" style="width: 300px;"><br><br>

            <label>Nível de Dificuldade:</label><br>
            <select name="nivel_dificuldade">
                <option value="basico">Básico</option>
                <option value="intermedio" selected>Intermédio</option>
                <option value="avancado">Avançado</option>
            </select><br><br>

            <label>Nota Mínima de Aprovação (%):</label><br>
            <input type="number" name="nota_minima_aprovacao" value="50"><br><br>
            
            <label>Limite de Tempo (minutos):</label><br>
            <input type="number" name="limite_tempo_minutos" value="45">
        </form>
    </body>
    </html>
    """
    return make_response(html_content, 200)

# 2. URL DE PARÂMETROS JSON
# Retorna a definição dos parâmetros em formato JSON.
# Permite à Inven!RA saber quais os campos a extrair do formulário HTML.
@app.route('/edu-financeira/params', methods=['GET'])
def get_json_params():
    return jsonify(PARAMS_DEFINITION)

# 3. URL DE DEPLOY
# Recebe o ID da atividade da Inven!RA e gera o link de acesso para os estudantes.
# O 'request.host_url' deteta automaticamente o domínio onde o servidor está a correr.
@app.route('/edu-financeira/deploy', methods=['GET'])
def deploy_activity():
    activity_id = request.args.get('activityID')
    
    if not activity_id:
        return jsonify({"error": "activityID obrigatorio"}), 400

    # Gera o URL final para o estudante clicar.
    base_url = request.host_url.rstrip('/')
    student_access_url = f"{base_url}/atividade/run?act={activity_id}"
    
    return jsonify({"access_url": student_access_url})

# 4. URL DE ANALYTICS
# Recebe um pedido POST com o 'activityID'.
# Retorna um JSON com os dados de progresso (mock data) dos alunos nessa atividade.
@app.route('/edu-financeira/analytics', methods=['POST'])
def get_analytics_data():
    # Tenta processar o corpo do pedido, mesmo que o cabeçalho não seja application/json
    data = request.get_json(force=True, silent=True) or {}
    activity_id = data.get('activityID', 'unknown')

    base_url = request.host_url.rstrip('/')

    # Exemplo de resposta com dados estáticos para dois alunos
    analytics_response = [
        {
            "inveniraStdID": "1001",
            "quantAnalytics": [
                { "name": "modulos_concluidos", "value": 4 },
                { "name": "tempo_total_minutos", "value": 35 },
                { "name": "pontuacao_orcamento", "value": 90 },
                { "name": "pontuacao_poupanca", "value": 85 },
                { "name": "pontuacao_juros", "value": 70 },
                { "name": "pontuacao_consumo", "value": 95 }
            ],
            "qualAnalytics": [
                # URLs que apontam para páginas de detalhe (a implementar futuramente)
                { "Relatorio Detalhado": f"{base_url}/report/detail?std=1001&act={activity_id}" },
                { "Erros Comuns": f"{base_url}/report/errors?std=1001&act={activity_id}" }
            ]
        },
        {
            "inveniraStdID": "1002",
            "quantAnalytics": [
                { "name": "modulos_concluidos", "value": 2 },
                { "name": "tempo_total_minutos", "value": 45 },
                { "name": "pontuacao_orcamento", "value": 60 },
                { "name": "pontuacao_poupanca", "value": 50 },
                { "name": "pontuacao_juros", "value": 20 },
                { "name": "pontuacao_consumo", "value": 0 }
            ],
            "qualAnalytics": [
                { "Relatorio Detalhado": f"{base_url}/report/detail?std=1002&act={activity_id}" }
            ]
        }
    ]

    return jsonify(analytics_response)

# 5. URL DE LISTA DE ANALYTICS
# Retorna a definição das métricas que esta atividade disponibiliza.
@app.route('/edu-financeira/analytics-list', methods=['GET'])
def get_analytics_list():
    return jsonify(ANALYTICS_LIST_DEF)

# Inicialização do servidor
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)