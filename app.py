from flask import Flask, request, jsonify
from db import init_db, create_session, validate_session, close_expired_sessions
import openai
import os

app = Flask(__name__)
init_db()

@app.route("/login", methods=["POST"])
def login():
    user = request.json.get("user")
    key = request.json.get("key")

    VALID_KEYS = {
        "TOM": "RAD33T",
        "ANGEL": "RAD33A",
        "JORGE": "RAD33J",
        "NINJA": "RAD33N",
        "LUCIA": "RAD33L",
        "HECTOR": "RAD33H"
    }

    if not user or not key:
        return jsonify({"error": "Usuario y clave requeridos"}), 400

    if user not in VALID_KEYS or VALID_KEYS[user] != key:
        return jsonify({"error": "Credenciales incorrectas"}), 401

    close_expired_sessions(user)
    session_count = validate_session(user)

    if session_count >= 2:
        return jsonify({"error": "Ya hay 2 sesiones activas para este usuario"}), 403

    token = create_session(user)
    return jsonify({"token": token}), 200

@app.route("/analyze", methods=["POST"])
def analyze():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Token requerido"}), 401

    user, active = validate_session(token=token, return_user=True)
    if not active:
        return jsonify({"error": "Sesión no válida o expirada"}), 403

    prompt = request.json.get("prompt")
    if not prompt:
        return jsonify({"error": "Prompt requerido"}), 400

    openai.api_key = os.getenv("OPENAI_API_KEY")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un analista institucional experto en Smart Money Concepts (SMC), order blocks, estructura de mercado, liquidez, OTE y análisis multitemporal."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.5
        )

        result = response["choices"][0]["message"]["content"]
        return jsonify({"respuesta": result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
