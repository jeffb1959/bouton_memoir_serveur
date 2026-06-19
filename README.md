# Phase 2.0.0 — Boutons Mémoire Serveur

## Objectif

Cette phase met en place un serveur Flask minimal pour lire une configuration de modules et de boutons depuis un fichier JSON local (`data/tasks.json`) et l’afficher dans une page web simple.

## 1) Créer l’environnement virtuel

Ouvrez un terminal PowerShell dans le dossier du projet puis lancez :

```powershell
python -m venv .venv
```

## 2) Activer l’environnement (Windows PowerShell)

```powershell
. .venv\Scripts\Activate.ps1
```

## 3) Installer les dépendances

```powershell
pip install -r requirements.txt
```

## 4) Lancer le serveur

```powershell
python app.py
```

## 5) URLs de test

- http://127.0.0.1:5000
- http://127.0.0.1:5000/api/modules
- http://127.0.0.1:5000/api/modules/salle_bain
