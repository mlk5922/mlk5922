#core/validators.py
from django.core.exceptions import ValidationError
from datetime import date
import re

def validate_future_date(value):
    if value < date.today():
        raise ValidationError('La date ne peut pas être dans le passé.')

def validate_phone_number(value):
    pattern = r'^\+?1?\d{9,15}$'
    if not re.match(pattern, value):
        raise ValidationError('Numéro de téléphone invalide.')

def validate_file_size(value):
    filesize = value.size
    if filesize > 10485760:  # 10MB
        raise ValidationError("La taille maximale du fichier est de 10MB")
