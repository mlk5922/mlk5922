# core/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, CustomPermission, Employee, Service, Contract, Leave, LeaveBalance,
    Attendance, Salary, SalaryAdvance, Evaluation, Training, Skill, EmployeeSkill,
    JobPosting, JobApplication, Favorite, Document, AuditLog, Notification,
    Payslip, Bonus, Interview  
)

# Custom User Admin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_hr', 'is_manager', 'is_employee', 'is_staff')
    list_filter = ('is_hr', 'is_manager', 'is_employee', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('is_hr', 'is_manager', 'is_employee')}),
    )
    search_fields = ('username', 'email')

# Custom Permission Admin
class CustomPermissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'can_manage_employees', 'can_manage_contracts', 'can_manage_leaves', 'can_manage_salaries', 'can_manage_recruitment')
    search_fields = ('user__username',)
    list_filter = ('can_manage_employees', 'can_manage_contracts', 'can_manage_leaves', 'can_manage_salaries', 'can_manage_recruitment')

# Employee Admin

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'code', 'user', 'gender')
    list_filter = ('service', 'gender')
    search_fields = ('nom', 'prenom', 'code', 'user__username')
    raw_id_fields = ('user',)

# Service Admin
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'is_active')
    search_fields = ('code', 'description')
    list_filter = ('is_active',)
    list_editable = ('is_active',)

# Contract Admin
class ContractAdmin(admin.ModelAdmin):
    list_display = ('employee', 'type', 'start_date', 'end_date', 'is_active')
    search_fields = ('employee__nom', 'employee__prenom')
    list_filter = ('type', 'is_active')
    list_editable = ('is_active',)

# Leave Admin
class LeaveAdmin(admin.ModelAdmin):
    list_display = ('employee', 'type', 'start_date', 'end_date', 'status', 'approved')
    search_fields = ('employee__nom', 'employee__prenom')
    list_filter = ('type', 'status', 'approved')
    list_editable = ('status', 'approved')

# Salary Admin
class SalaryAdmin(admin.ModelAdmin):
    list_display = ('employee', 'month', 'year', 'base_salary', 'net_salary', 'is_paid')
    search_fields = ('employee__nom', 'employee__prenom')
    list_filter = ('month', 'year', 'is_paid')
    list_editable = ('is_paid',)

# Evaluation Admin
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('employee', 'evaluator', 'date', 'performance_score', 'is_completed')
    search_fields = ('employee__nom', 'employee__prenom')
    list_filter = ('date', 'performance_score', 'is_completed')
    list_editable = ('is_completed',)

# Training Admin
class TrainingAdmin(admin.ModelAdmin):
    list_display = ('employee', 'title', 'start_date', 'end_date', 'status', 'is_completed')
    search_fields = ('employee__nom', 'employee__prenom', 'title')
    list_filter = ('status', 'start_date', 'is_completed')
    list_editable = ('status', 'is_completed')

# Skill Admin
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_active')
    search_fields = ('name', 'category')
    list_filter = ('category', 'is_active')
    list_editable = ('is_active',)

# EmployeeSkill Admin
class EmployeeSkillAdmin(admin.ModelAdmin):
    list_display = ('employee', 'skill', 'level', 'acquisition_date', 'is_verified')
    list_filter = ('employee', 'skill', 'acquisition_date', 'is_verified')
    search_fields = ('employee__username', 'skill__name')

# JobPosting Admin
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('title', 'contract_type', 'service', 'active', 'is_filled')
    search_fields = ('title', 'contract_type', 'service__code')
    list_filter = ('contract_type', 'active', 'is_filled')
    list_editable = ('active', 'is_filled')

# JobApplication Admin
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('job_posting', 'candidate', 'status', 'interview_date', 'is_selected')
    search_fields = ('job_posting__title', 'candidate__username')
    list_filter = ('status', 'interview_date', 'is_selected')
    list_editable = ('status', 'is_selected')

# Favorite Admin
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'url', 'created_at', 'is_active')
    search_fields = ('user__username', 'name', 'url')
    list_filter = ('created_at', 'is_active')
    list_editable = ('is_active',)

# Document Admin
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'filename', 'created_at', 'is_verified')
    search_fields = ('title', 'filename')
    list_filter = ('created_at', 'is_verified')
    list_editable = ('is_verified',)

# AuditLog Admin
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'model_name', 'timestamp', 'is_resolved')
    search_fields = ('user__username', 'model_name')
    list_filter = ('action', 'timestamp', 'is_resolved')
    list_editable = ('is_resolved',)

# Notification Admin
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'is_read', 'created_at', 'is_archived')
    search_fields = ('user__username', 'title')
    list_filter = ('is_read', 'created_at', 'is_archived')
    list_editable = ('is_read', 'is_archived')

# Payslip Admin
class PayslipAdmin(admin.ModelAdmin):
    list_display = ('employee', 'month', 'year', 'base_salary', 'net_salary', 'is_paid')
    search_fields = ('employee__nom', 'employee__prenom')
    list_filter = ('month', 'year', 'is_paid')
    list_editable = ('is_paid',)

# Bonus Admin
class BonusAdmin(admin.ModelAdmin):
    list_display = ('employee', 'amount', 'date', 'is_approved')
    search_fields = ('employee__nom', 'employee__prenom')
    list_filter = ('date', 'is_approved')
    list_editable = ('is_approved',)

# Interview Admin
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('job_application', 'interviewer', 'date', 'status')
    search_fields = ('job_application__job_posting__title', 'interviewer__username')
    list_filter = ('status', 'date')
    list_editable = ('status',)

# Register Models
admin.site.register(User, CustomUserAdmin)
admin.site.register(CustomPermission, CustomPermissionAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Contract, ContractAdmin)
admin.site.register(Leave, LeaveAdmin)
admin.site.register(LeaveBalance)
admin.site.register(Attendance)
admin.site.register(Salary, SalaryAdmin)
admin.site.register(SalaryAdvance)
admin.site.register(Evaluation, EvaluationAdmin)
admin.site.register(Training, TrainingAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(EmployeeSkill, EmployeeSkillAdmin)
admin.site.register(JobPosting, JobPostingAdmin)
admin.site.register(JobApplication, JobApplicationAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(AuditLog, AuditLogAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Payslip, PayslipAdmin)  # Enregistrement de la nouvelle classe
admin.site.register(Bonus, BonusAdmin)  # Enregistrement de la nouvelle classe
admin.site.register(Interview, InterviewAdmin)  # Enregistrement de la nouvelle classe