from flask import Flask, request, jsonify
import joblib
import pandas as pd
from pyngrok import ngrok

app = Flask(__name__)

try:
    pipeline = joblib.load('app/modelo_practico_optimizado.pkl')
    print("✅ Modelo cargado correctamente.")
except FileNotFoundError:
    print("❌ Error: modelo_practico_optimizado.pkl no encontrado.")
    pipeline = None

if pipeline is not None:
    @app.route('/predigo', methods=['POST'])
    def predigo():
        try:
            data = request.get_json(force=True)
            df_predict = pd.DataFrame([data])
            preds = pipeline.predict(df_predict)
            return jsonify({'prediction': int(preds[0])})
        except Exception as e:
            return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    # Crear túnel en puerto 5000
    public_url = ngrok.connect(5000)
    print("🌍 Tu API está disponible en:", public_url)
    app.run(port=5000)
