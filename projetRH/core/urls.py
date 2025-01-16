# core/urls.py
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from .views import (
    ServiceViewSet, EmployeeViewSet, ContractViewSet,
    LeaveViewSet, SalaryViewSet, EvaluationViewSet,
    JobPostingViewSet, JobApplicationViewSet, FavoriteViewSet,
    DashboardViewSet, TrainingViewSet, EmployeeSkillViewSet, SkillViewSet, add_training_for_employee, apply_job, candidate_signup, carry_over_leave, customize_favorites, delete_salary, delete_training_for_employee, edit_salary, edit_training_for_employee, generate_performance_report_pdf, leave_balance,
    login_view, manage_dashboard, manage_employees, add_employee, edit_employee, delete_employee,
    manage_services, add_service, edit_service, delete_service, manage_trainings_for_employee, print_services,
    manage_contracts, add_contract, edit_contract, delete_contract, archive_contract,
    manage_leaves, record_attendance, request_leave, approve_leave, reject_leave,
    manage_salaries, generate_salary, generate_payslip, add_bonus,
    manage_evaluations, add_evaluation, edit_evaluation, generate_evaluation_report, generate_evaluation_report_pdf,
    manage_recruitment, post_job, request_salary_advance, schedule_interview,
    manage_favorites, add_favorite, edit_favorite, remove_favorite,
    manage_trainings, manage_skills, manage_employee_skills, grant_permissions,
    print_employees, employee_detail, custom_logout, add_evaluation_without_employee, verify_email,
    view_applications, update_application_status, job_posting_detail
)

# Configuration du router pour l'API
router = DefaultRouter()
router.register(r'services', ServiceViewSet)
router.register(r'employees', EmployeeViewSet)
router.register(r'contracts', ContractViewSet)
router.register(r'leaves', LeaveViewSet)
router.register(r'salaries', SalaryViewSet)
router.register(r'evaluations', EvaluationViewSet)
router.register(r'job-postings', JobPostingViewSet)
router.register(r'job-applications', JobApplicationViewSet)
router.register(r'favorites', FavoriteViewSet, basename='favorite')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'formations', TrainingViewSet)  
router.register(r'skills', SkillViewSet)
router.register(r'employee-skills', EmployeeSkillViewSet)

# Routes pour l'interface utilisateur
ui_urlpatterns = [
    path('', RedirectView.as_view(pattern_name='manage_dashboard'), name='home'),
    path('dashboard/', manage_dashboard, name='manage_dashboard'),
    path('employees/', manage_employees, name='manage_employees'),
    path('employees/print/', print_employees, name='print_employees'),
    path('employee/<int:employee_id>/', employee_detail, name='employee_detail'),
    path('services/', manage_services, name='manage_services'),
    path('services/print/', print_services, name='print_services'),
    path('contracts/', manage_contracts, name='manage_contracts'),
    path('leaves/', manage_leaves, name='manage_leaves'),
    path('salaries/', manage_salaries, name='manage_salaries'),
    path('evaluations/', manage_evaluations, name='manage_evaluations'),
    path('recruitment/', manage_recruitment, name='manage_recruitment'),
    path('favorites/', manage_favorites, name='manage_favorites'),
    path('trainings/', manage_trainings, name='manage_trainings'),  # Liste des formations
    path('skills/', manage_skills, name='manage_skills'),
    path('employee-skills/', manage_employee_skills, name='manage_employee_skills'),
    path('grant-permissions/', grant_permissions, name='grant_permissions'),
]

# Routes pour les vues fonctionnelles
functional_urlpatterns = [
    # Candidat
    path('candidate/signup/', candidate_signup, name='candidate_signup'),
    path('verify-email/', verify_email, name='verify_email'),

    # Employés
    path('add-employee/', add_employee, name='add_employee'),
    path('edit-employee/<int:employee_id>/', edit_employee, name='edit_employee'),
    path('delete-employee/<int:employee_id>/', delete_employee, name='delete_employee'),
    path('employees/print/', print_employees, name='print_employees'),
    path('employee/<int:employee_id>/generate-performance-report/', generate_performance_report_pdf, name='generate_performance_report_pdf'),

    # Services
    path('add-service/', add_service, name='add_service'),
    path('edit-service/<int:service_id>/', edit_service, name='edit_service'),
    path('delete-service/<int:service_id>/', delete_service, name='delete_service'),

    # Contrats
    path('add-contract/', add_contract, name='add_contract'),
    path('edit-contract/<int:contract_id>/', edit_contract, name='edit_contract'),
    path('delete-contract/<int:contract_id>/', delete_contract, name='delete_contract'),
    path('archive-contract/<int:contract_id>/', archive_contract, name='archive_contract'),

    # Congés
    path('request-leave/', request_leave, name='request_leave'),
    path('approve-leave/<int:leave_id>/', approve_leave, name='approve_leave'),
    path('reject-leave/<int:leave_id>/', reject_leave, name='reject_leave'),
    path('leave-balance/<int:employee_id>/', leave_balance, name='leave_balance'),
    path('carry-over-leave/', carry_over_leave, name='carry_over_leave'),

    # Salaires
    path('generate-salary/', generate_salary, name='generate_salary'),
    path('generate-payslip/<int:employee_id>/<int:month>/<int:year>/', generate_payslip, name='generate_payslip'),
    path('add-bonus/<int:employee_id>/', add_bonus, name='add_bonus'),
    path('record-attendance/', record_attendance, name='record_attendance'),
    path('request-salary-advance/', request_salary_advance, name='request_salary_advance'),
    path('salaries/edit/<int:salary_id>/', edit_salary, name='edit_salary'),
    path('salaries/delete/<int:salary_id>/', delete_salary, name='delete_salary'),

    # Évaluations
    path('add-evaluation/<int:employee_id>/', add_evaluation, name='add_evaluation'),
    path('add-evaluation/', add_evaluation_without_employee, name='add_evaluation_without_employee'),
    path('edit-evaluation/<int:evaluation_id>/', edit_evaluation, name='edit_evaluation'),
    path('evaluation-report/<int:employee_id>/', generate_evaluation_report, name='generate_evaluation_report'),
    path('evaluation-report-pdf/<int:employee_id>/', generate_evaluation_report_pdf, name='generate_evaluation_report_pdf'),

    # Recrutement
    path('post-job/', post_job, name='post_job'),
    path('view-applications/<int:job_posting_id>/', view_applications, name='view_applications'),
    path('update-application-status/<int:application_id>/', update_application_status, name='update_application_status'),
    path('schedule-interview/<int:job_application_id>/', schedule_interview, name='schedule_interview'),
    path('apply-job/<int:job_posting_id>/', apply_job, name='apply_job'),
    path('job-posting/<int:job_posting_id>/', job_posting_detail, name='job_posting_detail'),

    # Favoris
    path('add-favorite/', add_favorite, name='add_favorite'),
    path('edit-favorite/<int:favorite_id>/', edit_favorite, name='edit_favorite'),
    path('remove-favorite/<int:favorite_id>/', remove_favorite, name='remove_favorite'),
    path('customize-favorites/', customize_favorites, name='customize_favorites'),

    # Formations
    path('formations/', manage_trainings, name='manage_trainings'),  # Liste des formations
    path('employee/<int:employee_id>/trainings/', manage_trainings_for_employee, name='manage_trainings_for_employee'),  # Formations d'un employé spécifique
    path('employee/<int:employee_id>/add_training/', add_training_for_employee, name='add_training_for_employee'),
    path('training/<int:training_id>/edit/', edit_training_for_employee, name='edit_training_for_employee'),
    path('training/<int:training_id>/delete/', delete_training_for_employee, name='delete_training_for_employee'),
]

# Routes pour l'API
api_urlpatterns = [
    path('api/', include(router.urls)),
]

# Routes pour l'authentification
auth_urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', custom_logout, name='logout'),
]

# Combinaison de toutes les routes
urlpatterns = ui_urlpatterns + functional_urlpatterns + api_urlpatterns + auth_urlpatterns