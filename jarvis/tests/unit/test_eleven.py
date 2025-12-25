import requests
from pathlib import Path

# Obter API key do arquivo .env
env_file = Path('audio/.env')
api_key = None

if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            if line.startswith('ELEVENLABS_API_KEY='):
                api_key = line.split('=', 1)[1].strip()
                break

if api_key:
    print(f'🔑 API Key: {api_key[:10]}...')
    
    # Testar a API
    headers = {'xi-api-key': api_key}
    try:
        print('🧪 Testando conexão com ElevenLabs...')
        response = requests.get('https://api.elevenlabs.io/v1/user', headers=headers, timeout=10)
        print(f'📡 Status: {response.status_code}')
        
        if response.status_code == 200:
            user_info = response.json()
            print('✅ API Key válida!')
            
            # Testar vozes
            voices_response = requests.get('https://api.elevenlabs.io/v1/voices', headers=headers, timeout=10)
            if voices_response.status_code == 200:
                voices = voices_response.json().get('voices', [])
                print(f'🎤 {len(voices)} vozes encontradas!')
                print('\n📋 Primeiras vozes:')
                for i, voice in enumerate(voices[:5]):
                    labels = voice.get('labels', {})
                    print(f'  {i+1}. {voice.get("name", "Unknown")} ({labels.get("gender", "?")}) - ID: {voice.get("voice_id", "")[:8]}...')
            else:
                print(f'❌ Erro ao obter vozes: {voices_response.status_code}')
        else:
            print(f'❌ API Key inválida - Status: {response.status_code}')
            if response.status_code == 401:
                print('💡 Dica: Verifica se a chave não foi revogada no painel ElevenLabs')
                
    except Exception as e:
        print(f'❌ Erro: {e}')
else:
    print('❌ API Key não encontrada!')