# prompter.py
from typing import List, Dict, Optional

class Prompter:
    """
    Classe responsável por gerar os prompts para o experimento de Chart QA,
    garantindo o rigor metodológico das condições experimentais.
    """

    @staticmethod
    def get_system_instruction(condicao: str) -> str:
        """
        Gera a mensagem de sistema, estabelecendo as regras de resposta curta.
        Substitui as antigas diretrizes de Evidence Briefing pela regra do CQA.
        """
        base = "Você receberá {contexto} e uma pergunta sobre os dados. Responda de forma objetiva. Se a resposta for numérica, forneça apenas o valor. Se for um estado, forneça apenas o nome."
        
        if condicao == 'G':
            contexto = "um gráfico de dispersão"
        elif condicao == 'T':
            contexto = "uma tabela de dados"
        else:
            contexto = "um gráfico de dispersão e uma tabela de dados"
            
        return base.format(contexto=contexto)

    @staticmethod
    def build_payload(pergunta: str, condicao: str, tabela_texto: Optional[str] = None, base64_image: Optional[str] = None) -> List[Dict]:
        """
        Substitui o antigo 'get_researcher_human'.
        Constrói a lista de mensagens no formato exigido pela API multimodal.
        """
        system_message = Prompter.get_system_instruction(condicao)
        
        messages = [
            {"role": "system", "content": system_message}
        ]
        
        user_content = []
        
        # Injeta a tabela se a condição exigir
        if condicao in ['T', 'GT']:
            if not tabela_texto:
                raise ValueError(f"Condição '{condicao}' exige 'tabela_texto'.")
            texto_tabela = f"Aqui estão os dados:\n\n{tabela_texto}\n\nPergunta: {pergunta}"
            user_content.append({"type": "text", "text": texto_tabela})
        
        # Injeta a imagem se a condição exigir
        if condicao in ['G', 'GT']:
            if not base64_image:
                raise ValueError(f"Condição '{condicao}' exige 'base64_image'.")
            
            # Se for só imagem, a pergunta precisa entrar aqui
            if condicao == 'G':
                user_content.append({"type": "text", "text": f"Pergunta: {pergunta}"})
                
            user_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"
                }
            })
            
        messages.append({
            "role": "user",
            "content": user_content
        })
        
        return messages