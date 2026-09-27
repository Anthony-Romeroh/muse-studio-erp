"""
WSGI entry point para Vercel
"""
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Import app después de configurar variables
from app import app

# Para Vercel Serverless Functions
if __name__ == "__main__":
    app.run()
