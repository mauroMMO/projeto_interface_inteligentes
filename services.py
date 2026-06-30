# services.py
import base64
import os

def encode_image_to_base64(image_path: str) -> str:
    """
    Lê um ficheiro de imagem (PNG/JPG) e retorna a sua representação codificada em Base64.
    
    Args:
        image_path (str): Caminho completo ou relativo para o ficheiro de imagem.
        
    Returns:
        str: String codificada em Base64 pronta para ser injetada no payload da API.
        
    Raises:
        FileNotFoundError: Se a imagem não existir no caminho especificado.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"ERRO: A imagem não foi encontrada no caminho: {image_path}")

    try:
        with open(image_path, "rb") as image_file:
            # Lê os bytes da imagem, codifica para base64 e converte para string utf-8
            base64_encoded = base64.b64encode(image_file.read()).decode('utf-8')
            return base64_encoded
    except Exception as e:
        raise RuntimeError(f"Erro ao tentar processar a imagem {image_path}: {str(e)}")