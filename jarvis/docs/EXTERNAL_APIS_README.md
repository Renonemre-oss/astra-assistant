# 🌐 Integrações com APIs Externas - Jarvis

Este documento descreve as novas integrações implementadas no Jarvis para conectar com APIs externas, incluindo notícias, calendários, email e redes sociais.

## 📋 APIs Implementadas

### 1. 📰 APIs de Notícias
- **RSS Feeds**: Leitura de qualquer feed RSS/Atom (funciona sem configuração)
- **NewsData.io**: API premium de notícias (requer chave de API)
- **NewsAPI.org**: API alternativa de notícias (requer chave de API)

### 2. 📅 APIs de Calendário
- **Google Calendar**: Listagem e criação de eventos
- **Microsoft Outlook**: Listagem e criação de eventos via Microsoft Graph

### 3. 📧 APIs de Email
- **Gmail**: Listagem de mensagens e envio de emails
- **Microsoft Outlook**: Listagem de mensagens e envio de emails via Microsoft Graph

### 4. 📱 APIs de Redes Sociais
- **Twitter/X**: Leitura de timeline e postagem de tweets (v2 API)
- **LinkedIn**: Criação de posts

## ⚙️ Configuração

### Variáveis de Ambiente

Configure as seguintes variáveis de ambiente no Windows:

```powershell
# APIs de Notícias (opcional)
$env:NEWS_API_KEY = "sua_chave_newsdata_ou_newsapi"

# Google APIs
$env:GOOGLE_CALENDAR_TOKEN = "seu_token_oauth_google_calendar"
$env:GMAIL_TOKEN = "seu_token_oauth_gmail"

# Microsoft Graph (Outlook/Office 365)
$env:MS_GRAPH_TOKEN = "seu_token_oauth_microsoft_graph"

# Twitter/X
$env:TWITTER_BEARER_TOKEN = "seu_bearer_token_twitter"
$env:TWITTER_USER_TOKEN = "seu_access_token_twitter"  # opcional para posts
$env:TWITTER_USER_ID = "seu_user_id_twitter"

# LinkedIn
$env:LINKEDIN_ACCESS_TOKEN = "seu_access_token_linkedin"
$env:LINKEDIN_URN = "urn:li:person:seu_id_linkedin"

# Configurações opcionais
$env:NEWS_PROVIDER = "newsdata"  # ou "newsapi" ou "rss"
$env:WEATHER_PROVIDER = "openweathermap"
$env:WEATHER_LANG = "pt_br"
```

### Como Obter Tokens OAuth

#### Google APIs (Calendar/Gmail)
1. Vá para [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um projeto ou use um existente
3. Ative as APIs necessárias (Calendar API, Gmail API)
4. Configure OAuth 2.0 credentials
5. Use uma ferramenta como [OAuth Playground](https://developers.google.com/oauthplayground/) para obter tokens

#### Microsoft Graph (Outlook)
1. Vá para [Azure App Registration](https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/)
2. Registre um novo app
3. Configure permissões necessárias (Calendars.Read, Mail.Read, etc.)
4. Use fluxo OAuth 2.0 para obter access token

#### Twitter/X
1. Crie um app em [Twitter Developer Portal](https://developer.twitter.com/)
2. Obtenha Bearer Token para leitura
3. Configure OAuth 2.0 para postagem

#### LinkedIn
1. Crie um app em [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Obtenha access token com scope `w_member_social`

## 🚀 Como Usar

### 1. Executar o Dashboard Principal
```powershell
python api_integration_hub.py
```

O dashboard agora inclui uma nova seção "🔗 INTEGRAÇÕES EXTERNAS" que mostra o status das APIs configuradas.

### 2. Testar Individualmente
```powershell
python example_external_apis.py
```

### 3. Usar Programaticamente
```python
from modules.external_apis.api_manager import APIManager

# Inicializar gerenciador
manager = APIManager()

# Notícias via RSS
news = manager.news.from_rss("https://rss.cnn.com/rss/edition.rss")

# Eventos do calendário Google
events = manager.calendar.google_list_events(max_results=5)

# Listar emails do Gmail
emails = manager.email.gmail_list_messages(max_results=10)

# Timeline do Twitter
tweets = manager.social.twitter_user_timeline("user_id", max_results=5)
```

## 📁 Estrutura dos Arquivos

```
jarvis/
├── modules/external_apis/
│   ├── __init__.py
│   ├── base_api.py          # Classe base para requisições HTTP
│   ├── api_manager.py       # Gerenciador central
│   ├── news_api.py          # Integração com notícias
│   ├── calendar_api.py      # Integração com calendários
│   ├── email_api.py         # Integração com emails
│   ├── social_api.py        # Integração com redes sociais
│   └── weather_api.py       # Integração com clima (já existia)
├── api_integration_hub.py   # Sistema principal (atualizado)
├── example_external_apis.py # Exemplo de uso
└── EXTERNAL_APIS_README.md  # Este arquivo
```

## 🔧 Funcionalidades Disponíveis

### NewsAPI
- `latest()`: Últimas notícias com filtros
- `from_rss()`: Leitura de feeds RSS/Atom

### CalendarAPI
- `google_list_events()`: Listar eventos Google Calendar
- `google_create_event()`: Criar evento Google Calendar
- `outlook_list_events()`: Listar eventos Outlook
- `outlook_create_event()`: Criar evento Outlook

### EmailAPI
- `gmail_list_messages()`: Listar mensagens Gmail
- `gmail_send_message()`: Enviar email via Gmail
- `outlook_list_messages()`: Listar mensagens Outlook
- `outlook_send_message()`: Enviar email via Outlook

### SocialMediaAPI
- `twitter_user_timeline()`: Timeline do usuário Twitter
- `twitter_post_tweet()`: Postar tweet
- `linkedin_post()`: Postar no LinkedIn

## 🛠️ Solução de Problemas

### Tokens Expirados
Os tokens OAuth têm validade limitada. Implemente refresh tokens para renovação automática.

### Permissões Insuficientes
Certifique-se de que suas apps têm as permissões corretas configuradas nos respectivos portais de desenvolvedores.

### Rate Limiting
Algumas APIs têm limites de requisições. O sistema implementa cache básico, mas considere implementar backoff exponencial.

### Logs de Debug
Para debugar problemas:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 Próximos Passos

- [ ] Implementar refresh automático de tokens OAuth
- [ ] Adicionar mais provedores de notícias
- [ ] Integrar com Slack/Discord
- [ ] Implementar webhooks para notificações em tempo real
- [ ] Adicionar suporte a anexos em emails
- [ ] Implementar análise de sentimento em redes sociais

## 🤝 Contribuição

Para adicionar uma nova integração:

1. Crie uma nova classe em `modules/external_apis/`
2. Herde de `BaseAPI` se precisar fazer requisições HTTP
3. Adicione a integração ao `APIManager`
4. Atualize este README com instruções de configuração

## ⚠️ Avisos Importantes

- **Segurança**: Nunca commite tokens ou chaves de API no código
- **Compliance**: Respeite os termos de uso de cada API
- **Privacy**: Implemente tratamento adequado de dados pessoais
- **Monitoring**: Monitore uso e custos das APIs pagas