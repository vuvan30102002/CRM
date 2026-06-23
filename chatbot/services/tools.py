from google.genai import types


def send_email(email):
    return {
        "message" : f"Đã gửi xác nhận thành công đến email {email} của khách hàng",
        "status" : "successfully"
    }

send_email_tool = types.FunctionDeclaration(
    name = "send_email",
    description="Gửi email xác nhận cho khách hàng",
    parameters={
        "type" : "object",
        "properties" : {
            "email" : {
                "type" : "string",
                "description" : "email của khách hàng"
            }
        },
        "required" : ["email"]
    }
)

tools = [
    types.Tool(
        function_declarations=[
            send_email_tool
        ]
    )
]