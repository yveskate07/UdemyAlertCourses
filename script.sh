#!/bin/bash

# Vérifier si on est sous Windows (Git Bash ou WSL)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

# Vérifier si l'activation a réussi
if [ $? -eq 0 ]; then
    echo "Environnement virtuel activé avec succès."

    pip install -r requirements.txt

    # Exécuter le script Python
    echo "Démarrage du scraping de udemy.com"
    python3 main.py
else
    echo "Erreur : Impossible d'activer l'environnement virtuel."
    exit 1
fi
