# MRX Systems - ERP de Gestão de Metais e Eletrônicos

## Visão Geral
Sistema ERP completo desenvolvido em Flask para gestão inteligente de compra, logística, estoque e separação de materiais metálicos e placas eletrônicas.

## Informações de Acesso

### Usuário Administrador Padrão
- **Email**: admin@sistema.com
- **Senha padrão**: admin123 (alterar após primeiro acesso)

⚠️ **Importante**: Configure as variáveis de ambiente ADMIN_EMAIL e ADMIN_PASSWORD para personalizar as credenciais do administrador.

## Arquitetura do Projeto

### Stack Tecnológico
- **Backend**: Python 3.11 + Flask 3.0
- **Database**: PostgreSQL (via Replit)
- **ORM**: SQLAlchemy + Flask-Migrate
- **Autenticação**: JWT (Flask-JWT-Extended)
- **WebSockets**: Flask-SocketIO + eventlet
- **IA**: Google Gemini AI (classificação de placas)
- **Processamento de Imagens**: OpenCV + Pillow
- **Planilhas**: openpyxl + pandas

### Estrutura de Diretórios
```
/
├── app/                    # Aplicação principal
│   ├── __init__.py        # Inicialização do Flask
│   ├── models.py          # Modelos de dados SQLAlchemy
│   ├── auth.py            # Autenticação e autorização
│   ├── rbac_config.py     # Configuração RBAC
│   ├── routes/            # Blueprints de rotas
│   ├── services/          # Serviços (IA, scanner)
│   ├── utils/             # Utilitários
│   ├── static/            # CSS, JS, imagens
│   └── templates/         # Templates HTML
├── app.py                 # Ponto de entrada (dev)
├── wsgi.py                # Ponto de entrada (prod)
├── requirements.txt       # Dependências Python
└── uploads/               # Arquivos enviados
```

## Módulos Principais

### 1. Gestão de Usuários e Perfis (RBAC)
- 7 perfis pré-configurados: Admin, Comprador, Conferente, Separação, Motorista, Financeiro, Auditoria
- Sistema de permissões granular
- Auditoria completa de ações

### 2. Fornecedores e Vendedores
- Cadastro PF/PJ com consulta CNPJ
- Sistema de atribuição de fornecedores a funcionários
- Preços por fornecedor + tipo de lote + estrelas

### 2.1 Visitas a Fornecedores (NOVO)
- Cadastro de visitas a potenciais fornecedores em campo
- Captura automática de GPS e geocoding
- Cards com status: Pendente, Aprovada, Recusada
- Conversão de visita para fornecedor (pre-preenche formulário)
- Estatísticas de visitas por status
- Acesso: /visitas.html

### 3. Solicitações com IA
- Upload de fotos de placas eletrônicas
- Classificação automática via Gemini AI
- Geocoding reverso (GPS → endereço)
- Cálculo automático de preços

### 4. Logística e Ordem de Serviço
- App PWA para motoristas
- Rastreamento GPS em tempo real
- Quadro Kanban de OS
- Reagendamento e cancelamento

### 5. Conferência de Recebimento
- Detecção automática de divergências
- Workflow de decisão administrativa
- Criação automática de lotes

### 6. WMS (Warehouse Management)
- Gestão completa de lotes
- Bloqueio/reserva de materiais
- Inventário cíclico
- Auditoria de movimentações

### 7. Separação de Lotes
- Registro de componentes separados
- Gestão de resíduos
- Aprovação de supervisor
- Criação de sublotes

### 8. Notificações em Tempo Real
- WebSocket (Socket.IO)
- Salas por perfil de usuário
- Push notifications (PWA)

### 9. Dashboard e Análises
- Métricas de compras, estoque, logística
- Gráficos Chart.js
- KPIs em tempo real

## Configuração

### Variáveis de Ambiente Necessárias
- `DATABASE_URL`: URL do PostgreSQL (já configurado pelo Replit)
- `SESSION_SECRET`: Chave secreta da sessão (já configurado)
- `JWT_SECRET_KEY`: Chave JWT (opcional, usa SESSION_SECRET por padrão)
- `ADMIN_EMAIL`: Email do admin (opcional)
- `ADMIN_PASSWORD`: Senha do admin (opcional)
- `GEMINI_API_KEY`: API key do Google Gemini (para IA de classificação)

### Inicialização do Banco de Dados
O banco de dados é inicializado automaticamente na primeira execução:
1. Cria todas as tabelas
2. Inicializa 3 tabelas de preço (1, 2 e 3 estrelas)
3. Cria tipo de lote padrão
4. Cria 7 perfis de usuário
5. Cria usuário administrador

## Desenvolvimento

### Executar Localmente
```bash
python app.py
```
Acesse: http://localhost:5000

### Produção (Deployment)
O projeto está configurado para usar **Gunicorn com eventlet** para suportar WebSockets:
```bash
gunicorn --bind=0.0.0.0:5000 --worker-class=eventlet -w 1 wsgi:app
```

## Features Especiais

### PWA (Progressive Web App)
- Service Worker registrado
- Instalável em dispositivos móveis
- Funciona offline (assets em cache)
- Manifest.json configurado

### IA de Classificação
- Usa Google Gemini para análise de imagens
- Classifica placas em: Leve, Médio, Pesado
- Fornece justificativa textual
- Integra com sistema de preços

### GPS e Geolocalização
- Captura automática de coordenadas
- Geocoding reverso (coordenadas → endereço)
- Rastreamento de rotas de motoristas
- Histórico de localizações

## Segurança
- Autenticação JWT com refresh tokens
- RBAC completo
- CORS configurado
- Senhas com bcrypt
- Auditoria de todas as ações
- Session secrets gerenciados pelo Replit

## Status do Projeto
✅ **Configurado e funcionando no Replit**
- Python 3.11 instalado
- Todas as dependências instaladas
- Banco de dados PostgreSQL configurado
- Workflow configurado na porta 5000
- Aplicação testada e verificada
- Deployment configurado com Gunicorn + eventlet

## Próximos Passos Recomendados
1. Configure a API key do Google Gemini (variável GEMINI_API_KEY) para habilitar classificação por IA
2. Altere a senha do administrador padrão
3. Configure emails personalizados e senhas para o admin
4. Faça o deploy para produção usando o botão "Deploy" do Replit

## Data de Configuração
Configurado em: 02 de dezembro de 2025
