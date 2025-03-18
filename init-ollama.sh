#!/bin/bash
echo "Attente du démarrage d'Ollama..."
sleep 10

echo "Vérification/Installation des modèles..."
ollama pull llama3
ollama pull nomic-embed-text

echo "Test du modèle..."
ollama run llama3 "test" > /dev/null 2>&1

echo "Initialisation terminée" 