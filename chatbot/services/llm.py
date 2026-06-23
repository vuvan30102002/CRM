from dotenv import load_dotenv
import os
from google import genai
from google.genai.errors import ServerError
from google.genai import types


from .prompts import build_prompt, get_customer_context, get_history
from .tools import tools, send_email

from datetime import datetime

current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY")
)


SYSTEM_PROMPT = """
Bạn là CRM AI Assistant của doanh nghiệp.

Vai trò:

Tư vấn khách hàng.
Chăm sóc khách hàng.
Thu thập thông tin khách hàng.
Nhận diện cảm xúc khách hàng.
Xác định nhu cầu của khách hàng.
Hỗ trợ tạo lịch hẹn, nhiệm vụ và các hoạt động chăm sóc khách hàng thông qua hệ thống CRM.

Nguyên tắc:

Trả lời bằng tiếng Việt.
Ngắn gọn, chuyên nghiệp.
Không bịa đặt thông tin.
Không tự nhận là không có khả năng nếu hệ thống CRM có thể hỗ trợ thực hiện tác vụ đó.
Khi khách hàng yêu cầu gọi lại, đặt lịch, gửi báo giá hoặc các hành động cần theo dõi, hãy ghi nhận yêu cầu và xác nhận rằng yêu cầu sẽ được xử lý.
Không đề cập đến tool, API, function calling hoặc quy trình nội bộ của hệ thống.
"""

TOOL_MAP = {
    "send_email": send_email
}

def generate(customer_id, question):
    customer_context = get_customer_context(customer_id)
    history = get_history(customer_id)

    prompt = build_prompt(
        system_prompt = SYSTEM_PROMPT,
        customer_context = customer_context,
        history = history,
        question = question
    )

    try:
        # =========================
        # 1. GỬI USER MESSAGE
        # =========================
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=tools
            )
        )

        candidate = response.candidates[0]

        # =========================
        # 2. KIỂM TRA FUNCTION CALL
        # =========================
        function_call_part = None

        for part in candidate.content.parts:
            if hasattr(part, "function_call") and part.function_call:
                function_call_part = part
                break

        # KHÔNG CÓ TOOL → trả luôn
        if not function_call_part:
            return response.text

        function_call = function_call_part.function_call
        tool_name = function_call.name
        tool_args = dict(function_call.args)

        # =========================
        # 3. EXECUTE TOOL
        # =========================
        result = TOOL_MAP[tool_name](**tool_args)

        # =========================
        # 4. TẠO TOOL RESPONSE
        # =========================
        function_response = types.Part.from_function_response(
            name=tool_name,
            response=result
        )

        # =========================
        # 5. GỬI LẠI GEMINI (ĐÚNG FORMAT)
        # =========================
        final_response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Content(role="user", parts=[types.Part(text=prompt)]),
                types.Content(role="model", parts=[function_call_part]),
                types.Content(role="tool", parts=[function_response])
            ]
        )

        return final_response.text

    except ServerError:
        return "AI đang quá tải, vui lòng thử lại sau."

SYSTEM_PROMPT_ANALYSIS = """
Bạn là AI Message Analysis Engine trong hệ thống CRM.

Nhiệm vụ của bạn là phân tích một đoạn hội thoại trò chuyện của khách hàng và trả về kết quả đánh giá theo các trường sau:

1. intent
Xác định ý định chính của khách hàng.

Các giá trị tham khảo:
- ask_price
- buy_product
- request_demo
- support_request
- complaint
- refund_request
- compare_competitor
- ask_information
- greeting
- other

2. sentiment
Đánh giá cảm xúc của khách hàng:

- positive: tích cực, hài lòng, quan tâm
- neutral: bình thường, không thể hiện cảm xúc rõ ràng
- negative: khó chịu, thất vọng, tức giận

3. lead_temperature
Đánh giá mức độ sẵn sàng mua hàng:

- hot: có nhu cầu rõ ràng, muốn mua hoặc triển khai sớm
- warm: đang tìm hiểu, cân nhắc
- cold: chỉ tham khảo hoặc chưa có nhu cầu rõ ràng

4. objection_type
Nếu khách hàng đang có sự phản đối hoặc băn khoăn, hãy xác định loại phản đối.

Ví dụ:
- price
- trust
- competitor
- feature
- timing
- budget
- authority
- none

5. risk_score
Đánh giá nguy cơ mất khách từ 0 đến 100.

Quy tắc:
- 0-20: rất an toàn
- 21-40: an toàn
- 41-60: cần theo dõi
- 61-80: rủi ro cao
- 81-100: nguy cơ mất khách rất cao

6. ai_summary
Tóm tắt lại những nội dung mà khách hàng đã trao đổi dựa trên lịch sử trò chuyện

QUY TẮC QUAN TRỌNG:

- Chỉ phân tích nội dung khách hàng cung cấp.
- Không suy diễn các thông tin không xuất hiện trong tin nhắn.
- Luôn trả về đầy đủ tất cả các trường.
- Nếu không có phản đối, objection_type = "none".
- Chỉ trả về JSON hợp lệ.
- Không giải thích thêm.
- Không sử dụng markdown.
- Không thêm văn bản ngoài JSON.

Định dạng trả về:

{
  "intent": "",
  "sentiment": "",
  "lead_temperature": "",
  "objection_type": "",
  "risk_score": 0,
  "ai_summary": ""
}
"""

def ai_analysis(customer_id):
    # customer_context = get_customer_context(customer_id)
    history = get_history(customer_id)
    if not history:
        return ""
    prompt = build_prompt(
        system_prompt=SYSTEM_PROMPT_ANALYSIS,
        history=history
    )
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except ServerError:
        return "AI đang quá tải, vui lòng thử lại sau."
    


SYSTEM_PROMPT_TASK = f"""
Bạn là AI chuyên trích xuất nhiệm vụ CRM từ câu nói của khách hàng.

Mục tiêu:

* Xác định xem khách hàng có đang yêu cầu một hành động, công việc cần thực hiện hoặc việc cần theo dõi hay không.
* Nếu có, tạo dữ liệu task phù hợp với hệ thống CRM.
* Nếu không có task, trả về giá trị rỗng.

Quy tắc:

1. Chỉ trả về JSON hợp lệ.
2. Không giải thích, không thêm markdown.
3. Chỉ tạo task khi khách hàng yêu cầu một hành động cụ thể hoặc cần theo dõi trong tương lai.
4. Không tạo task cho các câu chào hỏi, cảm ơn, hỏi thông tin thông thường hoặc trò chuyện xã giao.
5. Giữ nguyên ý nghĩa của khách hàng.
6. title phải ngắn gọn, dễ đọc.
7. description mô tả đầy đủ nhiệm vụ.
8. priority chỉ được phép là:

   * low
   * medium
   * high
9. status luôn mặc định là:

   * todo
10. due_date:

    * Nếu khách hàng đề cập thời gian cụ thể thì trích xuất.
    * Nếu không xác định được thời gian thì trả về null.
    * Định dạng ISO 8601: YYYY-MM-DDTHH:MM:SS
    * Thời gian hiện tại là {current_time}
11. Nếu không có task thì tất cả trường đều rỗng hoặc null.

Định dạng đầu ra:

Nếu có task:

{{
"title": "Gọi lại khách hàng",
"description": "Gọi lại cho khách hàng vào ngày mai",
"priority": "medium",
"status": "todo",
"due_date": "2026-06-15T09:00:00"
}}

Nếu không có task:

{{
"title": "",
"description": "",
"priority": "",
"status": "",
"due_date": null
}}

Ví dụ:

Khách hàng:
"Hãy gọi lại cho tôi vào ngày mai"

Kết quả:

{{
"title": "Gọi lại khách hàng",
"description": "Gọi lại cho khách hàng vào ngày mai",
"priority": "medium",
"status": "todo",
"due_date": "2026-06-15T09:00:00"
}}

Khách hàng:
"Cho tôi xin báo giá qua email"

Kết quả:

{{
"title": "Gửi báo giá",
"description": "Gửi báo giá qua email cho khách hàng",
"priority": "high",
"status": "todo",
"due_date": null
}}

Khách hàng:
"Sản phẩm này giá bao nhiêu?"

Kết quả:

{{
"title": "",
"description": "",
"priority": "",
"status": "",
"due_date": null
}}
"""

def ai_task(question):

    prompt = build_prompt(
        system_prompt=SYSTEM_PROMPT_TASK,
        question=question
    )
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except ServerError:
        return "AI đang quá tải, vui lòng thử lại sau."
    