from datetime import UTC, datetime, timedelta

from flask import (
    Blueprint,
    Response,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
    current_app,
    jsonify
)
from geoalchemy2.elements import WKTElement

from core import historic_site
from core.auth import repository as auth_repository
from core.historic_site import repository
from core.tags import repository as tags_repository
from web.controllers import (
    admin_maintenance_check,
    error_message,
    permission_required,
    success_message,
)

historic_site_bp = Blueprint("historic_site_bp", __name__, url_prefix="/historic_sites")


@historic_site_bp.route("/list", methods=["GET"])
@permission_required("list_sites")
@admin_maintenance_check
def list(current_user=None):
    """ "Lista los sitios historicos con paginación y filtros opcionales"""
    current_user = auth_repository.get_user(session.get("user_id"))

    search = request.args.get("search", "").strip()
    city = request.args.get("city", "todas")
    province = request.args.get("province", "todas")
    tags = request.args.getlist("tags") or ["todas"]
    state = request.args.get("state", "todos")
    visible = request.args.get("visible", "") == "1"
    fecha_rango = request.args.get("fecha_rango", "")
    order = request.args.get("order")
    page = request.args.get("page", 1, type=int)
    historic_sites_pagination = repository.list_historic_sites_paginated(
        search=search,
        city=city,
        province=province,
        tags=tags,
        state=state,
        visible=visible,
        fecha_rango=fecha_rango,
        order=order,
        page=page,
        per_page=25,
    )
    historic_sites_json = [
        historic_site.to_dict() for historic_site in historic_sites_pagination.items
    ]

    cities = [c[0] for c in repository.get_all_cities()]
    provinces = [p[0] for p in repository.get_all_provinces()]
    all_tags = tags_repository.list_all_tags()

    return render_template(
        "historic_site/list.html",
        historic_sites=historic_sites_json,
        pagination=historic_sites_pagination,
        user=current_user,
        search=search,
        city=city,
        province=province,
        selected_tags=tags,
        state=state,
        visible=visible,
        fecha_rango=fecha_rango,
        order=order,
        page=page,
        cities=cities,
        provinces=provinces,
        all_tags=all_tags,
    )


@historic_site_bp.route("/create", methods=["GET", "POST"])
@permission_required("create_site")
@admin_maintenance_check
def create(current_user=None):
    """Crea un nuevo sitio historico"""
    current_user = auth_repository.get_user(session.get("user_id"))
    
    if request.method == "POST":
        form = request.form
        data = {
            "name": form.get("name"),
            "short_description": form.get("short_description"),
            "description": form.get("description"),
            "city": form.get("city"),
            "province": form.get("province"),
            "location": WKTElement(
                f'POINT({form.get("long")} {form.get("lat")})', srid=4326
            ),
            "state_of_conservation": form.get("state_of_conservation"),
            "inauguration_year": form.get("inauguration_year"),
            "visible": form.get("visible") == "on",
            "category": repository.get_categories_by_ids(form.getlist("categories")),
            "tags": tags_repository.get_tags_by_ids(form.getlist("tags")),
        }
        
        if (
            not data["name"]
            or not data["short_description"]
            or not data["description"]
            or not data["city"]
            or not data["province"]
            or not form.get("lat")
            or not form.get("long")
            or not data["state_of_conservation"]
            or not data["inauguration_year"]
        ):
            error_message("Por favor, completa todos los campos obligatorios.")
            return render_template(
                "historic_site/create.html", form=form, user=current_user
            )
        
        try:
            # Crear el sitio histórico
            new_site = repository.create_historic_site(current_user.id, **data)
            
            # Procesar imágenes si se subieron
            files = request.files.getlist("images")
            if files and any(f.filename for f in files):
                titles = request.form.getlist("titles[]")
                descriptions = request.form.getlist("descriptions[]")
                
                # Validar cantidad máxima
                if len(files) > 10:
                    flash("Máximo 10 imágenes permitidas. Se procesarán las primeras 10.", "warning")
                    files = files[:10]
                    titles = titles[:10] if titles else []
                    descriptions = descriptions[:10] if descriptions else []
                
                try:
                    count = repository.upload_images(
                        new_site.id,
                        files,
                        current_user.id,
                        titles=titles if titles else None,
                        descriptions=descriptions if descriptions else None
                    )
                    success_message(f"Sitio histórico creado con {count} imagen(es) exitosamente.")
                except Exception as img_error:
                    flash(f"Sitio creado, pero error al subir imágenes: {str(img_error)}", "warning")
            else:
                success_message("El sitio historico ha sido creado correctamente.")
            
            return redirect(url_for("historic_site_bp.list"))
            
        except ValueError as e:
            error_message("Error al crear el sitio historico.")
            return render_template(
                "historic_site/create.html", form=form, error=str(e), user=current_user
            )

    categories = repository.list_categories()
    tags = tags_repository.list_all_tags()
    return render_template(
        "historic_site/create.html",
        historic_site=historic_site,
        user=current_user,
        categories=categories,
        tags=tags,
    )


@historic_site_bp.route("/edit/<int:historic_site_id>", methods=["GET", "POST"])
@permission_required("edit_site")
@admin_maintenance_check
def update(historic_site_id, current_user=None):
    """Edita un sitio historico existente"""
    current_user = auth_repository.get_user(session.get("user_id"))
    historic_site = repository.get_historic_site(historic_site_id)
    if not historic_site:
        return redirect(url_for("not_found"))
    if request.method == "POST":
        form = request.form
        update_data = {
            "name": form.get("name"),
            "short_description": form.get("short_description"),
            "description": form.get("description"),
            "city": form.get("city"),
            "province": form.get("province"),
            "location": WKTElement(
                f'POINT({form.get("long")} {form.get("lat")})', srid=4326
            ),
            "state_of_conservation": form.get("state_of_conservation"),
            "inauguration_year": form.get("inauguration_year"),
            "visible": form.get("visible") == "on",
            "category": repository.get_categories_by_ids(form.getlist("categories")),
            "tags": tags_repository.get_tags_by_ids(form.getlist("tags")),
        }
        if (
            not update_data["name"]
            or not update_data["short_description"]
            or not update_data["description"]
            or not update_data["city"]
            or not update_data["province"]
            or not form.get("lat")
            or not form.get("long")
            or not update_data["state_of_conservation"]
            or not update_data["inauguration_year"]
        ):
            error_message("Por favor, completa todos los campos obligatorios.")
            return render_template(
                "historic_site/update.html",
                historic_site=historic_site,
                form=form,
                user=current_user,
            )
        try:
            repository.update_historic_site(
                historic_site.id, current_user.id, **update_data
            )
            success_message("El sitio historico ha sido editado correctamente.")
            return redirect(url_for("historic_site_bp.list"))
        except ValueError as e:
            error_message("Error al editar el sitio historico.")
            return render_template(
                "historic_site/update.html",
                historic_site=historic_site,
                form=form,
                error=str(e),
                user=current_user,
            )
    categories = repository.list_categories()
    tags = tags_repository.list_all_tags()
    # modifications = list_modifications(historic_site.id)
    return render_template(
        "historic_site/update.html",
        historic_site=historic_site,
        user=current_user,
        categories=categories,
        tags=tags,
    )


@historic_site_bp.route("/modifications/<int:historic_site_id>", methods=["GET"])
@permission_required("edit_site")
@admin_maintenance_check
def list_modifications(historic_site_id: int, current_user=None):
    """Lista las modificaciones de un sitio historico con paginación y filtros opcionales"""
    current_user = auth_repository.get_user(session.get("user_id"))
    historic_site = repository.get_historic_site(historic_site_id)
    search = request.args.get("search_user_modification", "")
    date_range = request.args.get("date_range_modification", "")
    type = request.args.get("modification_type", "todos")
    page = request.args.get("page", default=1, type=int)
    modifications = repository.list_modifications(
        historic_site_id, search, date_range, type, page, per_page=25
    )
    return render_template(
        "historic_site/list_modifications.html",
        modifications=modifications,
        historic_site=historic_site,
        user=current_user,
        search=search,
        date_range=date_range,
        type=type,
    )


@historic_site_bp.route("/delete/<int:historic_site_id>", methods=["POST"])
@permission_required("delete_site")
@admin_maintenance_check
def delete(historic_site_id, current_user=None):
    """Elimina un sitio historico (soft delete)"""
    current_user = auth_repository.get_user(session.get("user_id"))
    try:
        repository.delete_historic_site(historic_site_id, current_user.id)
        success_message("El sitio historico ha sido eliminado correctamente.")
    except ValueError as e:
        error_message("Error al eliminar el sitio historico." + str(e))
    return redirect(url_for("historic_site_bp.list"))


@historic_site_bp.route("/export-csv", methods=["GET"])
@permission_required("export_csv")
@admin_maintenance_check
def export_csv(current_user=None):
    """Exporta los sitios historicos filtrados a un archivo CSV"""
    try:
        # Obtener los filtros
        search = request.args.get("search", "").strip()
        city = request.args.get("city", "todas")
        province = request.args.get("province", "todas")
        tags = request.args.getlist("tags") or ["todas"]
        state = request.args.get("state", "todos")
        visible = request.args.get("visible", "") == "1"
        fecha_rango = request.args.get("fecha_rango", "")
        order = request.args.get("order", "alfabetico_nombre")

        # Aplicar los filtros
        historic_sites = repository.list_historic_sites_paginated(
            search=search,
            city=city,
            province=province,
            tags=tags,
            state=state,
            visible=visible,
            fecha_rango=fecha_rango,
            order=order,
            page=1,  # Página 1
            per_page=10000,  # Número alto para obtener todos los resultados
        )

        if not historic_sites:
            flash(
                "No hay sitios históricos para exportar con los filtros aplicados.",
                "warning",
            )
            return redirect(url_for("historic_site_bp.list"))

        # Generar CSV con los sitios filtrados
        csv_content = repository.generate_csv_content(historic_sites.items)

        # Crear nombre de archivo
        timestamp = (datetime.now(UTC) - timedelta(hours=3)).strftime(
            "%Y%m%d_%H%M"
        )

        filename = f"sitios_{timestamp}.csv"

        # Crear respuesta de descarga
        response = Response(
            csv_content.getvalue(),
            mimetype="text/csv; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

        return response

    except Exception as e:
        flash(f"Error al exportar datos: {str(e)}", "danger")
        return redirect(url_for("historic_site_bp.list"))

# Gestión de imágenes
@historic_site_bp.route("/<int:site_id>/images/upload", methods=["POST"])
@permission_required("edit_site")
@admin_maintenance_check
def images_upload(site_id, current_user=None):
    """Sube múltiples imágenes a un sitio histórico"""
    current_user = auth_repository.get_user(session.get("user_id"))
    files = request.files.getlist("images")
    
    # Obtener títulos y descripciones del formulario
    titles = request.form.getlist("titles[]")
    descriptions = request.form.getlist("descriptions[]")
    
    if not files or all(f.filename == "" for f in files):
        flash("Selecciona al menos una imagen", "danger")
    else:
        try:
            # Pasar títulos y descripciones al repository
            count = repository.upload_images(
                site_id, 
                files, 
                current_user.id,
                titles=titles if titles else None,
                descriptions=descriptions if descriptions else None
            )
            flash(f"{count} imagen/es subida/s correctamente", "success")
        except ValueError as e:
            flash(str(e), "danger")
    
    return redirect(url_for("historic_site_bp.update", historic_site_id=site_id))


@historic_site_bp.route("/<int:site_id>/images/<int:image_id>/cover", methods=["POST"])
@permission_required("edit_site")
@admin_maintenance_check
def images_set_cover(site_id, image_id, current_user=None): 
    """Establece una imagen como portada del sitio"""
    try:
        repository.set_cover_image(site_id, image_id)
        flash("Portada actualizada", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("historic_site_bp.update", historic_site_id=site_id))


@historic_site_bp.route("/<int:site_id>/images/<int:image_id>/delete", methods=["POST"])
@permission_required("edit_site")
@admin_maintenance_check
def images_delete(site_id, image_id, current_user=None):
    """Elimina una imagen del sitio (soft delete)"""
    try:
        repository.delete_image(image_id, site_id)
        flash("Imagen eliminada", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("historic_site_bp.update", historic_site_id=site_id))


@historic_site_bp.route("/<int:site_id>/images/reorder", methods=["POST"])
@permission_required("edit_site")
@admin_maintenance_check
def images_reorder(site_id, current_user=None):
    """Reordena las imágenes de un sitio"""
    image_ids = request.json.get("image_ids", [])
    try:
        repository.reorder_images(site_id, image_ids)
        return jsonify({"status": "ok"})
    except Exception:
        return jsonify({"status": "error"}), 400