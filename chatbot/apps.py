from django.apps import AppConfig
from .services.model_llm import load_db


class ChatbotConfig(AppConfig):
    name = 'chatbot'

    def ready(self):
        load_db()
