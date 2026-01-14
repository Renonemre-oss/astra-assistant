import json
import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# Caminhos
BASE_DIR = os.path.dirname(__file__)
DATA_FILE = os.path.join(BASE_DIR, "dados", "intents.json")
MODEL_FILE = os.path.join(BASE_DIR, "modelo.pkl")

def treinar_modelo():
    """Treina um classificador de intenções e salva em disco."""
    # Carregar o ficheiro JSON
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    frases = []
    labels = []

    # Iterar sobre a lista de intenções dentro da chave "intents"
    for intent in data["intents"]:
        for pattern in intent["patterns"]:
            frases.append(pattern)
            labels.append(intent["tag"])

    # Vetorização TF-IDF
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(frases)

    # Modelo Naive Bayes
    modelo = MultinomialNB()
    modelo.fit(X, labels)

    # Salvar modelo + vectorizer
    joblib.dump((modelo, vectorizer), MODEL_FILE)
    print(f"✅ Modelo treinado e salvo em {MODEL_FILE}")

if __name__ == "__main__":
    treinar_modelo()
