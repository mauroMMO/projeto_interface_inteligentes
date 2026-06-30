# main.py
import os
from dotenv import load_dotenv
import logging
from controller import run_experiment

# Configura o log para vermos o que está a acontecer no terminal
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Carrega as variáveis do ficheiro .env (onde deve estar a OPENROUTER_API_KEY)
load_dotenv()

# ==========================================
# CONFIGURAÇÕES DA RODADA DO EXPERIMENTO
# ==========================================

# 1. Caminhos dos Ficheiros
# Substitua pelos caminhos reais no seu computador
QUESTIONS_CSV = "./dados/Banco de perguntas OFICIAL (1).xlsx - Banco de Perguntas (Mapa).csv"
DATA_CSV = "./dados/Banco de perguntas OFICIAL (1).xlsx - Dados (Mapa).csv"
IMAGE_PATH = "./dados/mapa_brasil_renda.png" # Você precisa ter a imagem PNG do gráfico/mapa
OUTPUT_CSV = "./resultados_experimento_mapa.csv"

# 2. Definições do Lote
IS_PILOT = True # Mude para False quando quiser rodar as 40 perguntas

# Quais modelos testar? (Nomes oficiais do OpenRouter)
MODELS_TO_TEST = [
    "anthropic/claude-3.5-sonnet",
    "google/gemini-1.5-pro",
    "openai/gpt-4o"
]

# Quais condições? 'M' (Mapa), 'T' (Tabela), 'MT' (Mapa + Tabela)
# Se fosse o scatterplot, usaria 'G', 'T', 'GT'
CONDITIONS_TO_TEST = ['M', 'T', 'MT'] 

if __name__ == "__main__":
    logging.info("A iniciar o pipeline de Chart QA...")
    
    # Chama o controller passando todas as variáveis
    run_experiment(
        questions_csv_path=QUESTIONS_CSV,
        data_csv_path=DATA_CSV,
        image_path=IMAGE_PATH,
        output_csv_path=OUTPUT_CSV,
        models_to_test=MODELS_TO_TEST,
        conditions_to_test=CONDITIONS_TO_TEST,
        is_pilot=IS_PILOT
    )