from .llm import generate_chitchat, generate_function_calling, generate_knowledge, ai_analysis, ai_task, intent_classifiter
from .customer_service import save_message, save_ai_analysis, save_ai_task, get_knowledge

class CRMAgent:

    def run(self,customer_id,question):

        intent = intent_classifiter(question)
        if intent == "FUNCTION":
            answer = generate_function_calling(customer_id, question)
        elif intent == "KNOWLEDGE":
            knowledge = get_knowledge(question)
            answer = generate_knowledge(customer_id, question, knowledge)
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
