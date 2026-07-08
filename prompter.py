from typing import List, Dict, Optional

class Prompter:
    """
    Classe responsável por gerar os prompts para o experimento de Chart QA,
    garantindo o rigor metodológico das condições experimentais.
    """
    @staticmethod
    def get_system_instruction(condicao: str) -> str:
        """
        Gera a mensagem de sistema com introdução dinâmica para evitar falsas 
        expectativas visuais nos LLMs.
        """
        # Introdução ancorada estritamente na condição real
        if condicao == 'G':
            intro = "Você receberá uma imagem de um gráfico de dispersão que mostra dados sobre estados brasileiros."
        elif condicao == 'T':
            intro = "Você receberá uma tabela de dados sobre estados brasileiros."
        else:
            intro = "Você receberá uma imagem de um gráfico de dispersão e a tabela de dados correspondente sobre estados brasileiros."
            
        return (
            f"{intro}\n\n"
            "Instruções:\n"
            "1. Responda à pergunta de forma direta e concisa.\n"
            "2. Se a pergunta pedir um valor numérico, forneça o número. Se pedir o nome de um "
            "estado ou região, forneça o nome.\n"
            "3. Se a pergunta não puder ser respondida com base nas informações fornecidas — "
            "seja porque o dado não existe, a entidade mencionada não está no conjunto, ou a "
            "pergunta requer informações externas ou visuais que não estão presentes — responda "
            "claramente 'Não é possível responder com base nas informações fornecidas' e explique "
            "brevemente por quê em uma frase."
        )
    @staticmethod
    def build_payload(pergunta: str, condicao: str, tabela_texto: Optional[str] = None, base64_image: Optional[str] = None) -> List[Dict]:
        """
        Constrói o payload multimodal com a pergunta inserida no final.
        """
        system_message = Prompter.get_system_instruction(condicao)
        
        messages = [
            {"role": "system", "content": system_message}
        ]
        
        user_content = []
        
        # 1. Adiciona a tabela se houver
        if condicao in ['T', 'GT']:
            if not tabela_texto:
                raise ValueError(f"Condição '{condicao}' exige 'tabela_texto'.")
            user_content.append({"type": "text", "text": f"Dados da Tabela:\n{tabela_texto}"})
        
        # 2. Adiciona a imagem se houver
        if condicao in ['G', 'GT']:
            if not base64_image:
                raise ValueError(f"Condição '{condicao}' exige 'base64_image'.")
            
            user_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            })
            
        # 3. Adiciona a pergunta por último, garantindo que o modelo a veja após o contexto
        user_content.append({"type": "text", "text": f"Pergunta: {pergunta}"})
            
        messages.append({
            "role": "user",
            "content": user_content
        })
        
        return messages