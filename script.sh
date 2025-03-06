#!/bin/bash

# Activer l'environnement virtuel
source .venv/Scripts/activate

# Vérifier si l'activation a réussi
if [ $? -eq 0 ]; then
    echo "Environnement virtuel activé avec succès."

    pip install -r requirements.txt
    
    # Exécuter le script Python
    echo "Demarrage du scraping de udemy.com"
    python main.py
else
    echo "Erreur : Impossible d'activer l'environnement virtuel."
    exit 1
fi
