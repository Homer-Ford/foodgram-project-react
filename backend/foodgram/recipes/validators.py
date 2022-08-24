from django.core.exceptions import ValidationError


def validate_no_zero(value):
    if value == 0:
        raise ValidationError(
            f'Поле не может равняться нулю.'
        )
