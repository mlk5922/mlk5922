#core/services.py
from decimal import Decimal
from core import models  
from .models import Attendance, AuditLog, Notification, SalaryAdvance
from django.core.mail import send_mail
from django.conf import settings


class SalaryCalculator:
    @staticmethod
    def calculate_monthly_salary(employee, month, year):
        # Get base salary and daily rate
        base_salary = employee.base_salary
        daily_rate = employee.daily_salary
        
        # Get all absences for the month
        absences = Attendance.objects.filter(
            employee=employee,
            date__month=month,
            date__year=year,
            is_present=False
        ).count()
        
        # Calculate absence deductions
        absence_deduction = Decimal(absences) * daily_rate
        
        # Get approved advances for the month
        advances = SalaryAdvance.objects.filter(
            employee=employee,
            request_date__month=month,
            request_date__year=year,
            approved=True
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        
        # Calculate net salary
        net_salary = base_salary - absence_deduction - advances
        
        return {
            'base_salary': base_salary,
            'absences': absences,
            'absence_deduction': absence_deduction,
            'advances': advances,
            'net_salary': net_salary
        }

class NotificationService:
    @staticmethod
    def notify_users(users, title, message):
        for user in users:
            Notification.objects.create(
                user=user,
                title=title,
                message=message
            )
            
            if user.email:
                send_mail(
                    title,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=True
                )

class AuditService:
    @staticmethod
    def log_action(user, action, model_name, object_id, changes, request):
        AuditLog.objects.create(
            user=user,
            action=action,
            model_name=model_name,
            object_id=object_id,
            changes=changes,
            ip_address=request.META.get('REMOTE_ADDR')
        )