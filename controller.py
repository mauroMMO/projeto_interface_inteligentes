# controller.py
import os
import logging
from data_loader import load_experiment_data, get_processed_combinations, save_result_incremental
from services import encode_image_to_base64
from prompter import Prompter
from model import OpenRouterModel

logger = logging.getLogger(__name__)

def run_experiment(
    questions_csv_path: str,
    data_csv_path: str,
    image_path: str,
    output_csv_path: str,
    models_to_test: list,
    conditions_to_test: list,
    is_pilot: bool = False
):
    """
    Função principal que orquestra o experimento de Chart QA.
    """
    # 1. Carrega os dados (Banco de Perguntas e Dados do IBGE)
    logger.info("A carregar os dados...")
    df_perguntas, df_dados = load_experiment_data(questions_csv_path, data_csv_path)
    
    # Prepara a tabela como string CSV pura (conforme conversamos)
    tabela_texto = df_dados.to_csv(index=False)
    
    # 2. Carrega a imagem em Base64 (se o ficheiro existir)
    base64_image = None
    if os.path.exists(image_path):
        base64_image = encode_image_to_base64(image_path)
    else:
        logger.warning(f"Atenção: Imagem não encontrada em {image_path}. Condições visuais falharão.")

    # 3. Descobre o que já foi processado para retomar de onde parou
    processed_set = get_processed_combinations(output_csv_path)
    
    # Limita a 5 perguntas se for a rodada piloto
    if is_pilot:
        logger.info("MODO PILOTO ATIVADO: Testando apenas as primeiras 5 perguntas.")
        df_perguntas = df_perguntas.head(5)

    # Verifica se a chave da API existe antes de começar
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY não está definida nas variáveis de ambiente.")

    # 4. Loop de Execução Aninhado
    for model_id in models_to_test:
        logger.info(f"=== Iniciando testes com o modelo: {model_id} ===")
        llm = OpenRouterModel(model_name=model_id, key=api_key)
        
        for condicao in conditions_to_test:
            logger.info(f"  -> Condição: {condicao}")
            
            for index, row in df_perguntas.iterrows():
                id_pergunta = str(row.get('ID')) # Ajuste se a sua coluna se chamar de forma diferente
                pergunta = str(row.get('Pergunta'))
                
                # Previne execução duplicada
                if (model_id, condicao, id_pergunta) in processed_set:
                    logger.debug(f"Pular: {model_id} | {condicao} | {id_pergunta} já respondida.")
                    continue
                
                logger.info(f"     * Perguntando ID: {id_pergunta}")
                
                # Monta o Payload dinamicamente dependendo da condição
                try:
                    payload = Prompter.build_payload(
                        pergunta=pergunta,
                        condicao=condicao,
                        tabela_texto=tabela_texto,
                        base64_image=base64_image
                    )
                except ValueError as ve:
                    logger.error(f"Erro ao montar payload para {id_pergunta}: {ve}")
                    continue

                # Chama a API (já blindada com retries no model.py)
                resposta_crua = llm.talk_to_model(messages=payload)
                
                # Monta o registo para salvar no CSV de saída
                result_dict = {
                    'Modelo': model_id,
                    'Condicao': condicao,
                    'ID_Pergunta': id_pergunta,
                    'Quadrante': str(row.get('Quadrante', '')),
                    'Categoria_Analitica': str(row.get('Categoria analítica', '')),
                    'Resposta_Crua': resposta_crua,
                    'Gabarito': str(row.get('Resposta esperada (gabarito)', '')),
                    'Tipo_Resposta': 'TBD', # A avaliação relaxada (±5%) será feita depois
                    'Erro_API': 'SIM' if resposta_crua == "ERRO_API_TIMEOUT" else 'NAO'
                }
                
                # Salva imediatamente esta linha no CSV (Persistência garantida)
                save_result_incremental(output_csv_path, result_dict)
                processed_set.add((model_id, condicao, id_pergunta))

    logger.info("=== Experimento Concluído! ===")