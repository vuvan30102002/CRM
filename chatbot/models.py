from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('sales', 'Sales'),
        ('manager', 'Manager'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='sales'
    )

class Customer(models.Model):

    SOURCE_CHOICES = (
        ('facebook', 'Facebook'),
        ('website', 'Website'),
        ('zalo', 'Zalo'),
        ('tiktok', 'TikTok'),
    )

    STATUS_CHOICES = (
        ('new', 'Mới'),
        ('contacted', 'Đã liên hệ'),
        ('interested', 'Quan tâm'),
        ('negotiating', 'Đàm phán'),
        ('won', 'Thành công'),
        ('lost', 'Thất bại'),
    )

    name = models.CharField(max_length=100)

    phone = models.CharField(
        max_length=20,
        blank=True,
        unique=True
    )

    email = models.EmailField()

    source = models.CharField(
        max_length=30,
        choices=SOURCE_CHOICES
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='new'
    )

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customers'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Visitor(models.Model):

    visitor_id = models.UUIDField(
        unique=True
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="visitors"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    last_seen = models.DateTimeField(
        auto_now=True
    )

class Message(models.Model):

    SENDER_CHOICES = (
        ('customer', 'Customer'),
        ('sales', 'Sales'),
        ('ai', 'AI'),
    )

    CHANNEL_CHOICES = (
        ('facebook', 'Facebook'),
        ('zalo', 'Zalo'),
        ('email', 'Email'),
        ('website', 'Website'),
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='messages'
    )

    sender = models.CharField(
        max_length=20,
        choices=SENDER_CHOICES
    )

    content = models.TextField()

    channel = models.CharField(
        max_length=30,
        choices=CHANNEL_CHOICES
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.name} - {self.sender}"


class AIMessageAnalysis(models.Model):

    SENTIMENT_CHOICES = (
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative'),
    )

    TEMPERATURE_CHOICES = (
        ('hot', 'Hot'),
        ('warm', 'Warm'),
        ('cold', 'Cold'),
    )

    # message = models.OneToOneField(
    #     Message,
    #     on_delete=models.CASCADE,
    #     related_name='analysis'
    # )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    intent = models.CharField(max_length=100)

    sentiment = models.CharField(
        max_length=20,
        choices=SENTIMENT_CHOICES
    )

    lead_temperature = models.CharField(
        max_length=20,
        choices=TEMPERATURE_CHOICES
    )

    objection_type = models.CharField(
        max_length=255,
        blank=True
    )

    risk_score = models.IntegerField(default=0)

    ai_summary = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis #{self.id}"


class Task(models.Model):

    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )

    STATUS_CHOICES = (
        ('todo', 'Todo'),
        ('doing', 'Doing'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='tasks'
    )

    analysis = models.ForeignKey(
        AIMessageAnalysis,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks'
    )

    title = models.CharField(max_length=255)

    description = models.TextField(
        blank=True
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='todo'
    )

    due_date = models.DateTimeField(
        null=True,
        blank=True
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tasks'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Appointment(models.Model):

    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('missed', 'Missed'),
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='appointments'
    )

    meeting_time = models.DateTimeField()

    note = models.TextField(
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.name} - {self.meeting_time}"


class LeadScore(models.Model):

    LEVEL_CHOICES = (
        ('cold', 'Cold'),
        ('warm', 'Warm'),
        ('hot', 'Hot'),
    )

    customer = models.OneToOneField(
        Customer,
        on_delete=models.CASCADE,
        related_name='lead_score'
    )

    score = models.IntegerField(default=0)

    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.customer.name} - {self.score}"


class Opportunity(models.Model):

    STAGE_CHOICES = (
        ('prospecting', 'Prospecting'),
        ('qualified', 'Qualified'),
        ('proposal', 'Proposal'),
        ('negotiation', 'Negotiation'),
        ('closed_won', 'Closed Won'),
        ('closed_lost', 'Closed Lost'),
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='opportunities'
    )

    value = models.DecimalField(
        max_digits=15,
        decimal_places=2
    )

    stage = models.CharField(
        max_length=30,
        choices=STAGE_CHOICES,
        default='prospecting'
    )

    probability = models.IntegerField(
        default=0
    )

    close_date = models.DateField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.name} - {self.value}"


class AIReport(models.Model):

    GENERATED_BY_CHOICES = (
        ('openai', 'OpenAI'),
        ('gemini', 'Gemini'),
        ('claude', 'Claude'),
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='ai_reports'
    )

    report_content = models.TextField()

    generated_by = models.CharField(
        max_length=50,
        choices=GENERATED_BY_CHOICES
    )

    report_date = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Report #{self.id}"