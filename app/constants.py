from django.core.validators import RegexValidator

MIN_EUROS_HORA = 9
phoneNumberRegex = RegexValidator(regex=r"^\+?1?\d{8,15}$")