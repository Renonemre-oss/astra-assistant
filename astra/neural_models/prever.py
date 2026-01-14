import os
import joblib

BASE_DIR = os.path.dirname(__file__)
MODEL_FILE = os.path.join(BASE_DIR, "modelo.pkl")

def prever_intencao(frase: str):
    """Classifica uma frase numa intenção (ex: pesquisar, lembrete, desligar)."""
    if not os.path.exists(MODEL_FILE):
        raise FileNotFoundError("⚠ Modelo não encontrado. Treina-o primeiro com modelo.py")

    modelo, vectorizer = joblib.load(MODEL_FILE)
    X = vectorizer.transform([frase])
    previsao = modelo.predict(X)[0]
    return previsao

if __name__ == "__main__":
    exemplos = [
        "procura músicas novas",
        "quero ver meus lembretes",
        "desliga por favor",
        "olá assistente"
    ]
    for frase in exemplos:
        print(f"💬 {frase} → 🎯 {prever_intencao(frase)}")
