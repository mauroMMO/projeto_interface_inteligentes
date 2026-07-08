from __future__ import annotations

import time
from typing import List, Optional, cast

from openai import RateLimitError
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import SecretStr


class OpenRouterModel:
	"""Interface fina para conversar com modelos do OpenRouter via LangChain."""

	def __init__(self, model_name: str, key: str, temperature: float = 0.0, max_retries: int = 3):
		self.model_name = model_name
		self.max_retries = max_retries
		self.model = ChatOpenAI(
			model=model_name,
			temperature=temperature,
			api_key=SecretStr(key),
			base_url="https://openrouter.ai/api/v1",
			default_headers={
				"HTTP-Referer": "https://openrouter.ai",
				"X-Title": "projeto_interface_inteligentes",
			},
		)

	def talk_to_model(
		self,
		messages: Optional[List[dict]] = None,
		system_message: Optional[str] = None,
		human_message: Optional[str] = None,
	) -> str:
		"""Envia mensagens ao modelo e devolve apenas o texto da resposta."""
		if messages is None:
			if system_message is None or human_message is None:
				raise ValueError("Forneça 'messages' ou o par 'system_message' e 'human_message'.")
			messages = [
				{"role": "system", "content": system_message},
				{"role": "user", "content": human_message},
			]

		langchain_messages = []
		for message in messages:
			role = message.get("role")
			content = message.get("content")
			if content is None:
				raise ValueError("Mensagem sem conteúdo não é suportada.")

			if role == "system":
				langchain_messages.append(SystemMessage(content=cast(str, content)))
			elif role == "user":
				langchain_messages.append(HumanMessage(content=content))
			else:
				raise ValueError(f"Papel de mensagem não suportado: {role}")

		for tentativa in range(1, self.max_retries + 1):
			try:
				response = self.model.invoke(langchain_messages)
				return str(response.content)
			except RateLimitError:
				if tentativa >= self.max_retries:
					return "ERRO_API_TIMEOUT"
				wait_seconds = 2 ** (tentativa - 1)
				time.sleep(wait_seconds)
			except ValueError as ve:
				mensagem_erro = str(ve)
				if "Upstream idle timeout exceeded" not in mensagem_erro and "'code': 504" not in mensagem_erro:
					raise

				if tentativa >= self.max_retries:
					return "ERRO_API_TIMEOUT"

				wait_seconds = 2 ** (tentativa - 1)
				time.sleep(wait_seconds)

		return "ERRO_API_TIMEOUT"