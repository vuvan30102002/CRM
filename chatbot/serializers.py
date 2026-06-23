from rest_framework import serializers
from .models import Customer, User, Task, Visitor, Message, AIMessageAnalysis

class ListUser(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id","username","email","password","role"]

class ListCustomer(serializers.ModelSerializer):
    assigned_role = serializers.CharField(
        source = 'assigned_to.role',
        read_only = True,
    )
    class Meta:
        model = Customer
        fields = ['id','name','phone','email','source','status','assigned_role', 'assigned_to']

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ["username","email","password","role"]
    def create(self, validate_data):
        role = validate_data.get("role")
        user = User.objects.create_user(**validate_data)
        if role == "admin":
            user.is_staff = True
        user.save()
        return user


class AdminCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['name','phone','email','source','status','assigned_to']

    def create(self, validated_data):
        customer = Customer.objects.create(**validated_data)
        return customer
    def update(self, instance, validate_data):
        for attr, value in validate_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id","customer","analysis","title","description","priority","status","due_date","created_by"]
    
    def create(self, validated_data):
        task = Task.objects.create(**validated_data)
        return task
    
    def update(self, instance, validate_data):
        for attr, value in validate_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
class VisitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visitor
        fields = ["visitor_id","customer","created_at"]

    def create(self, validated_data):
        visitor = Visitor.objects.create(**validated_data)
        return visitor
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["customer","sender","content","channel","created_at"]
    def create(self, validated_data):
        message = Message.objects.create(**validated_data)
        return message
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
class AIMessageAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIMessageAnalysis
        fields = [
            "customer",
            "intent",
            "sentiment",
            "lead_temperature",
            "objection_type",
            "risk_score",
            "ai_summary",
            "created_at",
        ]

    def create(self, validated_data):
        aianalysis = AIMessageAnalysis.objects.create(**validated_data)
        return aianalysis
    def update(self,instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

