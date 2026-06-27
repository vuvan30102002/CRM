from django.shortcuts import render, redirect
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from .pagination import CustomerPagination

from .models import Customer, User, Task, Visitor, Message, AIMessageAnalysis
from .serializers import ListCustomer, AdminCustomerSerializer, UserCreateSerializer, ListUser, TaskSerializer, VisitorSerializer, MessageSerializer, AIMessageAnalysisSerializer

from .services.agent import CRMAgent

from .services.llm import ai_analysis
from .services.customer_service import save_ai_analysis
from .services.model_llm import search

from openpyxl import Workbook
# Create your views here.

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, 'login.html')

def dashboard(request):
    return render(request, 'dashboard.html')

def assignment(request, customer_id):
    return render(request, 'assignment.html', {"customer_id" : customer_id})

def update_view(request, customer_id):
    return render(request, "update.html", {"customer_id": customer_id})

def task_by_id(request, customer_id):
    return render(request, "sales/detail_task.html", {"customer_id": customer_id})

def chatbot(request):
    return render(request, "chat/chatbot.html")

def administration_chatbot(request):
    return render(request, "chat/administration_chatbot.html")


@api_view(["POST"])
@permission_classes([IsAdminUser])
def create_user(request):
    serializer = UserCreateSerializer(data = request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message":"Tao thanh cong user"},
            status=status.HTTP_201_CREATED
        )
    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(["GET"])
@permission_classes([IsAdminUser])
def get_list_user(request):
    userObj = User.objects.all()
    serializer = ListUser(userObj, many = True)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_customer(request, customer_id):
    customerObj = Customer.objects.get(id = customer_id)
    serializer = ListCustomer(customerObj)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAdminUser])
def get_user_sale_and_manager(request):
    userObj = User.objects.filter(role__in = ["sales","manager"])
    serializer = ListUser(userObj, many=True)
    return Response(serializer.data)

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_list_customer(request):
#     try:
#         if request.user.role == "admin" or request.user.role == "manager":
#             customers = Customer.objects.all()
#         else:
#             customers = Customer.objects.filter(
#                 assigned_to=request.user
#             )
#     except:
#         customers = Customer.objects.all()
#     serializer = ListCustomer(customers, many=True)
#     return Response({
#         "role": request.user.role,
#         "customers": serializer.data
#     })

class CustomerListView(ListAPIView):

    serializer_class = ListCustomer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomerPagination

    def get_queryset(self):

        user = self.request.user

        if user.role in ["admin", "manager"]:
            return Customer.objects.all().order_by("-id")

        return Customer.objects.filter(
            assigned_to=user
        ).order_by("-id")

    def list(self, request, *args, **kwargs):

        response = super().list(
            request,
            *args,
            **kwargs
        )

        response.data["role"] = request.user.role

        return response

@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_customer(request):
    serializer = AdminCustomerSerializer(data = request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message" : "Tao khach hang thanh cong"},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["PATCH", "PUT"])
@permission_classes([IsAdminUser])
def update_customer(request, customer_id):
    try:
        target_customer = Customer.objects.get(id = customer_id)
    except:
        return Response(
            {"error" : "Khong tim thay nguoi dung nay"},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = AdminCustomerSerializer(target_customer, data = request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message":"Admin da cap nhat thanh cong khach hang"},
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def delete_customer(request, customer_id):
    try:
        customer = Customer.objects.get(id = customer_id)
    except Customer.DoesNotExist:
        return Response(
            {"message":"Khach hang khong ton tai"},
            status=status.HTTP_404_NOT_FOUND
        )
    customer.delete()
    return Response(
        {"message":"Xoa khach hang thanh cong"},
        status=status.HTTP_200_OK
    )

@api_view(["POST"])
@permission_classes([IsAdminUser])
def create_task(request):
    serializer = TaskSerializer(data = request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message" : "Tao thanh cong task"},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["PUT","PATCH"])
@permission_classes([IsAuthenticated])
def update_task(request, task_id):
    try:
        target_task = Task.objects.get(id = task_id)
    except:
        return Response(
            {"message" : "Khong tim thay task nay"},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = TaskSerializer(target_task, data = request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message":"Da cap nhat task thanh cong"}
        )
    return Response(
        {"message" : "Khong cap nhat duoc tak"},
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(["GET"])
def get_list_task(request):
    taskObj = Task.objects.all()
    serializer = TaskSerializer(taskObj, many = True)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_list_task_by_id(request, customer_id):
    taskObj = Task.objects.filter(customer_id = customer_id)
    serializer = TaskSerializer(taskObj, many = True)
    return Response(serializer.data)

@api_view(["GET"])
def check_visitor(request, visitor_id):
    visitor = Visitor.objects.filter(
        visitor_id=visitor_id
    ).first()

    if visitor:
        return Response(
            {"message": "Da ton tai visitor"},
            status=status.HTTP_200_OK
        )

    return Response(
        {"message": "Khong tim thay visitor"},
        status=status.HTTP_404_NOT_FOUND
    )

@api_view(["POST"])
def create_visitor(request):
    visitorSeria = VisitorSerializer(data = request.data)
    if visitorSeria.is_valid():
        visitorSeria.save()
        return Response(
            {"message" : "Tao thanh cong visitor"},
            status=status.HTTP_201_CREATED
        )
    return Response(visitorSeria.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def get_list_visitor(request):
    visitorObj = Visitor.objects.all()
    serializer = VisitorSerializer(visitorObj, many = True)
    return Response(serializer.data)



@api_view(["POST"])
def create_customer_front(request):
    customer = Customer.objects.create(
        name=request.data.get("name"),
        phone=request.data.get("phone"),
        email=request.data.get("email"),
        source="website"
    )

    Visitor.objects.create(
        visitor_id=request.data.get("visitor_id"),
        customer=customer
    )

    return Response(
        {
            "message": "Tạo khách hàng thành công",
            "customer_id": customer.id
        },
        status=status.HTTP_201_CREATED
    )

agent = CRMAgent()

@api_view(["POST"])
def generate(request):
    visitor_id = request.data.get("visitor_id")
    question = request.data.get("question")
    visitor = Visitor.objects.get(
        visitor_id=visitor_id
    )
    customer_id = visitor.customer.id
    answer = agent.run(customer_id, question)
    return Response(
        {"message" : answer},
        status=status.HTTP_200_OK
    )


@api_view(["GET"])
def get_list_messages(request, visitor_uuid):
    visitor = Visitor.objects.filter(visitor_id = visitor_uuid).first()
    messageObj = Message.objects.filter(customer = visitor.customer).order_by("-created_at")[:21]
    serializer = MessageSerializer(messageObj, many=True)
    return Response(serializer.data)

@api_view(["POST"])
def create_ai_analysis(request):
    serializer = AIMessageAnalysisSerializer(data = request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message" : "Da tao thanh cong ai analysis"},
            status=status.HTTP_201_CREATED
        )
    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(["GET"])
def get_list_ai_analysis(request):
    analysisObj = AIMessageAnalysis.objects.all()
    serializer = AIMessageAnalysisSerializer(analysisObj, many=True)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_summary_ai_analysis(request, customer_id):
    summary = AIMessageAnalysis.objects.filter(customer = customer_id).values("ai_summary","created_at")
    return Response(list(summary))
    
# xuat file excel
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def export_ai_analysis_excel(request, customer_id):
    wb = Workbook()
    ws = wb.active
    ws.title = "AI Analysis"
    ws.append([
        "ID",
        "intent",
        "sentiment",
        "lead_temperature",
        "objection_type",
        "risk_score",
        "ai_summary",
        "created_at"
    ])
    ai_analysis = AIMessageAnalysis.objects.filter(message__customer_id = customer_id)
    for analysis in ai_analysis:
        ws.append([
            analysis.id,
            analysis.intent,
            analysis.sentiment,
            analysis.lead_temperature,
            analysis.objection_type,
            analysis.risk_score,
            analysis.ai_summary,
            analysis.created_at.strftime("%d/%m/%Y %H:%M:%S")
        ])
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response["Content-Disposition"] = (
        'attachment; filename="ai_analysis.xlsx"'
    )

    wb.save(response)

    return response




@api_view(["GET"])
@permission_classes([IsAuthenticated])
def event_ai_analysis(request, customer_id):
    try:
        analysis = ai_analysis(customer_id)
        if not analysis:
            return Response(
                {"message" : "Không có nội dung trò chuyện giữa khách hàng và bot"},
                status=status.HTTP_400_BAD_REQUEST
            ) 
        save_ai_analysis(customer_id, analysis)
        return Response(
                {"message" : "Đã lưu thành công analysis vào data"},
                status=status.HTTP_201_CREATED
            )
    except:
        return Response(
            {"message" : "Không lưu thành công analysis vào data"},
            status=status.HTTP_400_BAD_REQUEST
        )
    

@api_view(["GET"])
def ask(request):
    results = search(request.data.get("query"))
    return Response(
        {"message" : results},
        status=status.HTTP_201_CREATED
    )