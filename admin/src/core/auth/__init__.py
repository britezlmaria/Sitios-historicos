from core.auth import repository
from core.auth.validators import is_valid_email, is_valid_password


def create_user(**data):
    """
    Realiza la creacion de usuarios validando que se hayan ingresado los datos minimos para el usuario,
    los cuales son:
        -Email
        -Nombre
        -Apellido
        -Password
        -Activo: SI | NO
        -Rol

    Si no se ingresan alguno de estos campos mencionados agrega un mensaje al diccionario de errores un mensaje asociado al campo faltante,
    se crea una instancia de ValueError con el diccionario de errores y se levanta la excepcion. En caso contrario llamo a la operacion del respositorio
    para poder crear el usuario 'create_user' al cual le paso **data recibido como parametro
    """
    errors = {}

    if not data.get("email"):
        errors["email"] = "Email requerido"
    elif not is_valid_email(data["email"]):
        errors["email"] = "Formato de email inválido"
    if repository.get_user_by_email(data.get("email")):
        errors["email"] = "El email ya está en uso por otro usuario"

    if not data.get("name") or not data["name"].strip():
        errors["name"] = "Nombre requerido"

    if not data.get("last_name") or not data["last_name"].strip():
        errors["last_name"] = "Apellido requerido"

    if not data.get("password"):
        errors["password"] = "Contraseña requerida"
    elif not is_valid_password(data["password"]):
        errors["password"] = "La contraseña debe tener al menos 6 caracteres"

    if data.get("enabled") is None:
        errors["enabled"] = "Estado requerido"

    if not data.get("id_role"):
        errors["id_role"] = "Rol requerido"

    if errors:
        raise ValueError(errors)

    return repository.create_user(**data)


def update_user(user_id: int, **data):
    """
    Realiza la edicion de usuarios validando que, si los campos fueron modificados,
    estos no sean nulos, en caso de que no hayan sido modificados permancen inalterados.

    Los campos validados  son:
        -Email
        -Nombre
        -Apellido
        -Password
        -Activo: SI | NO
        -Rol


    Si hay algun error los agrega al diccionario de errores, enviandolo por parametro al crear
    la instancia de ValueError la cual es levantada para que pueda ser atrapada por el controller.
    """
    user = repository.get_user(user_id)
    if not user:
        raise ValueError({"general": "Usuario no encontrado"})

    errors = {}

    email = data.get("email", user.email)
    name = data.get("name", user.name)
    last_name = data.get("last_name", user.last_name)
    password = data.get("password")
    enabled = data.get("enabled", user.enabled)
    id_role = data.get("id_role", user.id_role)

    if not email:
        errors["email"] = "Email requerido"
    elif not is_valid_email(email):
        errors["email"] = "Formato de email inválido"

    if not name or not name.strip():
        errors["name"] = "Nombre requerido"

    if not last_name or not last_name.strip():
        errors["last_name"] = "Apellido requerido"

    if password and not is_valid_password(password):
        errors["password"] = "La contraseña debe tener al menos 6 caracteres"

    if enabled is None:
        errors["enabled"] = "Estado requerido"

    if not id_role:
        errors["id_role"] = "Rol requerido"

    if email != user.email and repository.get_user_by_email(email):
        errors["email"] = "El email ya está en uso por otro usuario"

    if errors:
        raise ValueError(errors)

    return repository.update_user(
        user_id,
        email=email.strip(),
        name=name.strip(),
        last_name=last_name.strip(),
        password=password,
        enabled=enabled,
        id_role=id_role,
    )


def create_role(**data):
    """
    Crea un nuevo rol en el sistema.

    Valida que el campo 'name' esté presente en los datos recibidos.
    Si falta el nombre, lanza una excepción ValueError con el mensaje correspondiente.
    Si la validación es exitosa, delega la creación del rol al repositorio.

    Parámetros:
        name (str): Nombre del rol.

    Excepciones:
        ValueError: Si no se proporciona el nombre del rol.
    """

    if not data.get("name"):
        raise ValueError("Nombre del rol requerido")

    return repository.create_role(**data)
