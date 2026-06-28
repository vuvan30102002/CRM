from .llm import generate_chitchat, generate_function_calling, generate_knowledge, ai_analysis, ai_task, intent_classifiter, web_search
from .customer_service import save_message, save_ai_analysis, save_ai_task, get_knowledge, get_web_search
from tavily import TavilyClient
from dotenv import load_dotenv
import os, json
load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

client = TavilyClient(TAVILY_API_KEY)
class CRMAgent:

    def run(self,customer_id,question):

        intent = intent_classifiter(question)
        if intent == "FUNCTION":
            answer = generate_function_calling(customer_id, question)
        elif intent == "KNOWLEDGE":
            knowledge = get_knowledge(question)
            answer = generate_knowledge(customer_id, question, knowledge)
        elif intent == "WEB_SEARCH":
            result_web_search = get_web_search(client, question)
            answer = web_search(result_web_search, question)
        else:
            answer = generate_chitchat(customer_id, question)

        message = save_message(customer_id,"customer",question)

        save_message(customer_id,"ai",answer)

        # analysis = ai_analysis(customer_id)
        # save_ai_analysis(message.id, analysis)

        task = ai_task(question)
        if task.get("title"):
            save_ai_task(customer_id, task)

        return answer
    
agent = CRMAgent()

# response = agent.run(
#     customer_id=49,
#     question="Xin chào"
# )

# print(response)
