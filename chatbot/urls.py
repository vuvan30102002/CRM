from django.urls import path
from . import views

urlpatterns = [
    path("login_view", views.login_view, name = "login"),
    path("dashboard/", views.dashboard, name = "dashboard"),
    path("assignment/<int:customer_id>", views.assignment, name = "assignment"),
    path("update_view/<int:customer_id>", views.update_view, name = "updateView"),
    path("get_list_user", views.get_list_user, name = "listUser"),
    path("get_user_sale_and_manager", views.get_user_sale_and_manager, name = "listUserSaleAndManager"),
    path("create_user", views.create_user, name = "createUser"),

    # customer
    path("get_list_customer", views.CustomerListView.as_view(), name = "listCustomer"),
    path("get_customer/<int:customer_id>", views.get_customer, name = "getCustomer"),
    path("create_customer", views.create_customer, name = "createCustomer"),
    path("create_customer_front", views.create_customer_front, name = "createCustomer"),
    path("update_customer/<int:customer_id>", views.update_customer, name = "updateCustomer"),
    path("delete_customer/<int:customer_id>", views.delete_customer, name = "deleteCustomer"),

    # task
    path("create_task", views.create_task, name="createTask"),
    path("update_task/<int:task_id>", views.update_task, name="updateTask"),
    path("get_list_task", views.get_list_task, name="getListTask"),
    path("get_list_task_by_id/<int:customer_id>", views.get_list_task_by_id, name="getListTaskById"),

    # sales
    path("task_by_id/<int:customer_id>", views.task_by_id, name = "taskById"),

    # chatbot
    path("chatbot/", views.chatbot, name = "chatBot"),
    path("administration_chatbot/", views.administration_chatbot, name = "administrationChatBot"),

    # visitor
    path("check_visitor/<uuid:visitor_id>", views.check_visitor, name = "checkVisitor"),
    path("create_visitor/", views.create_visitor, name = "createVisitor"),
    path("get_list_visitor/", views.get_list_visitor, name = "getListVisitor"),

    # generate
    path("generate/", views.generate, name = "generate"),
    path("get_list_messages/<uuid:visitor_uuid>", views.get_list_messages, name = "getListMessages"),


    # ai analysis
    path("create_ai_analysis", views.create_ai_analysis, name = "AIAnalysis"),
    path("get_list_ai_analysis", views.get_list_ai_analysis, name = "getListAIAnalysis"),
    path("get_summary_ai_analysis/<int:customer_id>", views.get_summary_ai_analysis, name = "getSummaryAiAnalysis"),
    path("export_ai_analysis/<int:customer_id>",views.export_ai_analysis_excel,name="export_customers"),
    path("event_ai_analysis/<int:customer_id>", views.event_ai_analysis, name = "eventAiAnalysis"),

    # ask
    path("ask", views.ask, name = "ask"),



]