from flask import render_template


def error_401(error):
    return (
        render_template(
            "error.html",
            number=401,
            name="No autorizado",
            description="No tienes permisos para acceder a esta página.",
        ),
        401,
    )


def error_500(error):
    return (
        render_template(
            "error.html",
            number=500,
            name="Error interno del servidor",
            description="Ocurrió un error inesperado en el servidor.",
        ),
        500,
    )


def error_404(error):
    return (
        render_template(
            "error.html",
            number=404,
            name="No encontrado",
            description="La página que estás buscando no existe.",
        ),
        404,
    )
