#  Registro y Preservación de Sitios Históricos

Proyecto desarrollado para el **Trabajo Integrador 2025** de la Facultad de Informática (**UNLP**). Esta plataforma permite documentar y difundir el patrimonio cultural nacional mediante un panel administrativo en **Flask** y un portal público en **Vue.js 3**.

---

##  Integrantes 
* [Matheo Lamiral](https://github.com/MatheoLamiral/MatheoLamiral)
* [Vicente Garcia Marti](https://github.com/Vicen621)
* [Francisco Acosta](https://github.com/franciscoacosta31)
* [Francisco Acosta]
* [Maria Luisa Britez](https://github.com/britezlmaria/britezlmaria)

---

##  Componentes del Sistema

* **Administración (Backend):** CRUD de sitios, gestión de usuarios, roles y moderación de reseñas desarrollado en **Python y Flask**.
* **Portal Público (Frontend):** Interfaz **Mobile First** con mapas interactivos y sistema de favoritos desarrollada en **Vue.js 3**.
* **Infraestructura Docker:** Contenedores para la base de datos georreferenciada y almacenamiento de objetos.

##  Funcionalidades Destacadas

* **Gestión Geoespacial:** Uso de **PostGIS** para almacenar coordenadas y **Leaflet** para mapas interactivos.
* **Feature Flags:** Control de mantenimiento y visibilidad exclusivo para el *System Admin*.
* **Historial de Modificaciones:** Trazabilidad completa de acciones sobre cada sitio histórico.
* **Moderación:** Flujo de aprobación/rechazo de reseñas con motivos obligatorios.
* **Exportación:** Descarga de listado de sitios en formato **CSV** con filtros aplicados.
* **Almacenamiento:** Gestión de múltiples imágenes por sitio almacenadas en **MinIO**.

##  Stack Tecnológico
* **Backend:** Python 3.12, Flask, SQLAlchemy, Flask-Session.
* **Frontend:** Vue.js 3.5, Bootstrap, Leaflet.
* **Base de Datos:** PostgreSQL 16 + PostGIS.
* **Servicios:** MinIO (Object Storage) y pgAdmin.
    

## Google Auth

Para usar el google auth se deben tener las siguientes variables en el .env de la carpeta admin

```properties
SECRET_KEY={cadena de caracteres segura}

GOOGLE_CLIENT_SECRET={secret de cliente oauth}
GOOGLE_CLIENT_ID={id cliente oauth}

FRONTEND_ORIGIN=http://localhost:5173 # Importante que sea localhost y no 127.0.0.1, no anda si no
GOOGLE_REDIRECT_URI=http://localhost:5000/api/auth/google/callback
```
## Credenciales de acceso

| Mail | Contraseña | Rol |
| :--: | :--------: | :-: |
| admin@gmail.com | admin1 | system admin |
| alguno1@gmail.com | prueba_1 | admin |
| test@gmail.com | testalgo | editor |


##  Ejecución con Docker

El proyecto utiliza Docker para levantar la infraestructura de forma rápida y consistente.
En el .env de la carpeta portal
```properties
VITE_API_BASE=http://localhost:5000

```

### Levantar Servicios
  ```bash
  docker-compose up -d
  ```

Servicios Disponibles

PostgreSQL (PostGIS): Localhost puerto 5433.

pgAdmin: http://localhost:5050.

MinIO Console: http://localhost:9001 (User/Pass: minioadmin).


