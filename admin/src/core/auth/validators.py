import re


def is_valid_email(email: str) -> bool:
    """
    Valida si el email tiene un formato correcto.

    Parámetros:
        email (str): Email a validar.

    Retorna:
        bool: True si el email es válido, False en caso contrario.
    """
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email))


def is_valid_password(password: str) -> bool:
    """
    Valida si la contraseña cumple con el mínimo de longitud.

    Parámetros:
        password (str): Contraseña a validar.

    Retorna:
        bool: True si la contraseña tiene al menos 6 caracteres, False en caso contrario.
    """
    return len(password) >= 6
