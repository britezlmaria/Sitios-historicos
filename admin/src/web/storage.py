import json
from minio import Minio
from minio.error import S3Error
from flask import current_app
from werkzeug.utils import secure_filename
from datetime import timedelta
import uuid

class Storage:
    def __init__(self, app=None):
        self._client = None
        self._bucket = None
        
        if app is not None:
            self.init_app(app)  
        
    def init_app(self, app):
        self._client = Minio(
            endpoint=app.config["MINIO_SERVER"],
            access_key=app.config["MINIO_ACCESS_KEY"],
            secret_key=app.config["MINIO_SECRET_KEY"],
            secure=app.config.get("MINIO_SECURE", False),
        )
        self._bucket = app.config["MINIO_BUCKET"]

        self._ensure_bucket(app)

        app.storage = self
        return app

    def _ensure_bucket(self, app):
        """Crea bucket y lo configura como público"""
        try:
            # Crear si no existe
            if not self._client.bucket_exists(self._bucket):
                self._client.make_bucket(self._bucket)
                app.logger.info(f"✓ Bucket '{self._bucket}' creado")
            
            # Hacer público el bucket
            policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{self._bucket}/*"]
                }]
            }
            self._client.set_bucket_policy(self._bucket, json.dumps(policy))
            app.logger.info(f"✓ Bucket '{self._bucket}' configurado como público")
        except S3Error as e:
            app.logger.warning(f"⚠ Error bucket: {e}")


    def upload_image(self, file, site_id: int) -> dict:
        """Sube una imagen al almacenamiento y devuelve su URL y metadatos."""
        if not file or file.filename == '':
            raise ValueError("No se seleccionó archivo")

        # Validar extensión
        ext = secure_filename(file.filename).rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if ext not in {'jpg', 'jpeg', 'png', 'webp'}:
            raise ValueError("Error: solo se permiten archivos con formato JPG, PNG o WEBP")

        # Validar MIME type
        allowed_mime = {'image/jpeg', 'image/png', 'image/webp'}
        if file.content_type not in allowed_mime:
            raise ValueError(f"Error: tipo MIME inválido: {file.content_type}")
        
        # Validar tamaño
        file.seek(0, 2)
        size = file.tell()
        file.seek(0)
        if size > 5 * 1024 * 1024:
            raise ValueError("Máximo 5MB")
        if size == 0:
            raise ValueError("Archivo vacío")

        object_name = f"public/sites/{site_id}/{uuid.uuid4()}.{ext}"

        try:
            self._client.put_object(
                bucket_name=self._bucket,
                object_name=object_name,
                data=file,                    
                length=size,
                content_type=file.content_type or "image/jpeg"
            )
        except S3Error as e:
            raise ValueError(f"Error MinIO: {e}")

        endpoint = current_app.config["MINIO_SERVER"]
        # Agregar http:// o https:// según MINIO_SECURE
        protocol = "https" if current_app.config.get("MINIO_SECURE", False) else "http"
        url = f"{protocol}://{endpoint}/{self._bucket}/{object_name}"

        return {
            "url": url,
            "filename": object_name,
            "size": size,
            "content_type": file.content_type
        }
        
    def delete_object(self, object_name: str):
        """Elimina un objeto del almacenamiento (Minio)."""
        try:
            self._client.remove_object(self._bucket, object_name)
        except S3Error as e:
            if current_app:
                current_app.logger.warning(f"No se pudo eliminar {object_name}: {e}")
    
storage = Storage()
     