#!/bin/bash
echo "Attente du démarrage d'Ollama..."
while ! curl -s http://ollama:11434/api/tags > /dev/null; do
    echo "En attente d'Ollama..."
    sleep 5
done

echo "Vérification/Installation des modèles..."
# Pull llama3
curl -X POST http://ollama:11434/api/pull -d '{"name": "llama3"}'
while ! curl -s http://ollama:11434/api/show -d '{"name": "llama3"}' > /dev/null 2>&1; do
    echo "Téléchargement de llama3..."
    sleep 5
done

# Pull nomic-embed-text
curl -X POST http://ollama:11434/api/pull -d '{"name": "nomic-embed-text"}'
while ! curl -s http://ollama:11434/api/show -d '{"name": "nomic-embed-text"}' > /dev/null 2>&1; do
    echo "Téléchargement de nomic-embed-text..."
    sleep 5
done

echo "Test du modèle..."
curl -X POST http://ollama:11434/api/generate -d '{"model": "llama3", "prompt": "test"}'

echo "Initialisation terminée"