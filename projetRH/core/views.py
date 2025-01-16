from datetime import date, timedelta
from django.http import HttpResponse
from django.db.models import ProtectedError
from django.contrib import messages
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from decimal import Decimal
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count, Sum
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
import plotly.express as px
import pandas as pd
from datetime import date, timedelta
from rest_framework.response import Response
from .models import (
    Attendance, Employee, Contract, Leave, LeaveBalance, PerformanceStats, Salary, Evaluation, JobPosting,
    JobApplication, Favorite, Training, Skill, EmployeeSkill, Service, Payslip, Bonus, Interview, DiversityStats, User
)
from .serializers import (
    EmployeeSerializer, ContractSerializer, LeaveSerializer,
    SalarySerializer, EvaluationSerializer, JobPostingSerializer,
    JobApplicationSerializer, FavoriteSerializer, TrainingSerializer,
    SkillSerializer, EmployeeSkillSerializer, ServiceSerializer
)
from .forms import (
    CandidateSignUpForm, CustomPermissionForm, EmployeeForm, EvaluationForm, ContractForm,
    LeaveForm, SalaryAdvanceForm, SalaryForm, JobPostingForm, ServiceForm, FavoriteForm, BonusForm, InterviewForm,
    JobApplicationForm, TrainingForm
)

# Vue de connexion
def login_view(request):
    """
    Vue pour gérer la connexion des utilisateurs.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('manage_dashboard')  # Redirection vers le tableau de bord après la connexion
        else:
            return render(request, 'login.html', {'error': 'Nom d\'utilisateur ou mot de passe invalide'})
    return render(request, 'login.html')

# Vue pour logout
def custom_logout(request):
    logout(request)  # Déconnecte l'utilisateur
    return redirect('home')  # Redirige vers la page d'accueil

# Vue du tableau de bord
@login_required
def manage_dashboard(request):
    try:
        # Statistiques de base
        total_employees = Employee.objects.count()
        active_contracts = Contract.objects.filter(is_active=True).count()
        pending_leaves = Leave.objects.filter(status='PENDING').count()
        total_salaries = Salary.objects.aggregate(total_salaries=Sum('net_salary'))['total_salaries'] or 0
        recent_evaluations = Evaluation.objects.filter(date__gte=date.today() - timedelta(days=30)).count()
        open_job_postings = JobPosting.objects.filter(active=True).count()

        # Statistiques sur les services
        total_services = Service.objects.count()
        employees_by_service = Employee.objects.select_related('service').values('service__description').annotate(count=Count('id'))

        # Favoris de l'utilisateur
        favorites = Favorite.objects.filter(user=request.user).order_by('order')

        # Statistiques de diversité
        diversity_stats = DiversityStats.objects.all()
        diversity_data = {
            'male_count': diversity_stats.aggregate(Sum('male_count'))['male_count__sum'] or 0,
            'female_count': diversity_stats.aggregate(Sum('female_count'))['female_count__sum'] or 0,
            'other_count': diversity_stats.aggregate(Sum('other_count'))['other_count__sum'] or 0,
        }

        # Graphique de diversité
        diversity_df = pd.DataFrame(list(diversity_stats.values('year', 'male_count', 'female_count', 'other_count')))
        diversity_fig_html = "<p>Aucune donnée de diversité disponible.</p>"
        if not diversity_df.empty:
            diversity_fig = px.bar(diversity_df, x='year', y=['male_count', 'female_count', 'other_count'], 
                                   title="Répartition par genre", labels={'value': 'Nombre', 'variable': 'Genre'})
            diversity_fig_html = diversity_fig.to_html()

        # Statistiques des contrats
        contract_stats = Contract.objects.values('type').annotate(count=Count('id'))
        contract_data = {stat['type']: stat['count'] for stat in contract_stats}

        # Graphique des types de contrats
        contract_df = pd.DataFrame(list(contract_stats))
        contract_fig_html = "<p>Aucune donnée de contrat disponible.</p>"
        if not contract_df.empty:
            contract_fig = px.pie(contract_df, values='count', names='type', title="Répartition des types de contrats")
            contract_fig_html = contract_fig.to_html()

        # Statistiques des performances
        performance_stats = PerformanceStats.objects.values('year').annotate(avg_score=Avg('performance_score'))
        performance_data = {stat['year']: stat['avg_score'] for stat in performance_stats}

        # Graphique des performances
        performance_df = pd.DataFrame(list(performance_stats))
        performance_fig_html = "<p>Aucune donnée de performance disponible.</p>"
        if not performance_df.empty:
            performance_fig = px.line(performance_df, x='year', y='avg_score', title="Performance moyenne par année")
            performance_fig_html = performance_fig.to_html()

        # Statistiques des absences
        absence_stats = Leave.objects.values('type').annotate(count=Count('id'))
        absence_data = {stat['type']: stat['count'] for stat in absence_stats}

        # Graphique des absences
        absence_df = pd.DataFrame(list(absence_stats))
        absence_fig_html = "<p>Aucune donnée d'absence disponible.</p>"
        if not absence_df.empty:
            absence_fig = px.bar(absence_df, x='type', y='count', title="Répartition des types de congés")
            absence_fig_html = absence_fig.to_html()

        # Statistiques des salaires par service
        salaries_by_service = Employee.objects.select_related('service').values('service__description').annotate(total_salary=Sum('base_salary'))
        salary_df = pd.DataFrame(list(salaries_by_service))
        salary_fig_html = "<p>Aucune donnée de salaire disponible.</p>"
        if not salary_df.empty:
            salary_fig = px.bar(salary_df, x='service__description', y='total_salary', 
                                title="Répartition des salaires par service", labels={'service__description': 'Service', 'total_salary': 'Salaire total'})
            salary_fig_html = salary_fig.to_html()

        context = {
            'total_employees': total_employees,
            'active_contracts': active_contracts,
            'pending_leaves': pending_leaves,
            'total_salaries': total_salaries,
            'recent_evaluations': recent_evaluations,
            'open_job_postings': open_job_postings,
            'total_services': total_services,
            'employees_by_service': employees_by_service,
            'favorites': favorites,
            'diversity_data': diversity_data,
            'diversity_fig': diversity_fig_html,
            'contract_data': contract_data,
            'contract_fig': contract_fig_html,
            'performance_data': performance_data,
            'performance_fig': performance_fig_html,
            'absence_data': absence_data,
            'absence_fig': absence_fig_html,
            'salary_fig': salary_fig_html,
        }
        return render(request, 'dashboard.html', context)

    except Exception as e:
        # Gestion des erreurs
        print(f"Erreur dans manage_dashboard: {e}")
        messages.error(request, "Une erreur s'est produite lors du chargement du tableau de bord.")
        return render(request, 'dashboard.html', {})

# Vues pour les candidats
from .utils import generate_verification_code, send_verification_email
def candidate_signup(request):
    """
    Vue pour gérer l'inscription des candidats.
    """
    if request.method == 'POST':
        # Si le formulaire est soumis, valider les données
        form = CandidateSignUpForm(request.POST)
        if form.is_valid():
            # Sauvegarder l'utilisateur
            user = form.save()
            # Générer un code de validation
            user.verification_code = generate_verification_code()
            user.save()
            # Envoyer le code par e-mail
            send_verification_email(user)
            # Afficher un message de succès
            messages.success(request, "Un code de validation a été envoyé à votre adresse e-mail.")
            # Rediriger vers la page de vérification
            return redirect('verify_email')
    else:
        # Afficher un formulaire vide si la méthode est GET
        form = CandidateSignUpForm()
    # Rendre le template avec le formulaire
    return render(request, 'candidate_signup.html', {'form': form})

def verify_email(request):
    """
    Vue pour vérifier le code de validation reçu par e-mail.
    """
    if request.method == 'POST':
        # Récupérer l'e-mail et le code saisis par l'utilisateur
        email = request.POST.get('email')
        code = request.POST.get('code')
        try:
            # Vérifier si l'utilisateur et le code correspondent
            user = User.objects.get(email=email, verification_code=code)
            # Activer le compte
            user.is_active = True
            # Supprimer le code de validation après vérification
            user.verification_code = None
            user.save()
            # Connecter l'utilisateur
            login(request, user)
            # Afficher un message de succès
            messages.success(request, "Votre compte a été activé avec succès.")
            # Rediriger vers la page d'accueil
            return redirect('home')
        except User.DoesNotExist:
            # Afficher un message d'erreur si le code est invalide
            messages.error(request, "Code de validation invalide ou e-mail incorrect.")
    # Rendre le template de vérification
    return render(request, 'verify_email.html')

# Vues pour les employés avec recherche et filtrage
@login_required
def manage_employees(request):
    """
    Vue pour gérer la liste des employés avec recherche et filtrage.
    """
    query = request.GET.get('q')
    service_filter = request.GET.get('service')
    employees = Employee.objects.all()

    if query:
        employees = employees.filter(
            Q(nom__icontains=query) | Q(prenom__icontains=query) | Q(code__icontains=query)
        )

    if service_filter:
        employees = employees.filter(service__id=service_filter)

    services = Service.objects.all()
    return render(request, 'employees.html', {'employees': employees, 'services': services})

@login_required
def print_employees(request):
    """
    Vue pour imprimer la liste des employés.
    """
    employees = Employee.objects.all()
    html_string = render_to_string('print_employees.html', {'employees': employees})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="liste_employes.pdf"'

    # Convertir le HTML en PDF
    pisa_status = pisa.CreatePDF(html_string, dest=response)
    if pisa_status.err:
        return HttpResponse("Erreur lors de la génération du PDF", status=500)

    return response
def add_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            employee = form.save()
            employee.trainings.set(form.cleaned_data['trainings'])  # Associer les formations
            messages.success(request, "Employé ajouté avec succès!")
            return redirect('manage_employees')
    else:
        form = EmployeeForm()

    users = User.objects.filter(employee__isnull=True)
    services = Service.objects.all()
    trainings = Training.objects.all()  # Récupérer toutes les formations
    return render(request, 'add_employee.html', {
        'form': form,
        'users': users,
        'services': services,
        'trainings': trainings,  # Passer les formations au template
    })
@login_required
def edit_employee(request, employee_id):
    """
    Vue pour modifier les informations d'un employé.
    """
    employee = get_object_or_404(Employee, id=employee_id)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('manage_employees')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'edit_employee.html', {'form': form})

@login_required
def delete_employee(request, employee_id):
    """
    Vue pour supprimer un employé.
    """
    employee = get_object_or_404(Employee, id=employee_id)
    if request.method == 'POST':
        employee.delete()
        return redirect('manage_employees')
    return render(request, 'delete_employee.html', {'employee': employee})

@login_required
def employee_detail(request, employee_id):
    """
    Vue pour afficher la fiche détaillée d'un employé.
    """
    employee = get_object_or_404(Employee, id=employee_id)
    
    # Informations personnelles
    personal_info = {
        'Nom': employee.nom,
        'Prénom': employee.prenom,
        'Code employé': employee.code,
        'Date de naissance': employee.birth_date,
        'Date d\'embauche': employee.hire_date,
        'Adresse': employee.address,
        'Téléphone': employee.phone,
        'Genre': employee.get_gender_display(),
        'Service': employee.service.description,
    }
    
    # Historique professionnel
    contracts = Contract.objects.filter(employee=employee).order_by('-start_date')
    leaves = Leave.objects.filter(employee=employee).order_by('-start_date')
    salaries = Salary.objects.filter(employee=employee).order_by('-year', '-month')
    
    # Compétences
    employee_skills = EmployeeSkill.objects.filter(employee=employee).select_related('skill')
    
    # Formations
    trainings = Training.objects.filter(employee=employee).order_by('-start_date')
    
    # Évaluations
    evaluations = Evaluation.objects.filter(employee=employee).order_by('-date')
    
    # Rapports de performance
    performance_stats = PerformanceStats.objects.filter(employee=employee).order_by('-year')
    
    context = {
        'employee': employee,
        'personal_info': personal_info,
        'contracts': contracts,
        'leaves': leaves,
        'salaries': salaries,
        'employee_skills': employee_skills,
        'trainings': trainings,
        'evaluations': evaluations,
        'performance_stats': performance_stats,
    }
    return render(request, 'employee_detail.html', context)

@login_required
def generate_performance_report_pdf(request, employee_id):
    """
    Vue pour générer un rapport de performance en PDF.
    """
    employee = get_object_or_404(Employee, id=employee_id)
    evaluations = Evaluation.objects.filter(employee=employee).order_by('-date')
    performance_stats = PerformanceStats.objects.filter(employee=employee).order_by('-year')

    context = {
        'employee': employee,
        'evaluations': evaluations,
        'performance_stats': performance_stats,
    }

    html_string = render_to_string('performance_report_pdf.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="performance_report_{employee_id}.pdf"'

    pisa_status = pisa.CreatePDF(html_string, dest=response)
    if pisa_status.err:
        return HttpResponse("Erreur lors de la génération du PDF", status=500)

    return response 


@login_required
def print_employees(request):
    employees = Employee.objects.all()
    html_string = render_to_string('print_employees.html', {'employees': employees})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="liste_employes.pdf"'

    # Generate PDF
    pisa_status = pisa.CreatePDF(html_string, dest=response)
    if pisa_status.err:
        return HttpResponse("Erreur lors de la génération du PDF", status=500)

    return response

from django.core.exceptions import PermissionDenied

@login_required
def manage_trainings(request):
    query = request.GET.get('q')
    status_filter = request.GET.get('status')
    trainings = Training.objects.all()

    if query:
        trainings = trainings.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    if status_filter:
        trainings = trainings.filter(status=status_filter)

    # Add employee to the context (e.g., the first employee or a specific one)
    employee = Employee.objects.first()  # Replace with your logic to get the correct employee
    context = {
        'trainings': trainings,
        'employee': employee,  # Pass the employee to the template
    }
    return render(request, 'trainings.html', context)

@login_required
def manage_trainings_for_employee(request, employee_id):
    # Vérifier si l'utilisateur a la permission can_manage_trainings
    if not request.user.custompermission.can_manage_trainings:
        raise PermissionDenied("Vous n'avez pas la permission de gérer les formations.")

    employee = get_object_or_404(Employee, id=employee_id)
    query = request.GET.get('q')
    status_filter = request.GET.get('status')
    trainings = Training.objects.filter(employee=employee)

    if query:
        trainings = trainings.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    if status_filter:
        trainings = trainings.filter(status=status_filter)

    return render(request, 'trainings_for_employee.html', {
        'trainings': trainings,
        'employee': employee,
    })

@login_required
def add_training_for_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)

    if request.method == 'POST':
        form = TrainingForm(request.POST)
        if form.is_valid():
            training = form.save(commit=False)
            training.employee = employee
            training.save()
            messages.success(request, "Formation ajoutée avec succès!")
            return redirect('manage_trainings')
    else:
        form = TrainingForm()

    return render(request, 'add_training.html', {'form': form, 'employee': employee})

@login_required
def edit_training_for_employee(request, training_id):
    # Vérifier si l'utilisateur a la permission can_manage_trainings
    if not request.user.custompermission.can_manage_trainings:
        raise PermissionDenied("Vous n'avez pas la permission de gérer les formations.")

    training = get_object_or_404(Training, id=training_id)
    if request.method == 'POST':
        form = TrainingForm(request.POST, instance=training)
        if form.is_valid():
            form.save()
            messages.success(request, "Formation modifiée avec succès!")
            return redirect('manage_trainings')
    else:
        form = TrainingForm(instance=training)

    return render(request, 'edit_training.html', {'form': form, 'training': training})

@login_required
def delete_training_for_employee(request, training_id):
    # Vérifier si l'utilisateur a la permission can_manage_trainings
    if not request.user.custompermission.can_manage_trainings:
        raise PermissionDenied("Vous n'avez pas la permission de gérer les formations.")

    training = get_object_or_404(Training, id=training_id)
    if request.method == 'POST':
        training.delete()
        messages.success(request, "Formation supprimée avec succès!")
        return redirect('manage_trainings')

    return render(request, 'confirm_delete_training.html', {'training': training})
# Vues pour les services avec recherche
@login_required
def manage_services(request):
    """
    Vue pour gérer la liste des services avec recherche.
    """
    query = request.GET.get('q')
    services = Service.objects.all()

    if query:
        services = services.filter(
            Q(code__icontains=query) | Q(description__icontains=query)
        )

    return render(request, 'services.html', {'services': services})

@login_required
def print_services(request):
    """
    Vue pour imprimer la liste des services.
    """
    services = Service.objects.all()
    html_string = render_to_string('print_services.html', {'services': services})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="liste_services.pdf"'

    # Convertir le HTML en PDF
    pisa_status = pisa.CreatePDF(html_string, dest=response)
    if pisa_status.err:
        return HttpResponse("Erreur lors de la génération du PDF", status=500)

    return response

@login_required
def add_service(request):
    """
    Vue pour ajouter un nouveau service.
    """
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_services')
    else:
        form = ServiceForm()
    return render(request, 'add_service.html', {'form': form})

@login_required
def edit_service(request, service_id):
    """
    Vue pour modifier les informations d'un service.
    """
    service = get_object_or_404(Service, id=service_id)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect('manage_services')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'edit_service.html', {'form': form})

@login_required
def delete_service(request, service_id):
    """
    Vue pour supprimer un service.
    """
    service = get_object_or_404(Service, id=service_id)
    
    if request.method == 'POST':
        try:
            service.delete()
            messages.success(request, "Le service a été supprimé avec succès.")
            return redirect('manage_services')
        except ProtectedError:
            # Si le service est référencé par JobPosting, afficher un message d'erreur
            messages.error(request, "Impossible de supprimer ce service car il est référencé par une ou plusieurs offres d'emploi.")
            return redirect('manage_services')
    
    return render(request, 'delete_service.html', {'service': service})

# Vues pour les contrats avec recherche
@login_required
def manage_contracts(request):
    """
    Vue pour gérer la liste des contrats avec recherche.
    """
    query = request.GET.get('q')
    contract_type_filter = request.GET.get('contract_type')
    contracts = Contract.objects.all()

    if query:
        contracts = contracts.filter(
            Q(employee__nom__icontains=query) | Q(employee__prenom__icontains=query)
        )

    if contract_type_filter:
        contracts = contracts.filter(type=contract_type_filter)

    contract_types = Contract.CONTRACT_TYPES
    return render(request, 'contracts.html', {'contracts': contracts, 'contract_types': contract_types})

@login_required
def add_contract(request):
    """
    Vue pour ajouter un nouveau contrat.
    """
    if request.method == 'POST':
        form = ContractForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_contracts')
    else:
        form = ContractForm()
    return render(request, 'add_contract.html', {'form': form})

@login_required
def edit_contract(request, contract_id):
    """
    Vue pour modifier les informations d'un contrat.
    """
    contract = get_object_or_404(Contract, id=contract_id)
    if request.method == 'POST':
        form = ContractForm(request.POST, instance=contract)
        if form.is_valid():
            form.save()
            return redirect('manage_contracts')
    else:
        form = ContractForm(instance=contract)
    return render(request, 'edit_contract.html', {'form': form})

@login_required
def delete_contract(request, contract_id):
    """
    Vue pour supprimer un contrat.
    """
    contract = get_object_or_404(Contract, id=contract_id)
    if request.method == 'POST':
        contract.delete()
        return redirect('manage_contracts')
    return render(request, 'delete_contract.html', {'contract': contract})

# Vues pour les congés avec recherche
@login_required
def manage_leaves(request):
    """
    Vue pour gérer la liste des congés avec recherche.
    """
    query = request.GET.get('q')
    leave_type_filter = request.GET.get('leave_type')
    leaves = Leave.objects.all()

    if query:
        leaves = leaves.filter(
            Q(employee__nom__icontains=query) | Q(employee__prenom__icontains=query)
        )

    if leave_type_filter:
        leaves = leaves.filter(type=leave_type_filter)

    leave_types = Leave.LEAVE_TYPES
    return render(request, 'leaves.html', {'leaves': leaves, 'leave_types': leave_types})

@login_required
def request_leave(request):
    """
    Vue pour demander un congé.
    """
    if request.method == 'POST':
        form = LeaveForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_leaves')
    else:
        form = LeaveForm()
    return render(request, 'request_leave.html', {'form': form})

@login_required
def approve_leave(request, leave_id):
    leave = get_object_or_404(Leave, id=leave_id)
    leave.status = 'APPROVED'
    leave.approved = True
    leave.save()

    # Mettre à jour le solde des congés
    employee = leave.employee
    current_year = date.today().year
    leave_balance = LeaveBalance.objects.filter(employee=employee, year=current_year).first()

    if leave_balance:
        if leave.type == 'ANNUAL':
            leave_balance.annual_leave_balance -= (leave.end_date - leave.start_date).days
        elif leave.type == 'SICK':
            leave_balance.sick_leave_balance -= (leave.end_date - leave.start_date).days
        leave_balance.save()

    return redirect('manage_leaves')

# Vue les congés cumulés
@login_required
def carry_over_leave(request):
    if request.method == 'POST':
        current_year = date.today().year
        employees = Employee.objects.all()

        for employee in employees:
            current_balance = LeaveBalance.objects.filter(employee=employee, year=current_year).first()
            if current_balance:
                # Créer un nouveau solde pour l'année suivante avec les congés cumulés
                LeaveBalance.objects.create(
                    employee=employee,
                    year=current_year + 1,
                    annual_leave_balance=30,  # Nouveau solde annuel
                    sick_leave_balance=15,    # Nouveau solde maladie
                    cumulative_leave=max(0, current_balance.annual_leave_balance),  # Cumul des congés non utilisés
                )

        messages.success(request, "Les congés ont été cumulés avec succès.")
        return redirect('manage_dashboard')

    return render(request, 'carry_over_leave.html')

@login_required
def reject_leave(request, leave_id):
    """
    Vue pour rejeter un congé.
    """
    leave = get_object_or_404(Leave, id=leave_id)
    leave.status = 'REJECTED'
    leave.approved = False
    leave.save()
    return redirect('manage_leaves')  # Redirige vers la liste des congés

@login_required
def leave_balance(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    current_year = date.today().year
    leave_balance = LeaveBalance.objects.filter(employee=employee, year=current_year).first()

    if not leave_balance:
        leave_balance = LeaveBalance.objects.create(
            employee=employee,
            year=current_year,
            annual_leave_balance=30,  # Valeur par défaut
            sick_leave_balance=15,    # Valeur par défaut
        )

    context = {
        'employee': employee,
        'leave_balance': leave_balance,
    }
    return render(request, 'leave_balance.html', context)

# Vues pour les salaires avec recherche
@login_required
def manage_salaries(request):
    query = request.GET.get('q')
    month = request.GET.get('month')
    year = request.GET.get('year')
    salaries = Salary.objects.all()

    if query:
        salaries = salaries.filter(employee__nom__icontains=query) | salaries.filter(employee__prenom__icontains=query)
    if month:
        salaries = salaries.filter(month=month)
    if year:
        salaries = salaries.filter(year=year)

    # Pagination
    paginator = Paginator(salaries, 10)  # 10 salaires par page
    page_number = request.GET.get('page')
    salaries = paginator.get_page(page_number)

    return render(request, 'salaries.html', {'salaries': salaries})

@login_required
def generate_salary(request):
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        month = request.POST.get('month')
        year = request.POST.get('year')

        employee = get_object_or_404(Employee, id=employee_id)
        absences = Attendance.objects.filter(
            employee=employee,
            date__month=month,
            date__year=year,
            is_present=False
        ).count()

        # Calcul des retenues
        daily_salary = employee.daily_salary
        absences_deduction = absences * daily_salary

        # Créer un nouveau salaire
        Salary.objects.create(
            employee=employee,
            month=month,
            year=year,
            base_salary=employee.base_salary,
            absences_deduction=absences_deduction,
            net_salary=employee.base_salary - absences_deduction,
        )

        messages.success(request, "Salaire généré avec succès.")
        return redirect('manage_salaries')

    employees = Employee.objects.all()
    return render(request, 'generate_salary.html', {'employees': employees})

@login_required
def request_salary_advance(request):
    if request.method == 'POST':
        form = SalaryAdvanceForm(request.POST)
        if form.is_valid():
            advance = form.save(commit=False)
            advance.employee = request.user.employee
            advance.year = date.today().year
            advance.save()
            messages.success(request, "Demande d'avance envoyée avec succès.")
            return redirect('manage_salaries')
    else:
        form = SalaryAdvanceForm()

    return render(request, 'request_salary_advance.html', {'form': form})

def edit_salary(request, salary_id):
    # Récupérer le salaire à modifier
    salary = get_object_or_404(Salary, id=salary_id)

    if request.method == 'POST':
        # Traitement du formulaire soumis
        form = SalaryForm(request.POST, instance=salary)
        if form.is_valid():
            form.save()  # Enregistrer les modifications
            return redirect('manage_salaries')  # Rediriger vers la liste des salaires
    else:
        # Afficher le formulaire pré-rempli avec les données du salaire
        form = SalaryForm(instance=salary)

    # Afficher le formulaire dans le template
    return render(request, 'edit_salary.html', {'form': form})
def delete_salary(request, salary_id):
    # Récupérer le salaire à supprimer
    salary = get_object_or_404(Salary, id=salary_id)

    if request.method == 'POST':
        # Supprimer le salaire
        salary.delete()
        return redirect('manage_salaries')  # Rediriger vers la liste des salaires

    # Afficher une page de confirmation de suppression
    return render(request, 'confirm_delete.html', {'salary': salary})

# Vues pour les évaluations avec recherche
@login_required
def manage_evaluations(request):
    """
    Vue pour gérer la liste des évaluations avec recherche.
    """
    query = request.GET.get('q')
    evaluator_filter = request.GET.get('evaluator')
    evaluations = Evaluation.objects.all()

    if query:
        evaluations = evaluations.filter(
            Q(employee__nom__icontains=query) | Q(employee__prenom__icontains=query)
        )

    if evaluator_filter:
        evaluations = evaluations.filter(evaluator__username__icontains=evaluator_filter)

    return render(request, 'evaluations.html', {'evaluations': evaluations})

@login_required
def add_evaluation(request, employee_id):
    """
    Vue pour ajouter une évaluation.
    """
    employee = get_object_or_404(Employee, id=employee_id)
    if request.method == 'POST':
        form = EvaluationForm(request.POST)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.employee = employee
            evaluation.evaluator = request.user
            evaluation.save()
            messages.success(request, 'Évaluation ajoutée avec succès!')
            return redirect('employee_detail', employee_id=employee.id)
    else:
        form = EvaluationForm()
    return render(request, 'add_evaluation.html', {'form': form, 'employee': employee})

@login_required
def add_evaluation_without_employee(request):
    """
    Vue pour ajouter une évaluation sans spécifier d'employé.
    """
    if request.method == 'POST':
        form = EvaluationForm(request.POST)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.evaluator = request.user
            evaluation.save()
            messages.success(request, 'Évaluation ajoutée avec succès!')
            return redirect('manage_evaluations')
    else:
        form = EvaluationForm()
    return render(request, 'add_evaluation.html', {'form': form})

@login_required
def edit_evaluation(request, evaluation_id):
    """
    Vue pour modifier une évaluation.
    """
    evaluation = get_object_or_404(Evaluation, id=evaluation_id)
    if request.method == 'POST':
        form = EvaluationForm(request.POST, instance=evaluation)
        if form.is_valid():
            form.save()
            messages.success(request, 'Évaluation modifiée avec succès!')
            return redirect('manage_evaluations')
    else:
        form = EvaluationForm(instance=evaluation)
    return render(request, 'edit_evaluation.html', {'form': form})

@login_required
def generate_evaluation_report(request, employee_id):
    """
    Vue pour générer un rapport d'évaluation pour un employé.
    """
    employee = get_object_or_404(Employee, id=employee_id)
    evaluations = Evaluation.objects.filter(employee=employee)
    average_score = evaluations.aggregate(Avg('performance_score'))['performance_score__avg'] or 0

    context = {
        'employee': employee,
        'evaluations': evaluations,
        'average_score': average_score,
    }
    return render(request, 'evaluation_report.html', context)

@login_required
def generate_evaluation_report_pdf(request, employee_id):
    """
    Vue pour générer un rapport d'évaluation en PDF.
    """
    employee = get_object_or_404(Employee, id=employee_id)
    evaluations = Evaluation.objects.filter(employee=employee)
    average_score = evaluations.aggregate(Avg('performance_score'))['performance_score__avg'] or 0

    context = {
        'employee': employee,
        'evaluations': evaluations,
        'average_score': average_score,
    }

    html_string = render_to_string('evaluation_report_pdf.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="evaluation_report_{employee_id}.pdf"'

    pisa_status = pisa.CreatePDF(html_string, dest=response)
    if pisa_status.err:
        return HttpResponse("Erreur lors de la génération du PDF", status=500)

    return response

# Vues pour le recrutement avec recherche
@login_required
def manage_recruitment(request):
    """
    Vue pour gérer la liste des offres d'emploi avec recherche.
    """
    query = request.GET.get('q')
    status_filter = request.GET.get('status')
    job_postings = JobPosting.objects.all()

    if query:
        job_postings = job_postings.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    if status_filter:
        job_postings = job_postings.filter(status=status_filter)

    return render(request, 'recruitment.html', {'job_postings': job_postings})

@login_required
def post_job(request):
    """
    Vue pour poster une nouvelle offre d'emploi.
    """
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_recruitment')
    else:
        form = JobPostingForm()
    return render(request, 'post_job.html', {'form': form})

@login_required
def view_applications(request, job_posting_id):
    """
    Vue pour afficher les candidatures pour une offre d'emploi spécifique.
    """
    job_posting = get_object_or_404(JobPosting, id=job_posting_id)
    applications = JobApplication.objects.filter(job_posting=job_posting)
    return render(request, 'view_applications.html', {'job_posting': job_posting, 'applications': applications})

@login_required
def update_application_status(request, application_id):
    """
    Vue pour mettre à jour le statut d'une candidature.
    """
    application = get_object_or_404(JobApplication, id=application_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        application.status = new_status
        application.save()
        return redirect('view_applications', job_posting_id=application.job_posting.id)
    return render(request, 'update_application_status.html', {'application': application})

@login_required
def apply_job(request, job_posting_id):
    """
    Vue pour permettre aux utilisateurs de postuler à une offre d'emploi.
    """
    job_posting = get_object_or_404(JobPosting, id=job_posting_id)
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job_posting = job_posting
            application.candidate = request.user  # L'utilisateur connecté est le candidat
            application.save()
            messages.success(request, "Votre candidature a été soumise avec succès.")
            return redirect('job_posting_detail', job_posting_id=job_posting.id)
    else:
        form = JobApplicationForm()
    return render(request, 'apply_job.html', {'form': form, 'job_posting': job_posting})

def job_posting_detail(request, job_posting_id):
    job_posting = get_object_or_404(JobPosting, id=job_posting_id)
    return render(request, 'job_posting_detail.html', {'job_posting': job_posting})

# Vues pour les favoris avec recherche
@login_required
def manage_favorites(request):
    """
    Affiche la liste des favoris de l'utilisateur connecté avec recherche.
    """
    query = request.GET.get('q')
    favorites = Favorite.objects.filter(user=request.user)

    if query:
        favorites = favorites.filter(
            Q(name__icontains=query) | Q(url__icontains=query)
        )

    return render(request, 'favorites.html', {'favorites': favorites})

@login_required
def add_favorite(request):
    """
    Permet à l'utilisateur d'ajouter un nouveau favori.
    """
    if request.method == 'POST':
        form = FavoriteForm(request.POST)
        if form.is_valid():
            favorite = form.save(commit=False)
            favorite.user = request.user
            favorite.save()
            return redirect('manage_favorites')
    else:
        form = FavoriteForm()
    return render(request, 'add_favorite.html', {'form': form})

@login_required
def edit_favorite(request, favorite_id):
    """
    Permet à l'utilisateur de modifier un favori existant.
    """
    favorite = get_object_or_404(Favorite, id=favorite_id, user=request.user)
    if request.method == 'POST':
        form = FavoriteForm(request.POST, instance=favorite)
        if form.is_valid():
            form.save()
            return redirect('manage_favorites')
    else:
        form = FavoriteForm(instance=favorite)
    return render(request, 'edit_favorite.html', {'form': form, 'favorite': favorite})

@login_required
def remove_favorite(request, favorite_id):
    """
    Permet à l'utilisateur de supprimer un favori.
    """
    favorite = get_object_or_404(Favorite, id=favorite_id, user=request.user)
    if request.method == 'POST':
        favorite.delete()
        return redirect('manage_favorites')
    return render(request, 'delete_favorite.html', {'favorite': favorite})

@login_required
def customize_favorites(request):
    """
    Vue pour personnaliser les favoris de l'utilisateur.
    """
    if request.method == 'POST':
        # Récupérer les favoris sélectionnés et leur ordre
        favorites_data = request.POST.getlist('favorites')
        order_data = request.POST.getlist('order')

        # Supprimer les anciens favoris de l'utilisateur
        Favorite.objects.filter(user=request.user).delete()

        # Ajouter les nouveaux favoris avec leur ordre
        for favorite_name, order in zip(favorites_data, order_data):
            Favorite.objects.create(
                user=request.user,
                name=favorite_name,
                url=f"/{favorite_name.lower().replace(' ', '-')}/",  # Générer une URL basée sur le nom
                order=int(order),
            )

        messages.success(request, "Vos favoris ont été mis à jour avec succès.")
        return redirect('manage_favorites')

    # Liste des modules disponibles pour les favoris
    available_modules = [
        {'name': 'Contrats', 'url': 'manage_contracts'},
        {'name': 'Congés', 'url': 'manage_leaves'},
        {'name': 'Salaires', 'url': 'manage_salaries'},
        {'name': 'Évaluations', 'url': 'manage_evaluations'},
        {'name': 'Recrutement', 'url': 'manage_recruitment'},
        {'name': 'Formations', 'url': 'manage_trainings'},
        {'name': 'Compétences', 'url': 'manage_skills'},
    ]

    # Récupérer les favoris actuels de l'utilisateur
    user_favorites = Favorite.objects.filter(user=request.user)

    context = {
        'available_modules': available_modules,
        'user_favorites': user_favorites,
    }
    return render(request, 'customize_favorites.html', context)

# Vues pour les formations avec recherche
@login_required
def manage_trainings(request):
    """
    Vue pour gérer la liste des formations avec recherche.
    """
    query = request.GET.get('q')
    status_filter = request.GET.get('status')
    trainings = Training.objects.all()

    if query:
        trainings = trainings.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    if status_filter:
        trainings = trainings.filter(status=status_filter)

    return render(request, 'trainings.html', {'trainings': trainings})

# Vues pour les compétences avec recherche
@login_required
def manage_skills(request):
    """
    Vue pour gérer la liste des compétences avec recherche.
    """
    query = request.GET.get('q')
    skills = Skill.objects.all()

    if query:
        skills = skills.filter(
            Q(name__icontains=query) | Q(category__icontains=query)
        )

    return render(request, 'skills.html', {'skills': skills})

# Vues pour les compétences des employés avec recherche
@login_required
def manage_employee_skills(request):
    """
    Vue pour gérer les compétences des employés avec recherche.
    """
    query = request.GET.get('q')
    employee_skills = EmployeeSkill.objects.all()

    if query:
        employee_skills = employee_skills.filter(
            Q(employee__nom__icontains=query) | Q(employee__prenom__icontains=query) | Q(skill__name__icontains=query)
        )

    return render(request, 'employee_skills.html', {'employee_skills': employee_skills})

# Vues pour les permissions
@login_required
def grant_permissions(request):
    """
    Vue pour accorder des permissions personnalisées.
    """
    if not request.user.is_manager:
        return redirect('home')

    if request.method == 'POST':
        form = CustomPermissionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_permissions')
    else:
        form = CustomPermissionForm()

    return render(request, 'grant_permissions.html', {'form': form})

# Vue pour les fiches de paie
@login_required
def generate_payslip(request, employee_id, month, year):
    employee = get_object_or_404(Employee, id=employee_id)
    salary = Salary.objects.filter(employee=employee, month=month, year=year).first()
    if not salary:
        return HttpResponse("Aucun salaire trouvé pour cette période.")

    # Créer la fiche de paie
    payslip = Payslip.objects.create(
        employee=employee,
        month=month,
        year=year,
        base_salary=salary.base_salary,
        bonuses=salary.bonuses,
        deductions=salary.absences_deduction,
        net_salary=salary.net_salary
    )

    # Générer le PDF avec xhtml2pdf
    html_string = render_to_string('payslip_template.html', {'payslip': payslip})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="payslip_{employee_id}_{month}_{year}.pdf"'

    # Convertir le HTML en PDF
    pisa_status = pisa.CreatePDF(html_string, dest=response)
    if pisa_status.err:
        return HttpResponse("Erreur lors de la génération du PDF", status=500)

    return response

# Vue pour les bonus
@login_required
def add_bonus(request, employee_id):
    """
    Vue pour ajouter un bonus à un employé.
    """
    employee = get_object_or_404(Employee, id=employee_id)
    if request.method == 'POST':
        form = BonusForm(request.POST)
        if form.is_valid():
            bonus = form.save(commit=False)
            bonus.employee = employee
            bonus.save()
            return redirect('manage_salaries')
    else:
        form = BonusForm()
    return render(request, 'add_bonus.html', {'form': form})

# Vue pour archiver les contrats
@login_required
def archive_contract(request, contract_id):
    """
    Vue pour archiver un contrat.
    """
    contract = get_object_or_404(Contract, id=contract_id)
    contract.archived = True
    contract.save()
    return redirect('manage_contracts')

# Vue pour planifier un entretien
@login_required
def schedule_interview(request, job_application_id):
    """
    Vue pour planifier un entretien pour une candidature.
    """
    job_application = get_object_or_404(JobApplication, id=job_application_id)
    if request.method == 'POST':
        form = InterviewForm(request.POST)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.job_application = job_application
            interview.interviewer = request.user  # Ajoutez l'utilisateur connecté comme intervieweur
            interview.save()
            return redirect('manage_recruitment')
    else:
        form = InterviewForm()
    return render(request, 'schedule_interview.html', {'form': form, 'job_application': job_application})


@login_required
def record_attendance(request):
    """
    Vue pour enregistrer les présences/absences des employés.
    """
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        date = request.POST.get('date')
        is_present = request.POST.get('is_present') == 'on'
        reason = request.POST.get('reason', '')

        try:
            employee = Employee.objects.get(id=employee_id)
            Attendance.objects.create(
                employee=employee,
                date=date,
                is_present=is_present,
                reason=reason,
            )
            messages.success(request, "Pointage enregistré avec succès.")
        except Employee.DoesNotExist:
            messages.error(request, "L'employé spécifié n'existe pas.")
        return redirect('record_attendance')

    employees = Employee.objects.all()
    return render(request, 'record_attendance.html', {'employees': employees})

# Vues API
class DashboardViewSet(viewsets.ViewSet):
    """
    ViewSet pour le tableau de bord.
    """
    def list(self, request):
        total_employees = Employee.objects.count()
        active_contracts = Contract.objects.filter(is_active=True).count()
        pending_leaves = Leave.objects.filter(status='PENDING').count()
        total_salaries = Salary.objects.aggregate(total_salaries=Sum('net_salary'))['total_salaries'] or 0
        recent_evaluations = Evaluation.objects.filter(date__gte=date.today() - timedelta(days=30)).count()
        open_job_postings = JobPosting.objects.filter(active=True).count()

        # Statistiques sur les services
        total_services = Service.objects.count()
        employees_by_service = Employee.objects.values('service__description').annotate(count=Count('id'))

        data = {
            'total_employees': total_employees,
            'active_contracts': active_contracts,
            'pending_leaves': pending_leaves,
            'total_salaries': total_salaries,
            'recent_evaluations': recent_evaluations,
            'open_job_postings': open_job_postings,
            'total_services': total_services,
            'employees_by_service': employees_by_service,
        }
        return Response(data)
        

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer

class LeaveViewSet(viewsets.ModelViewSet):
    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer

class SalaryViewSet(viewsets.ModelViewSet):
    queryset = Salary.objects.all()
    serializer_class = SalarySerializer

class EvaluationViewSet(viewsets.ModelViewSet):
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer

class JobPostingViewSet(viewsets.ModelViewSet):
    queryset = JobPosting.objects.all()
    serializer_class = JobPostingSerializer

class JobApplicationViewSet(viewsets.ModelViewSet):
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer

class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer

from rest_framework.permissions import IsAuthenticated
from .permissions import CanManageTrainings

class TrainingViewSet(viewsets.ModelViewSet):
    queryset = Training.objects.all()
    serializer_class = TrainingSerializer
    permission_classes = [IsAuthenticated, CanManageTrainings]  

class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer

class EmployeeSkillViewSet(viewsets.ModelViewSet):
    queryset = EmployeeSkill.objects.all()
    serializer_class = EmployeeSkillSerializer