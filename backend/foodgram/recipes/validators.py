from django.core.exceptions import ValidationError


def validate_no_zero(value):
    error = 'Поле не может равняться нулю.'
    if value == 0:
        raise ValidationError(
            f'{error}'
        )
