# core/utils.py
import random
from django.core.mail import send_mail
from django.conf import settings

def generate_verification_code():
    """
    Génère un code de validation aléatoire à 6 chiffres.
    """
    return str(random.randint(100000, 999999))

def send_verification_email(user):
    """
    Envoie un e-mail avec le code de validation à l'utilisateur.
    """
    subject = "Confirmation de votre inscription"
    message = f"Votre code de validation est : {user.verification_code}"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])