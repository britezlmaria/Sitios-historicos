import csv
import io
from datetime import datetime
from typing import Any, List

from geoalchemy2.shape import to_shape
from shapely import wkt
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from core.auth.models import User
from core.database import db
from core.historic_site.models import (
    Category,
    HistoricSite,
    Image,
    Modification,
    ModificationType,
)
from core.tags.models import Tag
from flask import current_app


def get_historic_site(historic_site_id: int) -> HistoricSite | None:
    """ "Obtiene un sitio historico por su ID"""
    return db.session.get(HistoricSite, historic_site_id)


def get_historic_site_by_name(name: str) -> HistoricSite | None:
    """ "Obtiene un sitio historico por su nombre"""
    return (
        db.session.query(HistoricSite)
        .filter(HistoricSite.name == name, HistoricSite.deleted == False)
        .first()
    )


# CRUD historic sites ----------------------------
def list_historic_sites_paginated(
    search: str = "",
    city: str = "",
    province: str = "",
    tags: list[str] = ["todas"],
    state: str = "",
    visible: bool = False,
    fecha_rango: str = "",
    order: str = "alfabetico_nombre",
    page: int = 1,
    per_page: int = 25,
) -> Any:
    """Lista los sitios historicos con paginación y filtros opcionales"""
    historic_sites = (
        select(HistoricSite)
        .options(
            selectinload(HistoricSite.images),
            selectinload(HistoricSite.tags),
            selectinload(HistoricSite.category),
        )
        .filter(HistoricSite.deleted == False)
        .order_by(HistoricSite.id.asc())
    )

    # filtros
    if search:
        historic_sites = historic_sites.filter(
            HistoricSite.name.ilike(f"%{search}%")
            | HistoricSite.short_description.ilike(f"%{search}%")
        )
    if city and city.lower() != "todas":
        historic_sites = historic_sites.filter(HistoricSite.city == city)
    if province and province.lower() != "todas":
        historic_sites = historic_sites.filter(HistoricSite.province == province)
    if tags and "todas" not in [t.lower() for t in tags]:
        historic_sites = historic_sites.join(HistoricSite.tags).filter(
            Tag.id.in_([int(t) for t in tags])
        )
    if state and state.lower() != "todos":
        historic_sites = historic_sites.filter(HistoricSite.state_of_conservation == state)
    if visible:
        historic_sites = historic_sites.filter(HistoricSite.visible.is_(True))
    if fecha_rango:
        fechas = fecha_rango.split(" a ")
        if len(fechas) == 2:
            fecha_inicio = datetime.strptime(fechas[0], "%Y-%m-%d")
            fecha_fin = datetime.strptime(fechas[1], "%Y-%m-%d")
            historic_sites = historic_sites.filter(
                HistoricSite.inserted_at >= fecha_inicio,
                HistoricSite.inserted_at <= fecha_fin,
            )

    # orden
    historic_sites = historic_sites.order_by(None)

    if order == "alfabetico_nombre":
        historic_sites = historic_sites.order_by(HistoricSite.name.asc())
    elif order == "inverso_nombre":
        historic_sites = historic_sites.order_by(HistoricSite.name.desc())
    elif order == "alfabetico_ciudad":
        historic_sites = historic_sites.order_by(HistoricSite.city.asc())
    elif order == "inverso_ciudad":
        historic_sites = historic_sites.order_by(HistoricSite.city.desc())
    elif order == "recientes":
        historic_sites = historic_sites.order_by(HistoricSite.inserted_at.desc())
    elif order == "antiguos":
        historic_sites = historic_sites.order_by(HistoricSite.inserted_at.asc())
    return db.paginate(historic_sites, page=page, per_page=per_page, error_out=False)


def list_historic_sites() -> list[HistoricSite]:
    """Lista todos los sitios historicos"""
    return db.session.query(HistoricSite).filter(HistoricSite.deleted == False).all()


def create_historic_site(user_id: int, **kwargs) -> HistoricSite | None:
    """Crea un nuevo sitio historico, si ya existe uno con el mismo nombre, lanza un ValueError"""
    exist = get_historic_site_by_name(kwargs.get("name"))
    if not exist:
        new_historic_site = HistoricSite(**kwargs)
    else:
        raise ValueError("El nombre del sitio historico ya está en uso.")
    db.session.add(new_historic_site)
    db.session.commit()
    modifications = []
    modifications.append(create_modification_type("Creación"))
    create_modification(
        type=modifications,
        id_historic_site=new_historic_site.id,
        id_user=user_id,
        date_time=db.func.now(),
    )
    return new_historic_site


def update_historic_site(
    historic_site_id: int, user_id: int, **kwargs
) -> HistoricSite | None:
    """Actualiza un sitio historico, si ya existe uno con el mismo nombre, lanza un ValueError"""
    historic_site = get_historic_site(historic_site_id)
    if not historic_site:
        return None
    in_use = get_historic_site_by_name(kwargs.get("name"))
    if in_use and in_use.id != historic_site_id:
        raise ValueError("El nombre del sitio historico ya está en uso.")

    modification_type = []
    if kwargs.get("tags") != historic_site.tags:
        cambio_de_tags = create_modification_type("Cambio de tags")
        modification_type.append(cambio_de_tags)
    if kwargs.get("state_of_conservation") != historic_site.state_of_conservation:
        cambio_de_estado = create_modification_type("Cambio de estado")
        modification_type.append(cambio_de_estado)
    new_inauguration_year = int(kwargs.get("inauguration_year"))
    new_visible = bool(kwargs.get("visible"))

    if (
        kwargs.get("name") != historic_site.name
        or kwargs.get("short_description") != historic_site.short_description
        or kwargs.get("description") != historic_site.description
        or kwargs.get("city") != historic_site.city
        or kwargs.get("province") != historic_site.province
        or new_inauguration_year != historic_site.inauguration_year
        or new_visible != historic_site.visible
        or compare_location(kwargs.get("location"), historic_site.location)
        or kwargs.get("category") != historic_site.category
    ):
        cambio_de_edicion = create_modification_type("Edición")
        modification_type.append(cambio_de_edicion)

    create_modification(
        type=modification_type,
        id_historic_site=historic_site.id,
        id_user=user_id,
        date_time=db.func.now(),
    )

    historic_site.tags.clear()
    historic_site.category.clear()
    for key, value in kwargs.items():
        setattr(historic_site, key, value)
    db.session.commit()
    return historic_site


def compare_location(new_location, old_location) -> bool:
    """Compara dos ubicaciones (WKT) y devuelve True si son diferentes"""
    new_location_shape = wkt.loads(new_location.data)
    historic_site_shape = to_shape(old_location)
    tolerance = 1e-7
    return (
        abs(new_location_shape.x - historic_site_shape.x) > tolerance
        or abs(new_location_shape.y - historic_site_shape.y) > tolerance
    )


def delete_historic_site(historic_site_id: int, user_id: int) -> HistoricSite | None:
    """Elimina un sitio historico (soft delete)"""
    historic_site = get_historic_site(historic_site_id)
    if not historic_site:
        return None
    historic_site.deleted = True
    db.session.commit()
    modifications = []
    modifications.append(create_modification_type("Eliminación"))
    create_modification(
        type=modifications,
        id_historic_site=historic_site.id,
        id_user=user_id,
        date_time=db.func.now(),
    )
    return historic_site

def increment_visit_count(historic_site_id: int) -> None:
    """Incrementa el contador de visitas de un sitio historico"""
    historic_site = get_historic_site(historic_site_id)
    if historic_site:
        historic_site.visit_count += 1
        db.session.commit()


# Category ----------------------------
def create_category(**kwargs):
    """Crea una nueva categoría"""
    new_category = Category(**kwargs)
    db.session.add(new_category)
    db.session.commit()
    return new_category


def get_categories_by_ids(category_ids: list[int]) -> list[Category]:
    """Obtiene una lista de categorías por sus IDs"""
    if not category_ids:
        return []
    return db.session.query(Category).filter(Category.id.in_(category_ids)).all()


def list_categories() -> list[Category]:
    """Lista todas las categorías"""
    return db.session.query(Category).all()


# Modifications ----------------------------
def list_modifications(
    historic_site_id: int,
    search: str,
    date_range: str,
    type: str,
    page: int,
    per_page: int,
) -> list[Modification]:
    """Lista las modificaciones de un sitio historico con paginación y filtros opcionales"""
    query = (
        db.session.query(Modification)
        .filter_by(id_historic_site=historic_site_id)
        .options(selectinload(Modification.type))
    )
    if search:
        query = query.join(User, User.id == Modification.id_user).filter(
            User.email.ilike(f"%{search}%")
        )
    if date_range:
        rng = date_range.strip()
        if " - " in rng:
            start_s, end_s = [s.strip() for s in rng.split(" - ", 1)]
        elif " to " in rng:
            start_s, end_s = [s.strip() for s in rng.split(" to ", 1)]
        elif " a " in rng:
            start_s, end_s = [s.strip() for s in rng.split(" a ", 1)]
        else:
            start_s = end_s = rng
        try:
            start = datetime.fromisoformat(start_s).date()
            end = datetime.fromisoformat(end_s).date()
            query = query.filter(func.date(Modification.date_time).between(start, end))
        except ValueError:
            pass

    if type and type != "todos":
        query = query.filter(Modification.type.any(ModificationType.name == type))
    query = query.order_by(Modification.date_time.desc())
    return db.paginate(query, page=page, per_page=per_page, error_out=False)


def create_modification(**kwargs) -> Modification:
    """Crea una nueva modificación"""
    new_modification = Modification(**kwargs)
    db.session.add(new_modification)
    db.session.commit()
    return new_modification


def create_modification_type(name: str) -> Modification:
    """Crea un nuevo tipo de modificación si no existe"""
    new_modification_type = ModificationType(name=name)
    db.session.add(new_modification_type)
    db.session.commit()
    return new_modification_type


# Otras funciones ----------------------------
def generate_csv_content(historic_sites):
    """Genera el contenido CSV de los sitios historicos proporcionados"""
    output = io.StringIO()
    writer = csv.writer(output, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)

    headers = [
        "ID",
        "Nombre",
        "Descripcion breve",
        "Ciudad",
        "Provincia",
        "Estado de conservacion",
        "Anio de inauguracion",
        "Fecha de registro",
        "Latitud",
        "Longitud",
        "Visible",
        "Tags asociados",
    ]
    writer.writerow(headers)

    # Escribir datos
    for site in historic_sites:
        # Obtener tags como string
        tags = "|".join([tag.name for tag in site.tags]) if site.tags else ""

        row = [
            site.id,
            site.name,
            site.short_description,
            site.city,
            site.province,
            site.state_of_conservation,
            site.inauguration_year,
            site.inserted_at.strftime("%Y-%m-%d") if site.inserted_at else "",
            site.lat,
            site.lon,
            "Si" if site.visible else "No",
            tags,
        ]
        writer.writerow(row)

    output.seek(0)
    return output


def get_all_cities() -> list[tuple[str]]:
    """Lista todas las ciudades"""
    result = (
        db.session.query(HistoricSite.city).distinct().order_by(HistoricSite.city).all()
    )
    return [r[0] for r in result]


def get_all_provinces() -> list[tuple[str]]:
    """Lista todas las provincias"""
    result = (
        db.session.query(HistoricSite.province)
        .distinct()
        .order_by(HistoricSite.province)
        .all()
    )
    return [r[0] for r in result]

def get_active_images(site_id: int):
    """Obtiene las imágenes activas de un sitio ordenadas por order_index"""
    return (
        Image.query
        .filter_by(id_historic_site=site_id, deleted=False)
        .order_by(Image.order_index.asc()) 
        .all()
    )

def upload_images(site_id: int, files, current_user_id: int, titles: list = None, descriptions: list = None) -> int:
    """Sube múltiples imágenes y retorna cantidad subida"""
    site = HistoricSite.query.get_or_404(site_id)
    active = get_active_images(site_id)

    if len(active) + len(files) > 10:
        raise ValueError("Límite de 10 imágenes por sitio")

    uploaded = 0
    for idx, file in enumerate(files):
        if not file or not file.filename:
            continue
        
        # Determinar título
        if titles and idx < len(titles) and titles[idx].strip():
            title = titles[idx].strip()
        else:
            raw_title = file.filename.rsplit(".", 1)[0]
            title = raw_title.strip() or "Sin título"
            if len(title) < 3:
                title = "Imagen " + str(len(active) + uploaded + 1)

        # Determinar descripción
        description = None
        if descriptions and idx < len(descriptions) and descriptions[idx].strip():
            description = descriptions[idx].strip()


        data = current_app.storage.upload_image(file, site_id)

        is_cover = len(active) == 0 and uploaded == 0  # primera imagen = portada

        image = Image(
            id_historic_site=site_id,
            image=data["url"],
            title=title,
            description=description,
            order_index=len(active) + uploaded,
            is_cover=is_cover,
            content_type=data["content_type"],
            size=data["size"],
        )
        db.session.add(image)
        uploaded += 1

    db.session.commit()
    return uploaded


def set_cover_image(site_id: int, image_id: int):
    """Establece una imagen como portada de un sitio histórico"""
    
    Image.query.filter_by(id_historic_site=site_id).update({"is_cover": False})
    image = Image.query.get_or_404(image_id)
    if image.id_historic_site != site_id or image.deleted:
        raise ValueError("Imagen no válida")
    image.is_cover = True
    db.session.commit()


def delete_image(image_id: int, site_id: int):
    """Elimina una imagen de un sitio histórico (borrado lógico)"""
    image = Image.query.get_or_404(image_id)
    if image.id_historic_site != site_id:
        raise ValueError("Permiso denegado")

    if image.is_cover:
        raise ValueError("No se puede eliminar la imagen de portada. Cambia la portada primero.")

    image.deleted = True
    db.session.commit()


def reorder_images(site_id: int, image_ids: list[int]):
    """Reordena las imágenes de un sitio histórico"""
    for index, image_id in enumerate(image_ids):
        image = Image.query.filter_by(id=image_id, id_historic_site=site_id).first()
        if image:
            image.order_index = index  
    
    db.session.commit()