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

def build_prompt(
    system_prompt=None,
    customer_context=None,
    history=None,
    question=None,
    knowledge=None,
    web_search=None,
):
    sections = []

    if system_prompt:
        sections.append(system_prompt)

    if customer_context:
        sections.append(f"=== THÔNG TIN KHÁCH HÀNG ===\n{customer_context}")

    if history:
        sections.append(f"=== LỊCH SỬ HỘI THOẠI ===\n{history}")

    if question:
        sections.append(f"=== CÂU HỎI MỚI ===\n{question}")

    if knowledge:
        sections.append(f"=== KIẾN THỨC ===\n{knowledge}")

    if web_search:
        sections.append(f"=== WEB SEARCH ===\n{web_search}")

    sections.append("=== TRẢ LỜI ===")

    return "\n\n".join(sections)