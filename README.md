# Phase 2.0.0 - Boutons Memoire Serveur

## Objectif

Cette phase met en place un serveur Flask minimal pour lire une configuration de modules et de boutons depuis un fichier JSON local (`data/tasks.json`) et l'afficher dans une page web simple.

## 1) Creer l'environnement virtuel

Ouvrez un terminal PowerShell dans le dossier du projet puis lancez :

```powershell
python -m venv .venv
```

## 2) Activer l'environnement (Windows PowerShell)

```powershell
. .venv\Scripts\Activate.ps1
```

## 3) Installer les dependances

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

Cette phase ajoute un bouton de confirmation pour chaque tache dans la page principale.

Quand un utilisateur clique sur Confirmer:

- la valeur `days_remaining` est remise a `cycle_days` pour la tache concerne;
- la modification est sauvegardee dans `data/tasks.json`;
- la page redirige vers l'affichage principal afin de montrer la nouvelle valeur.

Contraintes valides pour cette phase :

- aucune edition du nom;
- aucune edition du delai;
- aucune passerelle ESP-NOW;
- aucun code Arduino.

## Phase 2.2.0

Cette phase ajoute l'edition depuis l'interface web pour chaque bouton :

- `task_name` (nom de tache),
- `cycle_days` (delai/cycle),
- `enabled` (etat actif).

Regle importante :

- changer le delai ne confirme pas la tache;
- `days_remaining` n'est pas modifie par l'edition.

Contraintes valides pour cette phase :

- aucune ajout/suppression de module;
- aucune ajout/suppression de bouton;
- aucune passerelle ESP-NOW;
- aucun code Arduino;
- aucune base de donnees.

## Phase 2.2.1

- Nettoyage du modele JSON : suppression des champs `task_id` et `id` sur chaque bouton.
- Conservation de la structure cible par bouton :
  - `button`
  - `task_name`
  - `cycle_days`
  - `days_remaining`
  - `enabled`
- Le vrai identifiant technique d'un bouton reste `module_id + button`.
- La logique de confirmation reste inchangée.
- La logique d'edition reste inchangée.

## Phase 2.3.0

- Ajout d'une route API de confirmation pour la future passerelle:
  - POST /api/modules/<module_id>/buttons/<button_number>/confirm
- La confirmation API met a jour `days_remaining = cycle_days`.
- La confirmation API sauvegarde `data/tasks.json`.
- Reponse JSON en cas de succes:
  - `status` = `ok`
  - `module_id`, `module_name`, `button`, `task_name`, `cycle_days`, `days_remaining`, `enabled`
- Reponses JSON d'erreur:
  - `status` = `error` + `error` si module introuvable,
  - `status` = `error` + `error` si bouton introuvable,
  - `status` = `error` + `error` si bouton desactive.
- Aucune communication ESP-NOW.
- Aucun code Arduino.
- Aucune base de donnees.

## Phase 2.4.0

- Ajout de la route `GET /api/modules/<module_id>/device-config`.
- Route prévue pour la passerelle/ module EE05.
- Retourne un JSON compact avec `status`, `module_id`, `module_name`, `buttons`.
- `buttons` contient uniquement les boutons actifs (`enabled = true`).
- Chaque bouton retourné expose :
  - `button`
  - `task_name`
  - `cycle_days`
  - `days_remaining`
- En cas de module introuvable, retourne `{"status":"error","error":"Module introuvable","module_id":"<module_id>"}` avec HTTP 404.
- Aucune communication ESP-NOW pour l'instant.
- Aucun code Arduino pour l'instant.
