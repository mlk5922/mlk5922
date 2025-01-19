# core/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
import os
from django.utils.translation import gettext_lazy as _

# Modèle utilisateur personnalisé


class User(AbstractUser):
    """
    Modèle utilisateur personnalisé basé sur AbstractUser.
    Ajoute des champs pour gérer les rôles (RH, manager, employé, candidat),
    l'activation du compte, et un code de validation pour la confirmation par e-mail.
    """

    # Champs supplémentaires
    email = models.EmailField(
        unique=True,
        verbose_name="Adresse e-mail",
        help_text="L'adresse e-mail doit être unique."
    )
    is_hr = models.BooleanField(
        default=False,
        verbose_name="Est un RH",
        help_text="Indique si l'utilisateur est un responsable des ressources humaines."
    )
    is_manager = models.BooleanField(
        default=False,
        verbose_name="Est un manager",
        help_text="Indique si l'utilisateur est un manager."
    )
    is_employee = models.BooleanField(
        default=True,
        verbose_name="Est un employé",
        help_text="Indique si l'utilisateur est un employé."
    )
    is_candidate = models.BooleanField(
        default=False,
        verbose_name="Est un candidat",
        help_text="Indique si l'utilisateur est un candidat."
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name="Compte activé",
        help_text="Désactivé par défaut jusqu'à la confirmation par e-mail."
    )
    verification_code = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        verbose_name="Code de validation",
        help_text="Code à 6 chiffres pour la validation du compte par e-mail."
    )

    # Méthodes et métadonnées
    def __str__(self):
        """
        Représentation en chaîne de caractères de l'utilisateur.
        """
        return self.username

    def clean(self):
        """
        Validation personnalisée pour s'assurer qu'un utilisateur ne peut pas être à la fois employé et candidat.
        """
        if self.is_employee and self.is_candidate:
            raise ValidationError(_("Un utilisateur ne peut pas être à la fois employé et candidat."))
        super().clean()

    def save(self, *args, **kwargs):
        """
        Surcharge de la méthode save pour appliquer des règles métier avant la sauvegarde.
        """
        self.clean()  # Appliquer la validation avant la sauvegarde
        super().save(*args, **kwargs)

    class Meta:
        """
        Métadonnées pour le modèle User.
        """
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ['username']  # Trier par nom d'utilisateur par défaut
# Modèle de document
class Document(models.Model):
    title = models.CharField(max_length=255)  # Titre du document
    file = models.FileField(
        upload_to='documents/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])]
    )  # Fichier uploadé avec validation des extensions
    created_at = models.DateTimeField(auto_now_add=True)  # Date de création
    updated_at = models.DateTimeField(auto_now=True)  # Date de mise à jour
    is_verified = models.BooleanField(default=False)  # Indique si le document est vérifié

    def filename(self):
        return os.path.basename(self.file.name)  # Retourne le nom du fichier

    def __str__(self):
        return self.title

# Modèle de permission personnalisée
class CustomPermission(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    can_manage_employees = models.BooleanField(default=False, verbose_name="Peut gérer les employés")
    can_manage_contracts = models.BooleanField(default=False, verbose_name="Peut gérer les contrats")
    can_manage_leaves = models.BooleanField(default=False, verbose_name="Peut gérer les congés")
    can_manage_salaries = models.BooleanField(default=False, verbose_name="Peut gérer les salaires")
    can_manage_recruitment = models.BooleanField(default=False, verbose_name="Peut gérer le recrutement")
    can_manage_trainings = models.BooleanField(default=False, verbose_name="Peut gérer la formation")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    def __str__(self):
        return f"Permissions pour {self.user.username}"

# Modèle de service
class Service(models.Model):
    code = models.CharField(max_length=10, unique=True)  # Code du service
    description = models.TextField()  # Description du service
    created_at = models.DateTimeField(auto_now_add=True)  # Date de création
    updated_at = models.DateTimeField(auto_now=True)  # Date de mise à jour
    is_active = models.BooleanField(default=True)  # Indique si le service est actif

    def __str__(self):
        return self.code

# Modèle d'employé
class Employee(models.Model):
    GENDER_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
        ('O', 'Autre')
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    nom = models.CharField(max_length=255, verbose_name="Nom")
    prenom = models.CharField(max_length=255, verbose_name="Prénom")
    code = models.CharField(max_length=10, unique=True, verbose_name="Code employé")
    birth_date = models.DateField(verbose_name="Date de naissance")
    hire_date = models.DateField(verbose_name="Date d'embauche")
    address = models.TextField(verbose_name="Adresse")
    phone = models.CharField(max_length=20, null=True, blank=True)
    documents = models.ManyToManyField(Document, blank=True, verbose_name="Documents")
    service = models.ForeignKey(Service, on_delete=models.PROTECT, verbose_name="Service")
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Salaire de base")
    daily_salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Salaire journalier", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.prenom} {self.nom} - {self.code}"

# Modèle de contrat
class Contract(models.Model):
    CONTRACT_TYPES = [
        ('CDI', 'Contrat à Durée Indéterminée'),
        ('CDD', 'Contrat à Durée Déterminée'),
        ('STAGE', 'Stage'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT)
    type = models.CharField(max_length=50, choices=CONTRACT_TYPES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    monthly_salary = models.DecimalField(max_digits=10, decimal_places=2)
    daily_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # Valeur par défaut
    is_active = models.BooleanField(default=True)
    archived = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.employee} - {self.type}"

# Modèle de congé
class Leave(models.Model):
    LEAVE_TYPES = [
        ('ANNUAL', 'Congé Annuel'),
        ('SICK', 'Congé Maladie'),
        ('MATERNITY', 'Congé Maternité'),
        ('PATERNITY', 'Congé Paternité'),
        ('UNPAID', 'Congé Sans Solde'),
    ]
    LEAVE_STATUS = [
        ('PENDING', 'En attente'),
        ('APPROVED', 'Approuvé'),
        ('REJECTED', 'Rejeté'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT)  # Employé associé
    type = models.CharField(max_length=10, choices=LEAVE_TYPES)  # Type de congé
    start_date = models.DateField()  # Date de début du congé
    end_date = models.DateField()  # Date de fin du congé
    status = models.CharField(max_length=10, choices=LEAVE_STATUS, default='PENDING')  # Statut du congé
    approved = models.BooleanField(default=False)  # Indique si le congé est approuvé
    created_at = models.DateTimeField(auto_now_add=True)  # Date de création
    updated_at = models.DateTimeField(auto_now=True)  # Date de mise à jour

    def __str__(self):
        return f"{self.employee} - {self.type}"

# Modèle de solde de congé
class LeaveBalance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT)  # Employé associé
    year = models.IntegerField()  # Année du solde
    annual_leave_balance = models.IntegerField(default=30)  # Solde de congé annuel
    sick_leave_balance = models.IntegerField(default=15)  # Solde de congé maladie
    cumulative_leave = models.IntegerField(default=0)  # Congés cumulés de l'année précédente
    created_at = models.DateTimeField(auto_now_add=True)  # Date de création
    updated_at = models.DateTimeField(auto_now=True)  # Date de mise à jour

    def __str__(self):
        return f"{self.employee} - {self.year}"

    def save(self, *args, **kwargs):
        # Si c'est une nouvelle année, cumuler les congés non utilisés de l'année précédente
        if not self.pk:  # Vérifie si c'est une nouvelle instance
            previous_year_balance = LeaveBalance.objects.filter(
                employee=self.employee,
                year=self.year - 1
            ).first()
            if previous_year_balance:
                self.cumulative_leave = max(0, previous_year_balance.annual_leave_balance)
        super().save(*args, **kwargs)

# Modèle de présence
class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT)  # Employé associé
    date = models.DateField()  # Date de la présence
    is_present = models.BooleanField(default=True)  # Indique si l'employé est présent
    reason = models.TextField(blank=True, null=True)  # Raison de l'absence (optionnel)
    created_at = models.DateTimeField(auto_now_add=True)  # Date de création
    updated_at = models.DateTimeField(auto_now=True)  # Date de mise à jour

    class Meta:
        unique_together = ['employee', 'date']  # Contrainte d'unicité

    def __str__(self):
        return f"{self.employee} - {self.date} - {'Présent' if self.is_present else 'Absent'}"

# Modèle de salaire
class Salary(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT)  # Employé associé
    month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])  # Mois du salaire
    year = models.IntegerField()  # Année du salaire
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)  # Salaire de base
    absences_deduction = models.DecimalField(max_digits=10, decimal_places=2)  # Déduction pour absences
    bonuses = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Bonus
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Ajoutez ce champ si nécessaire
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)  # Salaire net
    is_paid = models.BooleanField(default=False)  # Indique si le salaire est payé
    created_at = models.DateTimeField(auto_now_add=True)  # Date de création
    updated_at = models.DateTimeField(auto_now=True)  # Date de mise à jour

    class Meta:
        unique_together = ['employee', 'month', 'year']  # Contrainte d'unicité

    def __str__(self):
        return f"{self.employee} - {self.month}/{self.year}"

# Modèle d'avance sur salaire
class SalaryAdvance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT)  # Employé associé
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Montant de l'avance
    reason = models.TextField()  # Raison de l'avance
    year = models.IntegerField()  # Année de l'avance
    approved = models.BooleanField(default=False)  # Indique si l'avance est approuvée
    created_at = models.DateTimeField(auto_now_add=True)  # Date de création
    updated_at = models.DateTimeField(auto_now=True)  # Date de mise à jour
    request_date = models.DateField(auto_now_add=True)  # Date de la demande

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['employee', 'year'],
                condition=models.Q(approved=True),
                name='max_two_advances_per_year'
            )
        ]

    def __str__(self):
        return f"{self.employee} - {self.amount}"

# Modèle d'évaluation
class Evaluation(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT)  # Employé associé
    evaluator = models.ForeignKey(User, on_delete=models.PROTECT)  # Évaluateur
    date = models.DateField()  # Date de l'évaluation
    performance_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])  # Score de performance
    comments = models.TextField()  # Commentaires
    is_completed = models.BooleanField(default=False)  # Indique si l'évaluation est terminée
    created_at = models.DateTimeField(auto_now_add=True)  # Date de création
    updated_at = models.DateTimeField(auto_now=True)  # Date de mise à jour

    # Additional fields
    score_1 = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], null=True, blank=True)
    score_2 = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], null=True, blank=True)
    score_3 = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], null=True, blank=True)
    criteria_1 = models.CharField(max_length=255, null=True, blank=True)
    criteria_2 = models.CharField(max_length=255, null=True, blank=True)
    criteria_3 = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.employee} - {self.performance_score}"

# Modèle de formation
class Training(models.Model):
    # Choix pour le statut de la formation
    TRAINING_STATUS = [
        ('PLANNED', 'Planifiée'),
        ('IN_PROGRESS', 'En cours'),
        ('COMPLETED', 'Terminée'),
        ('CANCELLED', 'Annulée'),
    ]

    # Relations
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Employé")

    # Champs de base
    title = models.CharField(max_length=255, verbose_name="Titre de la formation")
    description = models.TextField(verbose_name="Description")
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(verbose_name="Date de fin")
    status = models.CharField(max_length=20, choices=TRAINING_STATUS, verbose_name="Statut")
    score = models.IntegerField(null=True, blank=True, verbose_name="Score")
    certificate = models.FileField(upload_to='certificates/', null=True, blank=True, verbose_name="Certificat")
    is_completed = models.BooleanField(default=False, verbose_name="Terminée")

    # Champs de date
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    def __str__(self):
        """
        Représentation en chaîne de caractères de l'objet Training.
        """
        return f"{self.title} - {self.employee}"

    class Meta:
        """
        Métadonnées pour le modèle Training.
        """
        verbose_name = "Formation"
        verbose_name_plural = "Formations"

# Modèle de compétence
class Skill(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    description = models.TextField()
    level = models.CharField(max_length=50, choices=[('Débutant', 'Débutant'), ('Intermédiaire', 'Intermédiaire'), ('Avancé', 'Avancé')], default='Débutant')
    acquisition_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# Modèle de compétence d'employé
class EmployeeSkill(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='skill_employees')
    level = models.CharField(
        max_length=50,
        choices=[('Débutant', 'Débutant'), ('Intermédiaire', 'Intermédiaire'), ('Avancé', 'Avancé')],
        default='Débutant'
    )
    acquisition_date = models.DateField(default=timezone.now)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['employee', 'skill']

    def __str__(self):
        return f"{self.employee} - {self.skill} (Niveau: {self.level})"

# Modèle d'offre d'emploi
class JobPosting(models.Model):
    title = models.CharField(max_length=100)  # Titre de l'offre
    description = models.TextField()  # Description de l'offre
    contract_type = models.CharField(max_length=5, choices=Contract.CONTRACT_TYPES)  # Type de contrat
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True)    
    active = models.BooleanField(default=True)  # Indique si l'offre est active
    is_filled = models.BooleanField(default=False)  # Indique si le poste est pourvu
    created_at = models.DateTimeField(auto_now_add=True)  # Date de création
    updated_at = models.DateTimeField(auto_now=True)  # Date de mise à jour

    def __str__(self):
        return self.title

# Modèle de candidature
class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('RECEIVED', 'Reçue'),
        ('PROCESSING', 'En cours de traitement'),
        ('INTERVIEW', 'Entretien planifié'),
        ('REJECTED', 'Rejetée'),
        ('ACCEPTED', 'Acceptée'),
    ]
    job_posting = models.ForeignKey(JobPosting, on_delete=models.PROTECT)
    candidate = models.ForeignKey(User, on_delete=models.PROTECT)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='RECEIVED')
    cv_file = models.FileField(upload_to='cvs/')
    cover_letter = models.TextField()
    interview_date = models.DateTimeField(null=True, blank=True)
    is_selected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    full_name = models.CharField(max_length=255, default='Non spécifié')  # Valeur par défaut
    address = models.TextField(default='Non spécifiée')  # Valeur par défaut
    phone = models.CharField(max_length=20, default='Non spécifié')  # Valeur par défaut
    skills = models.TextField(default='Non spécifié')  # Valeur par défaut

    def __str__(self):
        return f"{self.candidate} - {self.job_posting}"
    
# Modèle de favori
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    name = models.CharField(max_length=100, verbose_name="Nom du favori")
    url = models.CharField(max_length=200, verbose_name="URL du favori")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    order = models.IntegerField(default=0, verbose_name="Ordre d'affichage")  # Nouveau champ pour l'ordre
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")

    class Meta:
        ordering = ['order']  # Trier par ordre d'affichage

    def __str__(self):
        return f"{self.user.username} - {self.name}"

# Modèle de journal d'audit
class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Création'),
        ('UPDATE', 'Modification'),
        ('DELETE', 'Suppression'),
    ]
    user = models.ForeignKey(User, on_delete=models.PROTECT)  # Utilisateur associé
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)  # Action effectuée
    model_name = models.CharField(max_length=100)  # Nom du modèle
    object_id = models.IntegerField()  # ID de l'objet
    changes = models.JSONField()  # Changements effectués
    timestamp = models.DateTimeField(auto_now_add=True)  # Date et heure de l'action
    ip_address = models.GenericIPAddressField()  # Adresse IP de l'utilisateur
    is_resolved = models.BooleanField(default=False)  # Indique si l'action est résolue

    def __str__(self):
        return f"{self.user} - {self.action}"

# Modèle de notification
class Notification(models.Model):
    PRIORITY_CHOICES = [
        ('LOW', 'Faible'),
        ('NORMAL', 'Normal'),
        ('HIGH', 'Élevée'),
        ('URGENT', 'Urgent'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Utilisateur associé
    title = models.CharField(max_length=255)  # Titre de la notification
    message = models.TextField()  # Message de la notification
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='NORMAL')  # Priorité de la notification
    is_read = models.BooleanField(default=False)  # Indique si la notification est lue
    is_archived = models.BooleanField(default=False)  # Indique si la notification est archivée
    created_at = models.DateTimeField(auto_now_add=True)  # Date de création

    class Meta:
        ordering = ['-created_at']  # Tri par date de création décroissante

    def __str__(self):
        return f"{self.user} - {self.title}"

# Modèle de fiche de paie
class Payslip(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Employé")
    month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)], verbose_name="Mois")
    year = models.IntegerField(verbose_name="Année")
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Salaire de base")
    bonuses = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Bonus")
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Déductions")
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Salaire net")
    is_paid = models.BooleanField(default=False, verbose_name="Payé")
    pdf_file = models.FileField(upload_to='payslips/', null=True, blank=True, verbose_name="Fichier PDF")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    def __str__(self):
        return f"Fiche de paie de {self.employee} - {self.month}/{self.year}"

    class Meta:
        verbose_name = "Fiche de paie"
        verbose_name_plural = "Fiches de paie"

# Modèle de prime
class Bonus(models.Model):
    BONUS_TYPES = [
        ('PERFORMANCE', 'Prime de performance'),
        ('RETENTION', 'Prime de fidélité'),
        ('SPECIAL', 'Prime exceptionnelle'),
        ('OTHER', 'Autre'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Employé")
    type = models.CharField(max_length=20, choices=BONUS_TYPES, default='PERFORMANCE', verbose_name="Type de prime")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant")
    reason = models.TextField(verbose_name="Raison")
    date = models.DateField(auto_now_add=True, verbose_name="Date")
    is_approved = models.BooleanField(default=False, verbose_name="Approuvé")
    is_paid = models.BooleanField(default=False, verbose_name="Payé")

    def __str__(self):
        return f"{self.get_type_display()} - {self.employee} - {self.amount}"

    class Meta:
        verbose_name = "Prime"
        verbose_name_plural = "Primes"

# Modèle pour gérer les entretiens
class Interview(models.Model):
    job_application = models.ForeignKey(JobApplication, on_delete=models.CASCADE)  # Candidature associée
    interviewer = models.ForeignKey(User, on_delete=models.CASCADE)   # Intervieweur
    date = models.DateTimeField()  # Date de l'entretien
    notes = models.TextField()  # Notes de l'entretien
    status = models.CharField(max_length=20, default='PENDING')  # Statut de l'entretien

    def __str__(self):
        return f"Entretien pour {self.job_application.job_posting.title}"

# Modèle pour les statistiques de diversité
class DiversityStats(models.Model):
    year = models.IntegerField()  # Année des statistiques
    male_count = models.IntegerField(default=0)  # Nombre d'hommes
    female_count = models.IntegerField(default=0)  # Nombre de femmes
    other_count = models.IntegerField(default=0)  # Nombre d'autres genres
    created_at = models.DateTimeField(auto_now_add=True)  # Date de création

    def __str__(self):
        return f"Statistiques de diversité pour {self.year}"
    
class PerformanceStats(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)  # Employé associé
    year = models.IntegerField()  # Année de la performance
    performance_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])  # Score de performance
    created_at = models.DateTimeField(auto_now_add=True)  # Date de création

    def __str__(self):
        return f"Performance de {self.employee} en {self.year}"    