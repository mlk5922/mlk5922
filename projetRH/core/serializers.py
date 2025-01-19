#core/serializers.py
from rest_framework import serializers
from .models import (
    User, CustomPermission, Employee, Service, Contract, Leave, LeaveBalance,
    Attendance, Salary, SalaryAdvance, Evaluation, Training, Skill, EmployeeSkill,
    JobPosting, JobApplication, Favorite, Document, Notification
)

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_hr', 'is_manager', 'is_employee']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

# Custom Permission Serializer
class CustomPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomPermission
        fields = [
            'user', 'can_manage_employees', 'can_manage_contracts', 'can_manage_leaves',
            'can_manage_salaries', 'can_manage_recruitment'
        ]

# Service Serializer
class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'code', 'description']

# Employee Serializer
class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    service = ServiceSerializer(read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'user', 'nom', 'prenom', 'code', 'gender', 'birth_date', 'hire_date',
            'address', 'phone', 'service', 'base_salary', 'daily_salary'
        ]

# Contract Serializer
class ContractSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = Contract
        fields = [
            'id', 'employee', 'type', 'start_date', 'end_date', 'monthly_salary',
            'daily_salary', 'is_active', 'archived', 'document'
        ]

# Leave Serializer
class LeaveSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = Leave
        fields = [
            'id', 'employee', 'type', 'start_date', 'end_date', 'status', 'approved'
        ]

# LeaveBalance Serializer
class LeaveBalanceSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = LeaveBalance
        fields = ['id', 'employee', 'year', 'annual_leave_balance', 'sick_leave_balance']

# Attendance Serializer
class AttendanceSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'employee', 'date', 'is_present']

# Salary Serializer
class SalarySerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = Salary
        fields = [
            'id', 'employee', 'month', 'year', 'base_salary', 'absences_deduction',
            'bonuses', 'net_salary'
        ]

# SalaryAdvance Serializer
class SalaryAdvanceSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = SalaryAdvance
        fields = ['id', 'employee', 'amount', 'reason', 'year', 'approved']

# Evaluation Serializer
class EvaluationSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    evaluator = UserSerializer(read_only=True)

    class Meta:
        model = Evaluation
        fields = [
            'id', 'employee', 'evaluator', 'date', 'performance_score', 'comments'
        ]

# Training Serializer
class TrainingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Training
        fields = '__all__'  

# Skill Serializer
class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'category', 'description', 'level', 'acquisition_date']

# EmployeeSkill Serializer
class EmployeeSkillSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    skill = SkillSerializer(read_only=True)

    class Meta:
        model = EmployeeSkill
        fields = ['id', 'employee', 'skill', 'level', 'acquired_date']

# JobPosting Serializer
class JobPostingSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)

    class Meta:
        model = JobPosting
        fields = ['id', 'title', 'description', 'contract_type', 'service', 'active']

# JobApplication Serializer
class JobApplicationSerializer(serializers.ModelSerializer):
    job_posting = JobPostingSerializer(read_only=True)
    candidate = UserSerializer(read_only=True)

    class Meta:
        model = JobApplication
        fields = [
            'id', 'job_posting', 'candidate', 'status', 'cv_file', 'cover_letter',
            'interview_date'
        ]

# Favorite Serializer
class FavoriteSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'name', 'url']

# Document Serializer
class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'title', 'file']

# Notification Serializer
class NotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'user', 'title', 'message', 'is_read']

# ModelSerializer with validation
class ValidatedModelSerializer(serializers.ModelSerializer):
    def validate(self, data):
        return data

# Using the new serializer
class ValidatedUserSerializer(ValidatedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_hr', 'is_manager', 'is_employee']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

# Using the new serializer
class ValidatedEmployeeSerializer(ValidatedModelSerializer):
    user = ValidatedUserSerializer(read_only=True)
    service = ServiceSerializer(read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'user', 'nom', 'prenom', 'code', 'gender', 'birth_date', 'hire_date',
            'address', 'phone', 'service', 'base_salary', 'daily_salary'
        ]#core/serializers.py
from rest_framework import serializers
from .models import (
    User, CustomPermission, Employee, Service, Contract, Leave, LeaveBalance,
    Attendance, Salary, SalaryAdvance, Evaluation, Training, Skill, EmployeeSkill,
    JobPosting, JobApplication, Favorite, Document, Notification
)

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_hr', 'is_manager', 'is_employee']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

# Custom Permission Serializer
class CustomPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomPermission
        fields = [
            'user', 'can_manage_employees', 'can_manage_contracts', 'can_manage_leaves',
            'can_manage_salaries', 'can_manage_recruitment'
        ]

# Service Serializer
class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'code', 'description']

# Employee Serializer
class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    service = ServiceSerializer(read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'user', 'nom', 'prenom', 'code', 'gender', 'birth_date', 'hire_date',
            'address', 'phone', 'service', 'base_salary', 'daily_salary'
        ]

# Contract Serializer
class ContractSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = Contract
        fields = [
            'id', 'employee', 'type', 'start_date', 'end_date', 'monthly_salary',
            'daily_salary', 'is_active', 'archived', 'document'
        ]

# Leave Serializer
class LeaveSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = Leave
        fields = [
            'id', 'employee', 'type', 'start_date', 'end_date', 'status', 'approved'
        ]

# LeaveBalance Serializer
class LeaveBalanceSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = LeaveBalance
        fields = ['id', 'employee', 'year', 'annual_leave_balance', 'sick_leave_balance']

# Attendance Serializer
class AttendanceSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'employee', 'date', 'is_present']

# Salary Serializer
class SalarySerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = Salary
        fields = [
            'id', 'employee', 'month', 'year', 'base_salary', 'absences_deduction',
            'bonuses', 'net_salary'
        ]

# SalaryAdvance Serializer
class SalaryAdvanceSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = SalaryAdvance
        fields = ['id', 'employee', 'amount', 'reason', 'year', 'approved']

# Evaluation Serializer
class EvaluationSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    evaluator = UserSerializer(read_only=True)

    class Meta:
        model = Evaluation
        fields = [
            'id', 'employee', 'evaluator', 'date', 'performance_score', 'comments'
        ]

# Training Serializer
class TrainingSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = Training
        fields = [
            'id', 'employee', 'title', 'description', 'start_date', 'end_date',
            'status', 'score', 'certificate'
        ]

# Skill Serializer
class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'category', 'description']

# EmployeeSkill Serializer
class EmployeeSkillSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    skill = SkillSerializer(read_only=True)

    class Meta:
        model = EmployeeSkill
        fields = ['id', 'employee', 'skill', 'level', 'acquired_date']

# JobPosting Serializer
class JobPostingSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)

    class Meta:
        model = JobPosting
        fields = ['id', 'title', 'description', 'contract_type', 'service', 'active']

# JobApplication Serializer
class JobApplicationSerializer(serializers.ModelSerializer):
    job_posting = JobPostingSerializer(read_only=True)
    candidate = UserSerializer(read_only=True)

    class Meta:
        model = JobApplication
        fields = [
            'id', 'job_posting', 'candidate', 'status', 'cv_file', 'cover_letter',
            'interview_date'
        ]

# Favorite Serializer
class FavoriteSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'name', 'url']

# Document Serializer
class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'title', 'file']

# Notification Serializer
class NotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'user', 'title', 'message', 'is_read']