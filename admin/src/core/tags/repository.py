import re
import unicodedata

from core.database import db
from core.tags.models import Tag


def list_tags(
    page: int = 1, per_page: int = 25, search: str = None, order: str = "recientes"
) -> tuple[list[Tag], int]:
    """
    Obtiene una lista paginada de etiquetas desde la base de datos segun los parametros indicados

    Args:
        page (int, optional): numero de pagina actual. Defaults to 1.
        per_page (int, optional): cantidad de elementos maxima de la pagina. Defaults to 25.
        search (str, optional): texto de filtrado para el nombre. Defaults to None.
        order (str, optional): orden en el que se ordenan los tags. Defaults to "recientes".

    Returns:
        tuple[list[Tag], int]:
        - list[Tag]: lista de etiquetas obtenidas
        - int : total de paginas obtenidas
    """
    query = db.session.query(Tag)

    # filtro por búsqueda
    if search:
        query = query.filter(Tag.name.ilike(f"%{search}%"))
    # orden
    if order == "alfabetico":
        query = query.order_by(Tag.name.asc())
    elif order == "inverso":
        query = query.order_by(Tag.name.desc())
    elif order == "antiguos":
        query = query.order_by(Tag.created_at.asc())
    else:  # recientes por defecto
        query = query.order_by(Tag.created_at.desc())

    query = query.filter_by(deleted=False)

    total = query.count()
    total_pages = (total + per_page - 1) // per_page
    tags = query.offset((page - 1) * per_page).limit(per_page).all()
    return tags, total_pages


def list_all_tags() -> list[Tag]:
    """
    Obtiene todas las etiquetas ordenadas alfabeticamente

    Returns:
        list[Tag]: lista con todas las etiquetas
    """
    return db.session.query(Tag).order_by(Tag.name.asc()).filter_by(deleted=False).all()


def create_tag(name: str) -> Tag:
    """
    Crea una nueva etiqueta en la base de datos

    Args:
        name (str): nombre de la etiqueta nueva

    Raises:
        ValueError: _name_ no debe estar vacio
        ValueError: _name_ debe tener entre 3 y 50 caracteres
        ValueError: ya existe un tag con el mismo nombre

    Returns:
        Tag: etiqueta creada
    """
    if not name:
        raise ValueError("Debe ingresar el nombre de la etiqueta")

    name_tag = slugify(name)
    if len(name_tag) > 50 or len(name_tag) < 3:
        raise ValueError("Debe ingresar entre 3 y 50 caracteres")

    existing = db.session.query(Tag).filter_by(name=name_tag, deleted=False).first()
    if existing:
        raise ValueError(f"Ya existe un tag con el nombre '{name_tag}'.")

    tag_deleted = db.session.query(Tag).filter_by(name=name_tag, deleted=True).first()
    if tag_deleted:
        tag_deleted.deleted = False
        db.session.commit()
        return tag_deleted

    new_tag = Tag(name=name_tag)
    db.session.add(new_tag)
    db.session.commit()
    return new_tag


def update_tag(tag_id: int, new_name: str) -> Tag:
    """
    Actualiza el nombre de una etiqueta seleccionada

    Args:
        tag_id (int): ID de la etiqueta a actualizar
        new_name (str): nuevo nombre para la etiqueta

    Raises:
        ValueError: _name_ no debe estar vacio
        ValueError: _name_ debe tener entre 3 y 50 caracteres
        ValueError: ya existe una etiqueta con el mismo nombre
        ValueError: etiqueta no encontrada

    Returns:
        Tag: etiqueta actualizada
    """
    if not new_name:
        raise ValueError("Debe ingresar el nombre de la etiqueta")

    name_tag = slugify(new_name)
    if len(name_tag) > 50 or len(name_tag) < 3:
        raise ValueError("Debe ingresar entre 3 y 50 caracteres")

    existing = db.session.query(Tag).filter_by(name=name_tag, deleted=False).first()
    if existing:
        raise ValueError(f"Ya existe una etiqueta con el nombre '{name_tag}'.")

    tag_deleted = db.session.query(Tag).filter_by(name=name_tag, deleted=True).first()
    if tag_deleted:
        db.session.delete(tag_deleted)

    tag = db.session.query(Tag).filter_by(id=tag_id).first()
    if not tag:
        raise ValueError("Etiqueta no encontrada.")
    tag.name = name_tag
    db.session.commit()
    return tag


def delete_tag(tag_id: int) -> None:
    """
    Hace un borrado logico de la etiqueta en la base de datos

    Args:
        tag_id (int): ID de la etiqueta a eliminar

    Raises:
        ValueError: etiqueta no encontrada
        ValueError: no se pudo eliminar la etiqueta porque esta asociada a algun sitio historico
    """
    tag = db.session.query(Tag).filter_by(id=tag_id).first()
    if not tag:
        raise ValueError("Etiqueta no encontrada.")
    if tag.historic_sites and len(tag.historic_sites) > 0:
        raise ValueError(
            "No se puede eliminar la etiqueta porque está asociada a sitios históricos."
        )
    tag.deleted = True
    db.session.commit()


def get_tag_by_id(tag_id: int) -> Tag | None:
    """
    Obtiene una etiqueta por el ID solicitado

    Args:
        tag_id (int): ID de la etiqueta a buscar

    Returns:
        Tag | None: etiqueta encontrada o None si no existe
    """
    if tag_id is None:
        return None
    return db.session.query(Tag).filter_by(id=tag_id).first()


def get_tags_by_ids(tag_ids: list[int]) -> list[Tag]:
    """
    Obtiene una lista de etiquetas por los IDs solicitados

    Args:
        tag_ids (list[int]): lista con los IDs de la estiquetas a buscar

    Returns:
        list[Tag]: Lista con las etiquetas encontradas
    """
    if not tag_ids:
        return []
    return db.session.query(Tag).filter(Tag.id.in_(tag_ids)).all()

def get_tags_by_names(tag_names: list[str]) -> list[Tag]:
    """
    Obtiene una lista de etiquetas por los nombres solicitados

    Args:
        tag_names (list[str]): lista con los nombres de las estiquetas a buscar

    Returns:
        list[Tag]: Lista con las etiquetas encontradas
    """
    if not tag_names:
        return []
    slugified_names = [slugify(name) for name in tag_names]
    return db.session.query(Tag).filter(Tag.name.in_(slugified_names)).all()

def slugify(text: str) -> str:
    """
    Funcion que convierte un nombre de etiqueta en un slug valido

    Args:
        text (str): nombre a convertir

    Returns:
        str: slug generado
    """
    # Normaliza el texto (quita acentos)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    # Pone todo en minúsculas
    text = text.lower()
    # Reemplaza cualquier caracter que no sea letra o número por guiones
    text = re.sub(r"[^a-z0-9]+", "-", text)
    # Quita guiones repetidos o al final
    text = text.strip("-")
    return text
