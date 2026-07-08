# main.py
import os
from pathlib import Path
from dotenv import load_dotenv
import logging
from controller import run_experiment

# Configura o log para vermos o que está a acontecer no terminal
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Carrega as variáveis do ficheiro .env ao lado deste script
load_dotenv(dotenv_path=Path(__file__).with_name(".env"))

if not os.environ.get("OPENROUTER_API_KEY"):
    raise ValueError("OPENROUTER_API_KEY não foi carregada da .env.")

# ==========================================
# CONFIGURAÇÕES DA RODADA DO EXPERIMENTO
# ==========================================

# 1. Caminhos dos Ficheiros
# Substitua pelos caminhos reais no seu computador
QUESTIONS_CSV = "./dados/perguntas_scatter.csv"
DATA_CSV = "./dados/TABELA.csv"
IMAGE_PATH = "./dados/scatterplot.jpeg"
OUTPUT_CSV = "./resultados_experimento_mapa.csv"

# 2. Definições do Lote
DEBUG = False # Quando True, roda só a primeira pergunta e imprime o payload completo no terminal

# Quais modelos testar? (Nomes oficiais do OpenRouter)
MODELS_TO_TEST = [
    # ==========================================
    # 1. Modelos Rápidos (Foco em Agilidade / Custo-Benefício)
    # ==========================================
    "google/gemini-3.5-flash",      # Google Rápido
    "openai/gpt-5.4-mini",           # OpenAI Rápido
    "anthropic/claude-haiku-4.5",   # Anthropic Rápido
    
    # ==========================================
    # 2. Modelos de Maior Pensamento (Foco em Raciocínio Profundo / Pro)
    # ==========================================
    "google/gemini-3.1-pro-preview", # Google Pro (Preview)
    "openai/gpt-5.5",                 # OpenAI Pro 
    "anthropic/claude-opus-4.8"    # Anthropic Pro (Sonnet)
]
# Quais condições? 'T' (Tabela), 'G' (Imagem), 'GT' (Tabela + Imagem)
#CONDITIONS_TO_TEST = ['T', 'GT', 'G'] 
CONDITIONS_TO_TEST = ['T'] 
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
        debug=DEBUG
    )