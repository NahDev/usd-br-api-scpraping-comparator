#!/usr/bin/env python3
"""Interface web (Flask): dashboard de cotações + painel de controle dos
robôs. O dashboard só lê os CSVs já gerados pelos scripts de coleta; o
painel de robôs pode disparar os scripts de verdade sob demanda.

Uso:
    python webapp/app.py
    (depois abra http://localhost:5001)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import robo 
from dados import montar_dados 
from flask import Flask, jsonify, render_template 

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/dados")
def api_dados():
    return jsonify(montar_dados())


@app.route("/robo")
def robo_painel():
    return render_template("robo.html")


@app.route("/api/robo/status")
def api_robo_status():
    return jsonify(robo.listar_status())


@app.route("/api/robo/rodar/<robo_id>", methods=["POST"])
def api_robo_rodar(robo_id):
    if robo_id not in robo.ROBOS:
        return jsonify({"erro": "robô desconhecido"}), 404

    iniciado = robo.rodar(robo_id)
    if not iniciado:
        return jsonify({"erro": "robô já está rodando"}), 409
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
