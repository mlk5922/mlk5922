#core/permissions.py
from rest_framework.permissions import BasePermission
from .models import CustomPermission
from django.contrib.auth import get_user_model

User = get_user_model()

# Base Permission Classes
class IsHR(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_hr

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_manager

class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_employee

class IsOwnerOrHR(BasePermission):
    def has_object_permission(self, request, view, obj):
        # HR can access all records
        if request.user.is_hr:
            return True
        # Employees can only access their own records
        return hasattr(obj, 'employee') and obj.employee.user == request.user

# Custom Permission Base Class
class CustomPermissionBase(BasePermission):
    def __init__(self, permission_attribute):
        self.permission_attribute = permission_attribute

    def has_permission(self, request, view):
        if request.user.is_hr or request.user.is_manager:
            return True
        custom_permission = CustomPermission.objects.filter(user=request.user).first()
        if custom_permission:
            return getattr(custom_permission, self.permission_attribute, False)
        return False

# Specific Custom Permissions
class CanManageEmployees(CustomPermissionBase):
    def __init__(self):
        super().__init__('can_manage_employees')

class CanManageContracts(CustomPermissionBase):
    def __init__(self):
        super().__init__('can_manage_contracts')

class CanManageLeaves(CustomPermissionBase):
    def __init__(self):
        super().__init__('can_manage_leaves')

class CanManageSalaries(CustomPermissionBase):
    def __init__(self):
        super().__init__('can_manage_salaries')

class CanManageRecruitment(CustomPermissionBase):
    def __init__(self):
        super().__init__('can_manage_recruitment')

class CanManageTrainings(BasePermission):
    def __init__(self):
        super().__init__('can_manage_formation')

# Combined Permissions
class CanManageContractsOrSelf(BasePermission):
    def has_permission(self, request, view):
        return CanManageContracts().has_permission(request, view) or IsEmployee().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        return CanManageContracts().has_object_permission(request, view, obj) or IsEmployee().has_object_permission(request, view, obj)

class CanManageRecruitmentOrSelf(BasePermission):
    def has_permission(self, request, view):
        return CanManageRecruitment().has_permission(request, view) or IsEmployee().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        return CanManageRecruitment().has_object_permission(request, view, obj) or IsEmployee().has_object_permission(request, view, obj)

# Salary Access Permission
class SalaryAccessPermission(BasePermission):
    def has_permission(self, request, view):
        return CanManageSalaries().has_permission(request, view) or IsEmployee().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        return CanManageSalaries().has_object_permission(request, view, obj) or IsEmployee().has_object_permission(request, view, obj)

# Employee Self Access
class EmployeeSelfAccess(BasePermission):
    def has_permission(self, request, view):
        return IsEmployee().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        return hasattr(obj, 'employee') and obj.employee.user == request.user