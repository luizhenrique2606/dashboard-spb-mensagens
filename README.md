# 📊 Dashboard de Mensagens SPB

Dashboard para monitoramento de mensagens do Sistema de Pagamentos Brasileiro (SPB) com interface moderna e responsiva.

## ✨ Funcionalidades

- 🔄 **Monitoramento em tempo real** de mensagens STR, LPI, SME, RCO, LDL, LTR, SLB e SEL
- 📱 **Interface web responsiva** com design moderno
- ⚡ **Atualização automática** dos dados a cada 5 segundos
- 📈 **Contadores dinâmicos** por aba e total geral
- 🎨 **Gradientes elegantes** no cabeçalho e cartões
- 🔗 **Links úteis** para documentação e planilha base
- 📊 **Integração com Google Sheets** para dados em tempo real

## 🚀 Deploy

### Desenvolvimento Local
1. Execute `python run_dashboard.py`
2. Acesse http://localhost:5000

### Produção (Render.com)
1. Configure a variável de ambiente `GOOGLE_CREDENTIALS` com as credenciais JSON
2. O app será executado automaticamente na porta definida pelo Render

## 📋 Requisitos

- Python 3.7+
- Credenciais do Google Sheets API
- Dependências listadas em requirements.txt

## 🔧 Configuração

### Variáveis de Ambiente (Produção)
- `GOOGLE_CREDENTIALS`: JSON das credenciais do Google Service Account
- `PORT`: Porta do servidor (definida automaticamente pelo Render)

### Desenvolvimento Local
- Arquivo `google_service_account_key.json` no diretório do usuário

## 📁 Estrutura do Projeto

```
dashboard_mensagens/
├── app.py                 # Aplicação Flask principal
├── run_dashboard.py       # Script para desenvolvimento local
├── requirements.txt       # Dependências Python
├── Procfile              # Configuração para deploy
├── templates/
│   └── dashboard.html    # Interface do usuário
└── README.md            # Este arquivo
```

## 🌐 APIs Disponíveis

- `GET /` - Página principal do dashboard
- `GET /api/data` - Retorna todos os dados de sucesso
- `GET /api/stats` - Retorna estatísticas resumidas
- `GET /api/recent` - Retorna os 10 registros mais recentes

## 📊 Configuração do Google Sheets

- **ID da Planilha**: `17aWoS5Q8x-1I5VY8Sr1re2aA3GhauCLSMZeaklSne18`
- **GID da Aba**: `862097115`

### Estrutura da Planilha
- **timestamp** - Data e hora do registro
- **message_code** - Código da mensagem (STR0007, LPI0001, etc.)
- **status** - Status do registro (deve ser "sucesso")
- **details** - Detalhes adicionais
- **catalog_code** - Código do catálogo para lógica R2

## 🎯 Tipos de Mensagem Suportados

### STR (Sistema de Transferência de Reservas)
- STR0007, STR0006, STR0004, STR0008, STR0010, STR0013, STR0025, STR0026

### LPI (Liquidação de Pagamentos Instantâneos)
- LPI0001, LPI0002, LPI0003, LPI0004, LPI0005

### SME (Sistema de Moeda Eletrônica)
- SME0001, SME0002, SME0003

### RCO (Reservas de Contingência Operacional)
- RCO0010, RCO0011

### Novos Tipos
- **LDL**: Mensagens de liquidação diferida
- **LTR**: Mensagens de liquidação em tempo real
- **SLB**: Mensagens de saldo bancário
- **SEL**: Mensagens de seleção

## 🔧 Solução de Problemas

### Erro de Conexão com Google Sheets
- Verifique as credenciais do Google Service Account
- Confirme permissões de acesso à planilha
- Verifique ID da planilha e GID da aba

### Dashboard não carrega
- Verifique se o servidor está rodando
- Teste as APIs: `/api/stats`
- Verifique console do navegador (F12)

### Dados não aparecem
- Confirme registros com `status = "sucesso"`
- Verifique formato das datas
- Teste conexão com planilha

## 📞 Suporte

1. Verifique logs do servidor no terminal
2. Confirme dependências instaladas
3. Teste conexão Google Sheets
4. Verifique estrutura da planilha