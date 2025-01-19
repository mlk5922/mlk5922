# core/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from .models import (
    User, CustomPermission, Employee, Service, Contract, Leave, LeaveBalance,
    Attendance, Salary, SalaryAdvance, Evaluation, Training, Skill, EmployeeSkill,
    JobPosting, JobApplication, Favorite, Document, Notification, Payslip, Bonus, Interview, DiversityStats
)

# Formulaire pour l'utilisateur
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'is_hr', 'is_manager', 'is_employee']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data['password'])  # Hasher le mot de passe
        if commit:
            user.save()
        return user
# Formulaire pour candidate
class CandidateSignUpForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput,
        help_text="Votre mot de passe doit contenir au moins 8 caractères.",
    )
    password2 = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput,
        help_text="Entrez le même mot de passe pour confirmation.",
    )
    user_type = forms.ChoiceField(
        choices=[('CANDIDATE', 'Candidat'), ('EMPLOYEE', 'Employé')],
        label="Type d'utilisateur",
        widget=forms.RadioSelect
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Les mots de passe ne correspondent pas.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user_type = self.cleaned_data.get("user_type")
        if user_type == 'CANDIDATE':
            user.is_candidate = True
        elif user_type == 'EMPLOYEE':
            user.is_employee = True
        user.is_active = False
        if commit:
            user.save()
        return user
    
# Formulaire pour les permissions personnalisées
class CustomPermissionForm(forms.ModelForm):
    class Meta:
        model = CustomPermission
        fields = '__all__'

# Formulaire pour l'employé
class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'hire_date': forms.DateInput(attrs={'type': 'date'}),
            'trainings': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }
# Formulaire pour le service
class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = '__all__'

# Formulaire pour le contrat
class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = '__all__'
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

# Formulaire pour le congé
class LeaveForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = '__all__'
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and end_date < start_date:
            raise ValidationError("La date de fin doit être postérieure à la date de début.")
        return cleaned_data

# Formulaire pour le solde de congé
class LeaveBalanceForm(forms.ModelForm):
    class Meta:
        model = LeaveBalance
        fields = '__all__'

# Formulaire pour la présence
class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

# Formulaire pour le salaire
class SalaryForm(forms.ModelForm):
    class Meta:
        model = Salary
        fields = ['employee', 'month', 'year', 'base_salary', 'bonuses', 'deductions', 'net_salary']


# Formulaire pour l'avance sur salaire
class SalaryAdvanceForm(forms.ModelForm):
    class Meta:
        model = SalaryAdvance
        fields = ['amount', 'reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

# Formulaire pour l'évaluation
class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = [
            'employee', 'date', 'performance_score', 'comments',
            'criteria_1', 'score_1', 'criteria_2', 'score_2', 'criteria_3', 'score_3'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'comments': forms.Textarea(attrs={'rows': 3}),
        }

# Formulaire pour la formation
class TrainingForm(forms.ModelForm):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        label="Employé",
        required=True,
    )

    class Meta:
        model = Training
        fields = ['title', 'description', 'start_date', 'end_date', 'status', 'employee']

# Formulaire pour la compétence
class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

# Formulaire pour la compétence de l'employé
class EmployeeSkillForm(forms.ModelForm):
    class Meta:
        model = EmployeeSkill
        fields = ['skill', 'level']

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'category', 'description', 'level', 'acquisition_date']

# Formulaire pour l'offre d'emploi
class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = ['title', 'description', 'contract_type', 'service', 'active', 'is_filled']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

# Formulaire pour la candidature
class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['full_name', 'address', 'phone', 'skills', 'cover_letter', 'cv_file']
        widgets = {
            'cover_letter': forms.Textarea(attrs={'rows': 3}),
            'cv_file': forms.FileInput(attrs={'accept': '.pdf,.doc,.docx'}),
        }
# Formulaire pour les favoris
class FavoriteForm(forms.ModelForm):
    class Meta:
        model = Favorite
        fields = ['name', 'url']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du favori'}),
            'url': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'URL du favori'}),
        }

# Formulaire pour le document
class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = '__all__'

# Formulaire pour la notification
class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = '__all__'
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3}),
        }

# Formulaire pour la fiche de paie
class PayslipForm(forms.ModelForm):
    class Meta:
        model = Payslip
        fields = ['employee', 'month', 'year', 'base_salary', 'bonuses', 'deductions', 'net_salary']
        widgets = {
            'month': forms.NumberInput(attrs={'min': 1, 'max': 12}),
            'year': forms.NumberInput(attrs={'min': 2000, 'max': 2100}),
        }

# Formulaire pour les primes
class BonusForm(forms.ModelForm):
    class Meta:
        model = Bonus
        fields = ['type', 'amount', 'reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

# Formulaire pour les entretiens
class InterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ['job_application', 'date', 'notes']  # Excluez 'interviewer'
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

# Formulaire pour les statistiques de diversité
class DiversityStatsForm(forms.ModelForm):
    class Meta:
        model = DiversityStats
        fields = ['year', 'male_count', 'female_count', 'other_count']

class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = ['employee', 'date', 'performance_score', 'comments']        