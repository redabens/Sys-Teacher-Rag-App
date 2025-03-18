# Image de base avec Python 3.10
FROM python:3.10-slim

# Définition des variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    OLLAMA_HOST="http://ollama:11434"

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copie des fichiers de dépendances
COPY requirements.txt .

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie du reste du projet
COPY . .
COPY init-ollama.sh /init-ollama.sh
RUN chmod +x /init-ollama.sh

# Configuration de supervisord
# RUN mkdir -p /etc/supervisor/conf.d
# COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8000 8501

# CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
CMD ["honcho", "start"]
