from django.core.exceptions import ValidationError

SPECIAL = set('!@#$%^&*()\'\"\\./,><;:[]{}=-+?')

def validator_name(value):
    if any(char in SPECIAL for char in value):
        raise ValidationError("Invalid username")