from flask import Flask, jsonify, render_template, redirect, url_for, request
import json
from datetime import datetime
from pathlib import Path

app = Flask(__name__)


BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "tasks.json"
LOG_FILE = BASE_DIR / "data" / "confirmations_log.json"


@app.post("/button-event")
def button_event():
    """Reçoit un événement JSON envoyé par la passerelle ESP32."""
    payload = request.get_json(silent=True)
    print(payload)
    return jsonify({"ok": True}), 200


def load_data():
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_data(data):
    """Sauvegarde les donnees dans le fichier JSON."""
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def load_confirmation_log():
    """Charge le journal des confirmations."""
    if not LOG_FILE.exists():
        return {"confirmations": []}

    with LOG_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_confirmation_log(log_data):
    """Sauvegarde le journal des confirmations."""
    with LOG_FILE.open("w", encoding="utf-8") as file:
        json.dump(log_data, file, ensure_ascii=False, indent=2)


def _button_number(button, fallback):
    button_value = button.get("button")
    if button_value is None:
        return fallback

    try:
        return int(button_value)
    except (TypeError, ValueError):
        return fallback


def get_server_time_iso():
    """Retourne l'heure serveur au format ISO simple."""
    return datetime.now().isoformat(timespec="seconds")


def find_module(data, module_id):
    """Trouve un module par son identifiant."""
    modules = data.get("modules", []) if isinstance(data, dict) else data
    for module in modules:
        if module.get("id") == module_id:
            return module
    return None


def find_button(module, button_number):
    """Trouve un bouton dans un module."""
    for button in module.get("buttons", []):
        if button.get("button") == button_number:
            return button
    return None


def build_device_config_payload(module):
    """Construit une configuration compacte pour un module EE05."""
    buttons = []

    for button in module.get("buttons", []):
        if button.get("enabled", True):
            buttons.append({
                "button": button.get("button"),
                "task_name": button.get("task_name"),
                "cycle_days": button.get("cycle_days"),
                "days_remaining": button.get("days_remaining")
            })

    return {
        "module_id": module.get("id"),
        "module_name": module.get("name"),
        "buttons": buttons
    }


def add_confirmation_log_entry(source, module, button):
    """Ajoute une entree au journal des confirmations."""
    log_data = load_confirmation_log()

    entry = {
        "timestamp": get_server_time_iso(),
        "source": source,
        "module_id": module.get("id"),
        "module_name": module.get("name"),
        "button": button.get("button"),
        "task_name": button.get("task_name"),
        "cycle_days": button.get("cycle_days"),
        "days_remaining": button.get("days_remaining")
    }

    log_data.setdefault("confirmations", []).append(entry)
    save_confirmation_log(log_data)


@app.route("/")
def index():
    data = load_data()
    modules = data.get("modules", []) if isinstance(data, dict) else data

    for module in modules:
        for index, button in enumerate(module.get("buttons", []), start=1):
            button["button"] = _button_number(button, index)

    log_data = load_confirmation_log()
    confirmations = log_data.get("confirmations", [])
    recent_confirmations = list(reversed(confirmations))[:20]

    return render_template(
        "index.html",
        modules=modules,
        recent_confirmations=recent_confirmations
    )


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


@app.route("/api/modules/<module_id>/device-config")
def api_module_device_config(module_id):
    """Retourne une configuration simplifiee pour un module EE05."""
    data = load_data()

    module = find_module(data, module_id)
    if module is None:
        return jsonify({
            "status": "error",
            "error": "Module introuvable",
            "module_id": module_id
        }), 404

    device_config = build_device_config_payload(module)

    return jsonify({
        "status": "ok",
        "module_id": module.get("id"),
        "module_name": module.get("name"),
        "buttons": device_config["buttons"]
    })


@app.route("/api/modules/<module_id>/sync")
def api_module_sync(module_id):
    """Retourne l'etat officiel compact d'un module pour synchronisation."""
    data = load_data()

    module = find_module(data, module_id)
    if module is None:
        return jsonify({
            "status": "error",
            "event": "sync",
            "error": "Module introuvable",
            "module_id": module_id,
            "server_time": get_server_time_iso()
        }), 404

    payload = build_device_config_payload(module)

    return jsonify({
        "status": "ok",
        "event": "sync",
        "module_id": payload["module_id"],
        "module_name": payload["module_name"],
        "server_time": get_server_time_iso(),
        "buttons": payload["buttons"]
    })


@app.route("/api/modules/<module_id>/buttons/<int:button_number>/confirm-sync", methods=["POST"])
def api_confirm_task_sync(module_id, button_number):
    """Confirme une tache et retourne une synchronisation compacte pour le module EE05."""
    data = load_data()

    module = find_module(data, module_id)
    if module is None:
        return jsonify({
            "status": "error",
            "error": "Module introuvable",
            "module_id": module_id
        }), 404

    button = find_button(module, button_number)
    if button is None:
        return jsonify({
            "status": "error",
            "error": "Bouton introuvable",
            "module_id": module_id,
            "button": button_number
        }), 404

    if not button.get("enabled", True):
        return jsonify({
            "status": "error",
            "error": "Bouton desactive",
            "module_id": module_id,
            "button": button_number
        }), 400

    button["days_remaining"] = button.get("cycle_days", 0)
    save_data(data)
    add_confirmation_log_entry("api_confirm_sync", module, button)

    device_config = build_device_config_payload(module)

    return jsonify({
        "status": "ok",
        "event": "confirm",
        "module_id": module.get("id"),
        "module_name": module.get("name"),
        "confirmed_button": {
            "button": button.get("button"),
            "task_name": button.get("task_name"),
            "cycle_days": button.get("cycle_days"),
            "days_remaining": button.get("days_remaining")
        },
        "buttons": device_config["buttons"]
    })


@app.route("/modules/<module_id>/buttons/<int:button_number>/confirm", methods=["POST"])
def confirm_task(module_id, button_number):
    """Confirme une tache depuis l'interface web."""
    data = load_data()

    module = find_module(data, module_id)
    if module is None:
        return jsonify({"error": "Module introuvable"}), 404

    button = find_button(module, button_number)
    if button is None:
        return jsonify({"error": "Bouton introuvable"}), 404

    button["days_remaining"] = button.get("cycle_days", 0)
    save_data(data)
    add_confirmation_log_entry("web", module, button)
    return redirect(url_for("index"))


@app.route("/api/modules/<module_id>/buttons/<int:button_number>/confirm", methods=["POST"])
def api_confirm_task(module_id, button_number):
    """Confirme une tache depuis une API JSON pour la future passerelle."""
    data = load_data()

    module = find_module(data, module_id)
    if module is None:
        return jsonify({"status": "error", "error": "Module introuvable"}), 404

    button = find_button(module, button_number)
    if button is None:
        return jsonify({"status": "error", "error": "Bouton introuvable"}), 404

    if not button.get("enabled", True):
        return jsonify({
            "status": "error",
            "error": "Bouton desactive",
            "module_id": module_id,
            "button": button_number
        }), 400

    button["days_remaining"] = button.get("cycle_days", 0)
    save_data(data)
    add_confirmation_log_entry("api", module, button)

    return jsonify({
        "status": "ok",
        "module_id": module_id,
        "module_name": module.get("name"),
        "button": button.get("button"),
        "task_name": button.get("task_name"),
        "cycle_days": button.get("cycle_days"),
        "days_remaining": button.get("days_remaining"),
        "enabled": button.get("enabled", True)
    })


@app.route("/modules/<module_id>/buttons/<int:button_number>/edit", methods=["POST"])
def edit_task(module_id, button_number):
    """Modifie le nom, le cycle et l'etat actif d'une tache."""
    data = load_data()
    modules = data if isinstance(data, list) else data.get("modules", [])

    task_name = request.form.get("task_name", "").strip()
    cycle_days_raw = request.form.get("cycle_days", "").strip()
    enabled = request.form.get("enabled") == "on"

    if not task_name:
        return jsonify({"error": "Le nom de la tache est obligatoire"}), 400

    try:
        cycle_days = int(cycle_days_raw)
    except ValueError:
        return jsonify({"error": "Le delai doit etre un nombre entier"}), 400

    if cycle_days <= 0:
        return jsonify({"error": "Le delai doit etre superieur a zero"}), 400

    for module in modules:
        if module.get("id") == module_id:
            for idx, button in enumerate(module.get("buttons", []), start=1):
                if _button_number(button, idx) == button_number:
                    button["task_name"] = task_name
                    button["cycle_days"] = cycle_days
                    button["enabled"] = enabled
                    # Important :
                    # Ne pas modifier days_remaining ici.
                    # Changer le delai ne confirme pas la tache.
                    save_data(data)
                    return redirect(url_for("index"))

            return jsonify({"error": "Bouton introuvable"}), 404

    return jsonify({"error": "Module introuvable"}), 404


@app.route("/api/confirmations-log")
def api_confirmations_log():
    """Retourne le journal des confirmations."""
    return jsonify(load_confirmation_log())


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
