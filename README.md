# Phase 2.9.0 - Boutons Memoire Serveur

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

## Phase 2.5.0

- Ajout de la route `POST /api/modules/<module_id>/buttons/<button_number>/confirm-sync`.
- La route confirme la tache (avec `days_remaining = cycle_days`), puis sauvegarde `data/tasks.json`.
- Réponse JSON compacte de succès :
  - `status = ok`
  - `event = confirm`
  - `module_id`
  - `module_name`
  - `confirmed_button` (avec `button`, `task_name`, `cycle_days`, `days_remaining`)
  - `buttons` (configuration compacte des boutons actifs).
- Gestion des erreurs JSON :
  - module introuvable
  - bouton introuvable
  - bouton desactive.
- Cette route est prévue pour la future passerelle ESP32-S3-Touch-LCD-5.
- Aucune communication ESP-NOW pour l'instant.
- Aucun code Arduino pour l'instant.

## Phase 2.6.0

- Ajout de la route `GET /api/modules/<module_id>/sync`.
- Route prévue pour la synchronisation globale d'un module EE05.
- Retour JSON avec `event = sync`.
- Retourne `server_time`.
- Retourne uniquement les boutons actifs au format compact (`button`, `task_name`, `cycle_days`, `days_remaining`).
- Gestion d'erreur module introuvable avec code HTTP 404.
- Aucune communication ESP-NOW pour l'instant.
- Aucun code Arduino pour l'instant.

## Phase 2.7.0

- Ajout d'un journal de confirmations dans `data/confirmations_log.json`.
- Journalisation des confirmations pour :
  - source `web` (interface web),
  - source `api` (POST /api/modules/<module_id>/buttons/<button_number>/confirm),
  - source `api_confirm_sync` (POST /api/modules/<module_id>/buttons/<button_number>/confirm-sync).
- Chaque entrée de journal contient :
  - `timestamp`, `source`, `module_id`, `module_name`, `button`, `task_name`, `cycle_days`, `days_remaining`.
- Ajout de la route `GET /api/confirmations-log` pour lire le journal.
- Aucune interface web du journal pour l’instant.
- Aucune base de données.
- Aucune communication ESP-NOW.

## Phase 2.8.0

- Affichage du journal dans la page principale.
- Les 20 confirmations les plus récentes sont affichées, du plus récent au plus ancien.
- Aucune suppression du journal.
- Aucun filtre ajouté.
- Aucun export CSV.
- Aucune pagination.
- Aucune communication ESP-NOW pour l'instant.

## Phase 2.9.0

- Ajout de last_confirmed_at comme date officielle de dernière confirmation.
- days_remaining est maintenant calculé dynamiquement à partir de cycle_days et last_confirmed_at.
- Les valeurs négatives de days_remaining sont supportées pour les tâches dépassées.
- GET /api/modules reste compatible avec la passerelle en continuant de retourner days_remaining.
- confirm-sync, la confirmation web et l'API de confirmation mettent maintenant last_confirmed_at à aujourd'hui.
- Migration douce des anciennes données : si last_confirmed_at manque, il est estimé depuis cycle_days et days_remaining.
- L'édition d'une tâche ne confirme pas la tâche.

Tests validés:

- Flask démarre correctement.
- La page web s'ouvre.
- GET /api/modules retourne days_remaining.
- Une ancienne date de confirmation donne un days_remaining négatif.
- confirm-sync remet la tâche au vert en mettant last_confirmed_at à aujourd'hui.
- La passerelle reste compatible sans modification.


