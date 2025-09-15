#!/usr/bin/env python3
"""
Dashboard de Mensagens SPB - Aplicação Flask
Monitora sucessos e erros das mensagens STR/LPI/SME
"""

import os
import sys
import gspread
from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta
import json
import base64

# Configurações
SPREADSHEET_ID = '17aWoS5Q8x-1I5VY8Sr1re2aA3GhauCLSMZeaklSne18'
WORKSHEET_GID = 862097115

# Configuração para produção - usa variável de ambiente
def get_service_account_info():
    """Obtém as credenciais do Google Sheets"""
    # Em produção, usa variável de ambiente
    if 'GOOGLE_CREDENTIALS' in os.environ:
        credentials_json = os.environ['GOOGLE_CREDENTIALS']
        return json.loads(credentials_json)
    
    # Em desenvolvimento local, usa arquivo
    import getpass
    usuario = getpass.getuser()
    SA_PATH = f'/Users/{usuario}/Documents/Python/google_service_account_key.json'
    
    if os.path.exists(SA_PATH):
        with open(SA_PATH, 'r') as f:
            return json.load(f)
    
    raise FileNotFoundError("Credenciais do Google Sheets não encontradas")

app = Flask(__name__)

def get_worksheet():
    """Conecta à planilha do Google Sheets"""
    try:
        # Usa as credenciais obtidas da função
        service_account_info = get_service_account_info()
        gc = gspread.service_account_from_dict(service_account_info)
        sh = gc.open_by_key(SPREADSHEET_ID)
        
        # Tenta encontrar a aba pelo GID
        try:
            ws = sh.get_worksheet_by_id(WORKSHEET_GID)
            if ws is not None:
                print(f"✅ Aba encontrada pelo GID: {ws.title} (ID: {ws.id})")
                return ws
        except Exception as e:
            print(f"❌ Erro ao buscar por GID: {e}")
            pass
        
        # Fallback: procura por todas as abas
        print("📋 Abas disponíveis:")
        for ws in sh.worksheets():
            try:
                ws_id = getattr(ws, 'id', None) or getattr(ws, '_properties', {}).get('sheetId')
                print(f"  - {ws.title}: ID = {ws_id}")
                if getattr(ws, 'id', None) == WORKSHEET_GID:
                    print(f"✅ Aba encontrada no fallback: {ws.title}")
                    return ws
                if getattr(ws, '_properties', {}).get('sheetId') == WORKSHEET_GID:
                    print(f"✅ Aba encontrada no fallback (properties): {ws.title}")
                    return ws
            except Exception as e:
                print(f"❌ Erro ao processar aba {ws.title}: {e}")
                continue
        
        raise RuntimeError('Aba não encontrada')
    except Exception as e:
        print(f"Erro ao conectar à planilha: {e}")
        return None

def get_success_data():
    """Obtém dados de sucesso da planilha com lógica de catálogo"""
    try:
        ws = get_worksheet()
        if not ws:
            return []
        
        # Obtém todos os dados
        all_data = ws.get_all_values()
        if len(all_data) <= 1:  # Apenas cabeçalho ou vazio
            return []
        
        # Processa os dados (pula o cabeçalho)
        success_data = []
        for row in all_data[1:]:
            if len(row) >= 3 and row[2].lower() == 'sucesso':
                # Dados básicos
                message_code = row[1] if len(row) > 1 else ''
                catalog_code = row[4].lower() if len(row) > 4 else ''  # Coluna E
                
                # Adiciona a mensagem original
                success_data.append({
                    'timestamp': row[0] if len(row) > 0 else '',
                    'message_code': message_code,
                    'status': row[2] if len(row) > 2 else '',
                    'details': row[3] if len(row) > 3 else '',
                    'catalog_code': catalog_code
                })
                
                # Lógica de catálogo - adiciona mensagens relacionadas
                if catalog_code == 'trocadecatalagonupag':
                    # STR da Nu Pagamentos + R2 da Nu Financeira (exceto STR0010 e STR0013)
                    if message_code.startswith('STR') and message_code not in ['STR0010', 'STR0013']:
                        success_data.append({
                            'timestamp': row[0],
                            'message_code': f"{message_code}R2",
                            'status': 'sucesso',
                            'details': f"R2 gerado por {catalog_code}",
                            'catalog_code': catalog_code,
                            'generated': True
                        })
                
                elif catalog_code == 'trocadecatalagonufin':
                    # STR da Nu Financeira + R2 da Nu Invest
                    if message_code.startswith('STR'):
                        success_data.append({
                            'timestamp': row[0],
                            'message_code': f"{message_code}R2",
                            'status': 'sucesso',
                            'details': f"R2 gerado por {catalog_code}",
                            'catalog_code': catalog_code,
                            'generated': True
                        })
                
                elif catalog_code == 'trocadecatalagonuinvest':
                    # STR da Nu Invest + R2 da Nu Pagamentos
                    if message_code.startswith('STR'):
                        success_data.append({
                            'timestamp': row[0],
                            'message_code': f"{message_code}R2",
                            'status': 'sucesso',
                            'details': f"R2 gerado por {catalog_code}",
                            'catalog_code': catalog_code,
                            'generated': True
                        })
        
        return success_data
    except Exception as e:
        print(f"Erro ao obter dados: {e}")
        return []

def get_stats():
    """Calcula estatísticas dos dados"""
    data = get_success_data()
    
    if not data:
        return {
            'total_success': 0,
            'today_success': 0,
            'message_types': {},
            'recent_messages': []
        }
    
    # Estatísticas básicas
    total_success = len(data)
    today = datetime.now().strftime('%Y-%m-%d')
    today_success = len([d for d in data if d['timestamp'].startswith(today)])
    
    # Tipos de mensagem
    message_types = {}
    for d in data:
        msg_type = d['message_code'][:6] if d['message_code'] else 'Unknown'  # STR000, LPI000, etc.
        message_types[msg_type] = message_types.get(msg_type, 0) + 1
    
    # Mensagens recentes (últimas 10)
    recent_messages = sorted(data, key=lambda x: x['timestamp'], reverse=True)[:10]
    
    return {
        'total_success': total_success,
        'today_success': today_success,
        'message_types': message_types,
        'recent_messages': recent_messages
    }

@app.route('/')
def dashboard():
    """Página principal do dashboard"""
    return render_template('dashboard.html')

@app.route('/api/data')
def api_data():
    """API: Retorna todos os dados de sucesso"""
    return jsonify(get_success_data())

@app.route('/api/stats')
def api_stats():
    """API: Retorna estatísticas resumidas"""
    return jsonify(get_stats())

@app.route('/api/recent')
def api_recent():
    """API: Retorna os 10 registros mais recentes"""
    data = get_success_data()
    recent = sorted(data, key=lambda x: x['timestamp'], reverse=True)[:10]
    return jsonify(recent)

if __name__ == '__main__':
    print("🚀 Iniciando Dashboard de Mensagens SPB")
    
    # Obtém a porta do ambiente (para Render) ou usa 5000 como padrão
    port = int(os.environ.get('PORT', 5000))
    
    print(f"📊 Dashboard: http://localhost:{port}")
    print("🔄 Pressione Ctrl+C para parar")
    
    # Testa conexão
    try:
        ws = get_worksheet()
        if ws:
            print("✅ Conexão com Google Sheets OK")
        else:
            print("❌ Erro na conexão com Google Sheets")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    app.run(debug=False, host='0.0.0.0', port=port)
