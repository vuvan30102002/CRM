from ..models import Customer, Message
from ..serializers import ListCustomer, AIMessageAnalysisSerializer, TaskSerializer
import json
from rest_framework import status
from rest_framework.response import Response

from .model_llm import search


def get_customer_data(customer_id):
    customer = Customer.objects.get(id=customer_id)
    serializer = ListCustomer(customer)
    return serializer.data

def save_message(customer_id,sender, content):
    message = Message.objects.create(
        customer_id = customer_id,
        sender = sender,
        content = content,
        channel = "website"
    )
    return message

def save_ai_analysis(customer_id, ai_analysis):
    analysis = json.loads(ai_analysis)
    analysis["customer"] = customer_id
    serializer = AIMessageAnalysisSerializer(data = analysis)
    if serializer.is_valid():
        return serializer.save()

    raise ValueError(serializer.errors)

def save_ai_task(customer_id, task):
    if not task:
        return
    task["customer"] = customer_id
    serializer = TaskSerializer(data = task)
    if serializer.is_valid():
        return serializer.save()

    raise ValueError(serializer.errors)


def get_knowledge(question):
    results = search(question)
    knowldege = []
    for result in results:
        knowldege.append(result.page_content)
    return knowldege
