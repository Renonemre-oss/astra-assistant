# 🚀 ASTRA API Integration Hub

## 📋 Resumo
Sistema unificado para integração de múltiplas APIs que fornece dados em tempo real sobre:
- 📰 **Notícias** (Newsdata.io)  
- 📈 **Ações/Stocks** (Yahoo Finance)
- 💰 **Criptomoedas** (CoinGecko)
- 🌤️ **Clima** (OpenWeatherMap) - *Opcional*

## ✨ Principais Funcionalidades

### 🔄 **Cache Inteligente**
- Evita requisições desnecessárias
- Diferentes durações por tipo de dados
- Sistema otimizado de performance

### ⏰ **Scheduler Automático**
- **Notícias**: Atualiza a cada 5 minutos
- **Criptomoedas**: Atualiza a cada 30 segundos  
- **Ações**: Atualiza a cada 1 minuto
- **Clima**: Atualiza a cada 10 minutos

### 📊 **Dashboard Unificado**
- Interface visual limpa e organizada
- Dados em tempo real
- Indicadores visuais (🟢🔴 para alta/baixa)

## 🚀 Como Usar

### 1. **Execução Básica**
```bash
python api_integration_hub.py
```

### 2. **Opções Disponíveis**
- **Opção 1**: Dashboard único (executa uma vez)
- **Opção 2**: Modo automático com scheduler contínuo

### 3. **Configurar APIs Opcionais**
Para usar funcionalidades completas, descomente e configure suas API keys no código:

```python
# Exemplo de configuração
hub.set_api_key('openweather', 'YOUR_OPENWEATHER_API_KEY')
```

## 🔑 API Keys Necessárias

### ✅ **Já Funcionando (Sem configuração)**
- **Newsdata.io**: ✅ Configurado
- **CoinGecko**: ✅ API Pública (sem chave necessária)

### ⚙️ **Opcional (Requer configuração)**
- **OpenWeatherMap**: Para dados de clima
  - Site: https://openweathermap.org/api
  - Plano gratuito disponível

### ⚠️ **Com Limitações**
- **Yahoo Finance**: API gratuita com rate limits
  - Funciona para testes
  - Para produção, considere APIs pagas

## 📊 Exemplo de Saída

```
🚀 ASTRA API INTEGRATION HUB - DASHBOARD
================================================================================

📰 ÚLTIMAS NOTÍCIAS
--------------------------------------------------
  1. YouTube pagará 24,5 milhões de dólares para encerrar processo...
     📰 G1 - O Portal
  2. Gli imprenditori tornano a scuola
     📰 Unione

💰 CRIPTOMOEDAS  
--------------------------------------------------
  BTC: $112,938.00 🟢 +0.75%
  ETH: $4,154.55 🟢 +0.77%
  XRP: $2.84 🔴 -0.54%

⏰ Última atualização: 30/09/2025 11:44:09
```

## 🛠️ Tecnologias Utilizadas
- **Python 3.x**
- **requests**: Para chamadas HTTP
- **schedule**: Para agendamento automático
- **threading**: Para execução em background
- **dataclasses**: Para estruturas de dados
- **datetime**: Para manipulação de tempo

## 📁 Estrutura do Projeto

```
ASTRA/
├── api_integration_hub.py      # Arquivo principal
├── newsdata_api_script.py      # Script de notícias
├── API_HUB_README.md          # Este arquivo
└── ...outros arquivos do ASTRA
```

## 🔧 Personalização

### Adicionar Nova API
1. Crie uma nova classe seguindo o padrão das existentes
2. Adicione ao `SchedulerManager` se necessário
3. Inclua no `UnifiedDashboard`

### Modificar Intervalos de Atualização
```python
# Em SchedulerManager.start_scheduler()
schedule.every(X).minutes.do(self._update_something)
```

### Configurar Cache
```python
# Em ApiIntegrationHub.__init__()
self.cache_duration = {
    'news': 300,    # 5 minutos
    'crypto': 30,   # 30 segundos  
    # etc...
}
```

## 🐛 Solução de Problemas

### **Rate Limit (429 Error)**
- Yahoo Finance tem limites de requisições
- Use cache ou aguarde alguns minutos
- Considere APIs pagas para produção

### **Erro de Conexão**
- Verifique sua conexão com a internet
- Algumas APIs podem ter instabilidades temporárias

### **API Key Inválida**
- Verifique se a chave está correta
- Confirme se a API key não expirou

## 🚀 Próximos Passos

1. **Integrar com GUI do ASTRA**
2. **Adicionar banco de dados local**
3. **Implementar alertas personalizados**
4. **Criar API REST própria**
5. **Dashboard web**

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs de erro no terminal
2. Confirme que todas as dependências estão instaladas
3. Teste as APIs individualmente

---

**🎯 Status**: ✅ Funcionando
**🔄 Última atualização**: 30/09/2025
**👨‍💻 Desenvolvido para**: Projeto ASTRA
