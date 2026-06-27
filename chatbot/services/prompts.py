from .customer_service import get_customer_data
from ..models import Message


def get_customer_context(customer_id):
    customer = get_customer_data(customer_id)

    return f"""
Tên: {customer["name"]}
SĐT: {customer["phone"]}
Email: {customer["email"]}
"""

def get_history(customer_id):
    messages = Message.objects.filter(customer_id = customer_id).order_by("-created_at")[:20]
    if not messages.exists():
        return ""
    history = ""
    for msg in reversed(messages):
        history += f"{msg.sender}: {msg.content}\n"
    return history

def build_prompt(system_prompt = None ,customer_context = None ,history = None ,question = None, knowledge = None):
    return f"""
{system_prompt}

=== THÔNG TIN KHÁCH HÀNG ===
{customer_context}

=== LỊCH SỬ HỘI THOẠI ===
{history}

=== CÂU HỎI MỚI ===
{question}

=== KIẾN THỨC ===
{knowledge}

=== TRẢ LỜI ===
"""