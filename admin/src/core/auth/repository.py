
from flask import current_app
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from core.auth.models import Permission, Role, Role_Permission, User
from core.database import db
from sqlalchemy.exc import IntegrityError
import secrets

# usuarios --------------------------------------


def is_deleted(user: User) -> bool:
    """
    Indica si el usuario está marcado como eliminado.

    Parámetros:
        user (User): El usuario a verificar.

    Retorna:
        bool: True si el usuario está eliminado, False en caso contrario.
    """
    return bool(user.deleted)


def get_not_deleted(query):
    """
    Aplica un filtro a una consulta para excluir usuarios eliminados.

    Parámetros:
        query: Consulta SQLAlchemy sobre el modelo User.

    Retorna:
        query: Consulta filtrada por usuarios no eliminados.
    """
    return query.filter(User.deleted == False)


def get_user(user_id: int) -> User | None:
    """
    Obtiene un usuario por su ID, excluyendo los eliminados.

    Parámetros:
        user_id (int): ID del usuario a buscar.

    Retorna:
        User: El usuario encontrado, o None si no existe o está eliminado.
    """
    stmt = (
        select(User)
        .options(joinedload(User.role))
        .where(User.id == user_id, User.deleted == False)
    )
    return db.session.scalar(stmt)


def get_user_by_email(email: str) -> User | None:
    """
    Obtiene un usuario por su email, excluyendo los eliminados.

    Parámetros:
        email (str): Email del usuario a buscar.

    Retorna:
        User: El usuario encontrado, o None si no existe o está eliminado.
    """
    stmt = (
        select(User)
        .options(joinedload(User.role))
        .where(User.email == email, User.deleted == False)
    )
    return db.session.scalar(stmt)


# asignaciones
def assign_role(user: User, role: Role) -> User:
    """
    Asigna un rol a un usuario y guarda el cambio en la base de datos.

    Parámetros:
        user (User): Usuario al que se asigna el rol.
        role (Role): Rol a asignar.

    Retorna:
        User: El usuario actualizado con el nuevo rol.
    """
    user.role = role
    db.session.commit()
    return user


def unassign_role(user: User) -> User:
    """
    Asigna el rol 'Usuario público' a un usuario.

    Si el rol no existe, lanza una excepción.

    Parámetros:
        user (User): Usuario al que se le reasigna el rol.

    Retorna:
        User: El usuario actualizado con el rol público.

    Excepciones:
        ValueError: Si no existe el rol 'Usuario público'.
    """
    default_role = get_role_by_name("Usuario público")
    if not default_role:
        raise ValueError("No existe el rol 'Usuario público' para desasignar.")
    user.role = default_role
    user.id_role = default_role.id_role
    db.session.commit()
    return user


# busqueda


def search_users(
    email=None, enabled=None, role_name=None, order_by_date="asc", page=1, per_page=25
) -> list[User]:
    """
    Busca usuarios filtrando por email, estado, rol y orden de fecha.

    Permite paginación de resultados.

    Parámetros:
        email (str, opcional): Email a buscar (parcial).
        enabled (bool, opcional): Estado de habilitación.
        role_name (str, opcional): Nombre del rol.
        order_by_date (str): 'asc' o 'desc' para ordenar por fecha de creación.
        page (int): Número de página.
        per_page (int): Cantidad de resultados por página.

    Retorna:
        list[User]: Lista de usuarios que cumplen los filtros.
    """
    query1 = db.session.query(User).join(Role)
    query = get_not_deleted(query1)
    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))
    if enabled is not None:
        query = query.filter(User.enabled == enabled)
    if role_name:
        query = query.filter(Role.name == role_name)

    if order_by_date.lower() == "desc":
        query = query.order_by(User.inserted_at.desc())
    else:
        query = query.order_by(User.inserted_at.asc())

    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)

    return query.all()


# bloqueo y desbloqueo de usuarios


def block_user(user_id: int) -> User | None:
    """
    Bloquea (deshabilita) un usuario, excepto si es administrador.

    Parámetros:
        user_id (int): ID del usuario a bloquear.

    Retorna:
        User: El usuario bloqueado, o None si no existe o está eliminado.

    Excepciones:
        ValueError: Si se intenta bloquear a un administrador.
    """
    user = get_user(user_id)

    if not user or is_deleted(user):
        return None
    if user.role and user.role.name == "Administrador":
        raise ValueError("No se puede bloquear a un administrador")
    user.enabled = False
    db.session.commit()
    return user


def unblock_user(user_id: int) -> User | None:
    """
    Desbloquea (habilita) un usuario.

    Parámetros:
        user_id (int): ID del usuario a desbloquear.

    Retorna:
        User: El usuario desbloqueado, o None si no existe o está eliminado.
    """
    user = get_user(user_id)

    if not user or is_deleted(user):
        return None
    user.enabled = True
    db.session.commit()
    return user


# roles --------------------------------------
def create_role(**kwargs):
    """
    Crea un nuevo rol en la base de datos.

    Recibe los datos del rol como argumentos clave-valor y los utiliza para instanciar un objeto Role.
    Guarda el nuevo rol en la base de datos y lo retorna.

    Parámetros:
        kwargs: Campos del modelo Role (por ejemplo, name).

    Retorna:
        Role: El objeto Role creado.
    """
    new_role = Role(**kwargs)
    db.session.add(new_role)
    db.session.commit()
    return new_role


def get_role_by_name(name: str) -> Role | None:
    """
    Busca un rol por su nombre.

    Parámetros:
        name (str): Nombre del rol a buscar.

    Retorna:
        Role: El rol encontrado, o None si no existe.
    """
    return db.session.query(Role).filter_by(name=name).first()


def assign_permission_to_role(role: Role, permission: Permission):
    """
    Asocia un permiso a un rol en la base de datos.

    Parámetros:
        role (Role): El rol al que se asigna el permiso.
        permission (Permission): El permiso a asignar.

    Retorna:
        Role_Permission: La relación creada entre rol y permiso.
    """
    role_permission = Role_Permission(role=role, permission=permission)
    db.session.add(role_permission)
    db.session.commit()
    return role_permission


def list_roles() -> list[Role]:
    """
    Devuelve la lista de todos los roles existentes en la base de datos.

    Retorna:
        list[Role]: Lista de objetos Role.
    """
    return db.session.query(Role).all()


# permisos --------------------------------------


def create_permission(name: str) -> Permission:
    """
    Crea un nuevo permiso en la base de datos.

    Parámetros:
        name (str): Nombre del permiso.

    Retorna:
        Permission: El objeto Permission creado.
    """
    perm = Permission(name=name)
    db.session.add(perm)
    db.session.commit()
    return perm


def get_permission_by_name(name: str) -> Permission | None:
    """
    Busca un permiso por su nombre.

    Parámetros:
        name (str): Nombre del permiso a buscar.

    Retorna:
        Permission: El permiso encontrado, o None si no existe.
    """
    return db.session.query(Permission).filter_by(name=name).first()


# CRUD
def list_users() -> list[User]:
    """
    Devuelve la lista de usuarios no eliminados de la base de datos.

    Retorna:
        list[User]: Lista de objetos User.
    """
    return db.session.query(User).filter(User.deleted == False).all()


def create_user(**kwargs) -> User:
    """
    Crea un nuevo usuario en la base de datos.

    Verifica que el email no esté en uso por otro usuario no eliminado.
    Si el email ya existe, lanza una excepción ValueError.
    Guarda el usuario y su contraseña hasheada.

    Parámetros:
        kwargs: Campos del modelo User.

    Retorna:
        User: El objeto User creado.

    """
    try:
        password: str = kwargs.pop("password")
        email = kwargs.get("email")
        new_user = User(**kwargs)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return new_user
    except Exception as e:
        db.session.rollback()
        raise ValueError("No se puede crear el usuario.") from e


def update_user(user_id: int, **kwargs) -> User | None:
    """
    Actualiza los datos de un usuario existente.

    Si el usuario no existe, retorna None.
    Actualiza los campos recibidos y la contraseña si se proporciona.

    Parámetros:
        user_id (int): ID del usuario a actualizar.
        kwargs: Campos a actualizar.

    Retorna:
        User: El usuario actualizado, o None si no existe.
    """
    user = get_user(user_id)
    if not user:
        return None

    password = kwargs.pop("password", None)
    for key, value in kwargs.items():
        setattr(user, key, value)

    if password:
        user.set_password(password)

    db.session.commit()
    return user


def delete_user(user_id: int) -> User | None:
    """
    Marca un usuario como eliminado en la base de datos.

    No permite eliminar usuarios con rol 'Administrador'.
    Si el usuario no existe o ya está eliminado, retorna None.

    Parámetros:
        user_id (int): ID del usuario a eliminar.

    Retorna:
        User: El usuario eliminado, o None si no existe o ya está eliminado.

    Excepciones:
        ValueError: Si se intenta eliminar un administrador.
    """
    user = get_user(user_id)
    if not user or is_deleted(user):
        return None
    if user.role and user.role.name == "Administrador":
        raise ValueError("No se puede eliminar a un administrador")
    user.deleted = True
    db.session.commit()
    return user


# verificar si tiene perimisos


def has_permission(user: User, permission_name: str) -> bool:
    """
    Verifica si un usuario tiene un permiso específico a través de su rol.

    Parámetros:
        user (User): El usuario a verificar.
        permission_name (str): Nombre del permiso.

    Retorna:
        bool: True si el usuario tiene el permiso, False en caso contrario.
    """
    if not user:
        return False

    p = get_permission_by_name(permission_name)
    if not p:
        return False

    role_permission = (
        db.session.query(Role_Permission)
        .filter_by(id_role=user.id_role, id_permission=p.id_permission)
        .first()
    )

    return role_permission is not None


def upsert_user_from_google(email: str, name: str, picture: str | None) -> User:
    """
    Crea o actualiza un usuario autenticado con Google.

    - Si no existe, lo crea con una contraseña aleatoria hasheada.
    - Si existe, actualiza nombre y avatar.
    - Maneja rollbacks y asigna rol por defecto si corresponde.
    """
    email_norm = email.strip().lower()
    if not email_norm:
        raise ValueError("Email vacío al intentar crear/actualizar usuario Google")

    try:
        user = get_user_by_email(email_norm)

        if not user:
            random_pw = secrets.token_urlsafe(32)
            user = User(
                email=email_norm,
                name=name or "",
                last_name="",
                avatar=picture,
                enabled=True,  
            )
            try:
                user.set_password(random_pw)
            except AttributeError:
                user.password = random_pw

            try:
                default_role = get_role_by_name("Usuario público")
            except Exception:
                default_role = None

            if default_role:
                user.role = default_role
                try:
                    user.id_role = default_role.id_role
                except Exception:
                    pass

            db.session.add(user)
            db.session.commit()
        return user

    except IntegrityError as ie:
        db.session.rollback()
        raise

    except Exception as e:
        db.session.rollback()
        raise