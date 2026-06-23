from .llm import generate, ai_analysis, ai_task
from .customer_service import save_message, save_ai_analysis, save_ai_task

class CRMAgent:

    def run(self,customer_id,question):

        answer = generate(customer_id, question)

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
