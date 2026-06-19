from flask import Flask, jsonify, render_template, redirect, url_for, request
import json
from pathlib import Path

app = Flask(__name__)


DATA_FILE = Path(__file__).parent / "data" / "tasks.json"


def load_data():
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_data(data):
    """Sauvegarde les données dans le fichier JSON."""
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def _button_number(button, fallback):
    if button.get("button") is not None:
        return button.get("button")

    button_id = button.get("id")
    if isinstance(button_id, str):
        digits = "".join(char for char in button_id if char.isdigit())
        if digits:
            return int(digits)

    return fallback


@app.route("/")
def index():
    modules = load_data()
    for module in modules:
        for index, button in enumerate(module.get("buttons", []), start=1):
            button["button"] = _button_number(button, index)
    return render_template("index.html", modules=modules)


@app.route("/api/modules")
def get_modules():
    return jsonify(load_data())


@app.route("/api/modules/<module_id>")
def get_module(module_id):
    modules = load_data()
    for module in modules:
        if module.get("id") == module_id:
            return jsonify(module)
    return jsonify({"error": "Module introuvable"}), 404


@app.route("/modules/<module_id>/buttons/<int:button_number>/confirm", methods=["POST"])
def confirm_task(module_id, button_number):
    """Confirme une tâche depuis l'interface web."""
    data = load_data()
    modules = data if isinstance(data, list) else data.get("modules", [])

    for module in modules:
        if module.get("id") == module_id:
            for idx, button in enumerate(module.get("buttons", []), start=1):
                if _button_number(button, idx) == button_number:
                    button["days_remaining"] = button.get("cycle_days", 0)
                    save_data(data)
                    return redirect(url_for("index"))

            return jsonify({"error": "Bouton introuvable"}), 404

    return jsonify({"error": "Module introuvable"}), 404


@app.route("/modules/<module_id>/buttons/<int:button_number>/edit", methods=["POST"])
def edit_task(module_id, button_number):
    """Modifie le nom, le cycle et l'état actif d'une tâche."""
    data = load_data()
    modules = data if isinstance(data, list) else data.get("modules", [])

    task_name = request.form.get("task_name", "").strip()
    cycle_days_raw = request.form.get("cycle_days", "").strip()
    enabled = request.form.get("enabled") == "on"

    if not task_name:
        return jsonify({"error": "Le nom de la tâche est obligatoire"}), 400

    try:
        cycle_days = int(cycle_days_raw)
    except ValueError:
        return jsonify({"error": "Le délai doit être un nombre entier"}), 400

    if cycle_days <= 0:
        return jsonify({"error": "Le délai doit être supérieur à zéro"}), 400

    for module in modules:
        if module.get("id") == module_id:
            for idx, button in enumerate(module.get("buttons", []), start=1):
                if _button_number(button, idx) == button_number:
                    button["task_name"] = task_name
                    button["cycle_days"] = cycle_days
                    button["enabled"] = enabled
                    # Important :
                    # Ne pas modifier days_remaining ici.
                    # Changer le délai ne confirme pas la tâche.
                    save_data(data)
                    return redirect(url_for("index"))

            return jsonify({"error": "Bouton introuvable"}), 404

    return jsonify({"error": "Module introuvable"}), 404


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
