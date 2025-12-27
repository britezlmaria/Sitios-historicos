from geoalchemy2.elements import WKTElement

from core import auth
from core.auth import repository
from core.feature_flags.models import Flag
from core.feature_flags.repository import create_flag, get_flag_by_enum
from core.historic_site import repository as historic_repo
from core.reviews import repository as reviews_repo
from core.tags import repository as tags_repo


def run():
    """
    Inicializa los datos base del sistema para desarrollo o testing.

    - Crea roles principales: Administrador, Editor y Usuario público.
    - Crea y asigna permisos a los roles.
    - Crea usuarios de ejemplo con distintos roles y estados.
    - Crea tags y categorías para sitios históricos.
    - Crea sitios históricos de ejemplo con sus relaciones.
    - Crea usuarios de sistema y configura feature flags iniciales.

    Al finalizar, imprime un resumen de los objetos creados.

    No recibe parámetros ni retorna valores.
    """
    admin_role = auth.create_role(name="Administrador")
    editor_role = auth.create_role(name="Editor")
    public_role = auth.create_role(name="Usuario público")

    # creo permisos
    permisos = [
        "user_index",
        "user_new",
        "user_update",
        "user_destroy",
        "user_show",
        "export_csv",
        "create_site",
        "edit_site",
        "delete_site",
        "list_sites",
        "block_user",
        "unblock_user",
        "tags_management",
        "reviews_management"
    ]

    created_perms = []
    for perm_name in permisos:
        perm = repository.get_permission_by_name(perm_name)
        if not perm:
            perm = repository.create_permission(perm_name)
        created_perms.append(perm)

    for perm in created_perms:
        try:
            repository.assign_permission_to_role(admin_role, perm)
        except Exception:
            pass

    for p in [
        "user_index",
        "user_show",
        "create_site",
        "edit_site",
        "list_sites",
        "tags_management",
    ]:
        perm = repository.get_permission_by_name(p)
        if perm:
            try:
                repository.assign_permission_to_role(editor_role, perm)
            except Exception:
                pass

    user1 = auth.create_user(
        email="alguno@gmail.com",
        name="Alguno",
        last_name="Perez",
        password="prueba_1",
        enabled=True,
        system_admin=False,
        id_role=admin_role.id_role,
        deleted=False,
    )

    user2 = auth.create_user(
        email="alguno2@gmail.com",
        name="Alguno2",
        last_name="Perez2",
        password="prueba_2",
        enabled=False,
        system_admin=False,
        id_role=public_role.id_role,
        deleted=False,
    )

    user3 = auth.create_user(
        email="test@gmail.com",
        name="Test",
        last_name="Test",
        password="testalgo",
        enabled=True,
        system_admin=False,
        id_role=editor_role.id_role,
        deleted=False,
    )

    tag_sitio_turistico = tags_repo.create_tag(name="SitioTuristico")

    tag_sitio_museo = tags_repo.create_tag(name="Museo")

    tag_sitio_educativo = tags_repo.create_tag(name="Educativo")

    tag_sitio_clasico = tags_repo.create_tag(name="Clásico")

    category_cultural = historic_repo.create_category(name="Cultural")

    category_religioso = historic_repo.create_category(name="Religioso")

    category_culinario = historic_repo.create_category(name="Culinario")
    

    palacio_legislatura_categories = [category_cultural]
    palacio_legislatura_tags = [tag_sitio_turistico, tag_sitio_clasico]
    palacio_legislatura = historic_repo.create_historic_site(
        user_id=user1.id,
        name="Palacio de la legislatura de la Provincia de Buenos Aires",
        short_description="Sede del Poder Legislativo de la Provincia de Buenos Aires",
        description="El Palacio de la Legislatura de la Provincia de Buenos Aires es un edificio emblemático que alberga las cámaras de Diputados y Senadores de la provincia. Su arquitectura neoclásica lo convierte en un ícono de la ciudad.",
        city="Ciudad de Buenos Aires",
        province="Buenos Aires",
        location=WKTElement("POINT(-57.9561 -34.9226)", srid=4326),
        state_of_conservation="bueno",
        inauguration_year=1898,
        visible=True,
        category=palacio_legislatura_categories,
        tags=palacio_legislatura_tags,
    )

    museo_ciencias_naturales_categories = [category_cultural]
    museo_ciencias_naturales_tags = [
        tag_sitio_turistico,
        tag_sitio_educativo,
        tag_sitio_museo,
    ]
    museo_ciencias_naturales = historic_repo.create_historic_site(
        user_id=user1.id,
        name="Museo de Ciencias Naturales, UNLP",
        short_description="Uno de los museos de ciencias naturales más importantes de Argentina",
        description="El Museo de Ciencias Naturales de la Universidad Nacional de La Plata es uno de los más importantes del país. Alberga una vasta colección de fósiles, minerales y especies de flora y fauna autóctona.",
        city="La Plata",
        province="Buenos Aires",
        location=WKTElement("POINT(-57.9319 -34.9085)", srid=4326),
        state_of_conservation="regular",
        inauguration_year=1908,
        visible=True,
        category=museo_ciencias_naturales_categories,
        tags=museo_ciencias_naturales_tags,
    )

    catedral_categories = [category_cultural, category_religioso]
    catedral_tags = [tag_sitio_turistico]
    catedral = historic_repo.create_historic_site(
        user_id=user1.id,
        name="Catedral de la Plata",
        short_description="Imponente catedral de estilo neogótico",
        description="La Catedral de la Plata es un edificio emblemático de la ciudad, conocido por su arquitectura neogótica y sus impresionantes vitrales. Inaugurada en 1902, es la sede de la Diócesis de La Plata.",
        city="La Plata",
        province="Buenos Aires",
        location=WKTElement("POINT(-57.9545 -34.9216)", srid=4326),
        state_of_conservation="malo",
        inauguration_year=1751,
        visible=True,
        category=catedral_categories,
        tags=catedral_tags,
    )
    
    facultad_informatica_categories = [category_cultural]
    facultad_informatica_tags = [tag_sitio_educativo]
    facultad_informatica = historic_repo.create_historic_site(
        user_id=user1.id,
        name="Facultad de Informática, UNLP",
        short_description="Facultad de Informática de la Universidad Nacional de La Plata",
        description="La Facultad de Informática de la UNLP es una institución educativa dedicada a la formación en ciencias de la computación y tecnología. Fundada en 1990, ofrece programas de grado y posgrado.",
        city="La Plata",
        province="Buenos Aires",
        location=WKTElement("POINT(-57.9410 -34.9090)", srid=4326),
        state_of_conservation="bueno",
        inauguration_year=1990,
        visible=True,
        category=facultad_informatica_categories,
        tags=facultad_informatica_tags,
    )
    
    estadio_unico_categories = [category_cultural]
    estadio_unico_tags = [tag_sitio_turistico, tag_sitio_clasico]
    estadio_unico = historic_repo.create_historic_site(
        user_id=user1.id,
        name="Estadio Único, La Plata",
        short_description="Estadio multipropósito de La Plata",
        description="El Estadio Único de La Plata es un moderno estadio multipropósito inaugurado en 2003. Alberga eventos deportivos y culturales, y es conocido por su arquitectura innovadora y capacidad para más de 50,000 espectadores.",
        city="La Plata",
        province="Buenos Aires",
        location=WKTElement("POINT(-57.9375 -34.9145)", srid=4326),
        state_of_conservation="bueno",
        inauguration_year=2003,
        visible=True,
        category=estadio_unico_categories,
        tags=estadio_unico_tags,
    )
    
    plaza_moreno_categories = [category_cultural]
    plaza_moreno_tags = [tag_sitio_clasico]
    plaza_moreno = historic_repo.create_historic_site(
        user_id=user1.id,
        name="Plaza Moreno, La Plata",
        short_description="Plaza central de La Plata",
        description="La Plaza Moreno es la plaza central de la ciudad de La Plata, rodeada por edificios emblemáticos como la Catedral y el Palacio Municipal. Es un punto de encuentro popular para residentes y turistas.",
        city="La Plata",
        province="Buenos Aires",
        location=WKTElement("POINT(-57.9412 -34.9214)", srid=4326),
        state_of_conservation="regular",
        inauguration_year=1882,
        visible=True,
        category=plaza_moreno_categories,
        tags=plaza_moreno_tags,
    )
    

    admin = auth.create_user(
        email="admin@gmail.com",
        name="Admin",
        last_name="Admin",
        password="admin1",
        enabled=True,
        system_admin=True,
        id_role=admin_role.id_role,
    )

    # historic_repo.upload_images(facultad_informatica.id, "https://picsum.photos/200/300", admin.id,"Imagen 1", "descripcion 1")
    # historic_repo.upload_images(facultad_informatica.id, "https://picsum.photos/200/300", admin.id,"Imagen 2", "descripcion 2")
    
    if not get_flag_by_enum(Flag.ADMIN_MAINTENANCE_MODE):
        create_flag(
            name=Flag.ADMIN_MAINTENANCE_MODE.value,
            description="Activa el modo mantenimiento del sistema de administración",
            enabled=False,
            maintenance_message="Sistema en mantenimiento programado.",
        )

    if not get_flag_by_enum(Flag.PORTAL_MAINTENANCE_MODE):
        create_flag(
            name=Flag.PORTAL_MAINTENANCE_MODE.value,
            description="Activa el modo mantenimiento del portal web público",
            enabled=False,
            maintenance_message="Portal en mantenimiento.",
        )

    if not get_flag_by_enum(Flag.REVIEWS_ENABLED):
        create_flag(
            name=Flag.REVIEWS_ENABLED.value,
            description="Habilita la creación y visualización de reseñas",
            enabled=True,
        )

    print(f"Roles creados: \n{admin_role}, \n{editor_role}, \n{public_role}")
    print(f"Usuarios creados:\n {user1}\n {user2}\n {user3}\n {admin}")
    print("Feature flags verificados correctamente")
    print(
        f"Sitios históricos creados:\n {palacio_legislatura}\n {museo_ciencias_naturales}\n {catedral}\n {facultad_informatica}\n {estadio_unico}\n {plaza_moreno}"
    )

    review1 = reviews_repo.create_review(
        user_id=user2.id,
        site_id=palacio_legislatura.id,
        rating=5,
        comment="Un lugar impresionante con mucha historia."
    )

    review2 = reviews_repo.create_review(
        user_id=user2.id,
        site_id=museo_ciencias_naturales.id,
        rating=4,
        comment="Muy educativo y entretenido para toda la familia."
    )

    review3 = reviews_repo.create_review(
        user_id=user2.id,
        site_id=catedral.id,
        rating=3,
        comment="La arquitectura es hermosa, pero el mantenimiento podría mejorar."
    )
    print(f"Reseñas creadas:\n {review1}\n {review2}\n {review3}")


