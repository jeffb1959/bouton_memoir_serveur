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

## Phase 2.1.0

Cette phase ajoute un bouton **Confirmer** pour chaque tâche dans la page principale.

Quand un utilisateur clique sur **Confirmer** :

- la valeur `days_remaining` est remise à `cycle_days` pour la tâche concernée;
- la modification est sauvegardée dans `data/tasks.json`;
- la page redirige vers l’affichage principal afin de montrer la nouvelle valeur.

Contraintes validées pour cette phase :

- aucune édition du nom;
- aucune édition du délai;
- aucune passerelle ESP-NOW;
- aucun code Arduino.

## Phase 2.2.0

Cette phase ajoute l'édition depuis l'interface web pour chaque bouton :

- `task_name` (nom de tâche),
- `cycle_days` (délai/cycle),
- `enabled` (état actif).

Règle importante :

- changer le délai ne confirme pas la tâche;
- `days_remaining` n'est pas modifié par l'édition.

Contraintes validées pour cette phase :

- aucune ajout/suppression de module;
- aucune ajout/suppression de bouton;
- aucune passerelle ESP-NOW;
- aucun code Arduino;
- aucune base de données.
