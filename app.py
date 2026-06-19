from flask import Flask, jsonify, render_template
import json
from pathlib import Path

app = Flask(__name__)


TASKS_PATH = Path(__file__).parent / "data" / "tasks.json"


def load_modules():
    with TASKS_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


@app.route("/")
def index():
    modules = load_modules()
    return render_template("index.html", modules=modules)


@app.route("/api/modules")
def get_modules():
    return jsonify(load_modules())


@app.route("/api/modules/<module_id>")
def get_module(module_id):
    modules = load_modules()
    for module in modules:
        if module.get("id") == module_id:
            return jsonify(module)
    return jsonify({"error": "Module introuvable"}), 404


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
