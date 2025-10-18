"""Utilidades para interactuar con Supabase Storage en Portfolio Manager."""
from __future__ import annotations

import json
import logging
import tempfile
from mimetypes import guess_type
from pathlib import Path
from typing import Any, Dict, Optional

from config import SupabaseConfig

try:  # pragma: no cover - dependencia opcional durante instalación inicial
    from supabase import Client, create_client
except Exception:  # pragma: no cover - supabase-py puede no estar instalado todavía
    Client = Any  # type: ignore
    create_client = None  # type: ignore


logger = logging.getLogger(__name__)


class SupabaseStorage:
    """Cliente ligero para manejar lectura/escritura en Supabase Storage."""

    def __init__(self) -> None:
        self._client: Optional[Any] = None
        self._bucket_validated: bool = False

    def _is_enabled(self) -> bool:
        return SupabaseConfig.is_configured()

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client

        if not self._is_enabled():
            raise RuntimeError("Supabase no está configurado correctamente.")

        if create_client is None:
            raise RuntimeError(
                "La librería 'supabase' no está instalada. Ejecuta 'pip install -r requirements.txt'."
            )

        self._client = create_client(  # type: ignore[arg-type]
            SupabaseConfig.SUPABASE_URL,
            SupabaseConfig.get_supabase_key(),
        )
        return self._client

    @staticmethod
    def _extract_error(response: Any) -> Optional[str]:
        """Obtiene el mensaje de error desde un StorageResponse o diccionario."""

        if response is None:
            return None

        if hasattr(response, "error"):
            error_obj = getattr(response, "error")
            if not error_obj:
                return None
            if isinstance(error_obj, dict):
                return (
                    error_obj.get("message")
                    or error_obj.get("error")
                    or str(error_obj)
                )
            return str(error_obj)

        if isinstance(response, dict):
            error_obj = response.get("error")
            if not error_obj:
                return None
            if isinstance(error_obj, dict):
                return (
                    error_obj.get("message")
                    or error_obj.get("error")
                    or str(error_obj)
                )
            return str(error_obj)

        return None

    def _ensure_bucket_exists(self, client: Any) -> None:
        """Valida que el bucket exista; si es posible, lo crea automáticamente."""

        if self._bucket_validated:
            return

        bucket_name = SupabaseConfig.SUPABASE_BUCKET_NAME
        if not bucket_name:
            raise RuntimeError("Nombre de bucket de Supabase no configurado.")

        storage_client = getattr(client, "storage", None)
        if storage_client is None:
            raise RuntimeError("El cliente de Supabase no expone el módulo de storage.")

        try:
            bucket_exists = False

            get_bucket_fn = getattr(storage_client, "get_bucket", None)
            if callable(get_bucket_fn):
                response = get_bucket_fn(bucket_name)
                error_message = self._extract_error(response)
                if not error_message:
                    bucket_exists = True
                elif "not found" not in error_message.lower():
                    raise RuntimeError(error_message)

            if not bucket_exists:
                list_fn = getattr(storage_client, "list_buckets", None)
                if callable(list_fn):
                    response = list_fn()
                    error_message = self._extract_error(response)
                    if error_message:
                        logger.debug("No se pudo listar buckets: %s", error_message)
                    data = getattr(response, "data", None)
                    if isinstance(data, list):
                        for item in data:
                            name = None
                            if isinstance(item, dict):
                                name = item.get("name") or item.get("id")
                            elif hasattr(item, "get"):
                                try:
                                    name = item.get("name")  # type: ignore[attr-defined]
                                except Exception:  # pragma: no cover - acceso dinámico best effort
                                    name = None
                            if name == bucket_name:
                                bucket_exists = True
                                break

            if bucket_exists:
                return

            if not SupabaseConfig.SUPABASE_SERVICE_ROLE_KEY:
                raise RuntimeError(
                    "El bucket de Supabase no existe y no hay clave de servicio para crearlo automáticamente."
                )

            create_fn = getattr(storage_client, "create_bucket", None)
            if not callable(create_fn):
                raise RuntimeError(
                    "No se puede crear el bucket automáticamente (método create_bucket no disponible)."
                )

            response = create_fn(
                bucket_name,
                {"public": True},
            )
            error_message = self._extract_error(response)
            if error_message:
                raise RuntimeError(error_message)

            logger.info("Bucket '%s' creado automáticamente en Supabase.", bucket_name)

        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("No se pudo validar o crear el bucket '%s': %s", bucket_name, exc)
        finally:
            # Evitar repetir validaciones en la misma ejecución; si falló, se registró el warning.
            self._bucket_validated = True

    def _get_bucket(self) -> Any:
        client = self._get_client()
        self._ensure_bucket_exists(client)
        return client.storage.from_(SupabaseConfig.SUPABASE_BUCKET_NAME)

    def load_portfolio_json(self, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Descarga el JSON del portafolio desde Supabase Storage.
        
        Args:
            user_id: UUID del usuario. Si se proporciona, busca en {user_id}/Informes/
        
        Returns:
            Diccionario con los datos del portfolio o None
        """
        if not self._is_enabled():
            logger.debug("Supabase deshabilitado; se omite descarga remota.")
            return None

        bucket = self._get_bucket()
        path = SupabaseConfig.portfolio_json_path(user_id)

        logger.info("Descargando portafolio desde Supabase: %s/%s", SupabaseConfig.SUPABASE_BUCKET_NAME, path)

        # Intentar descarga directa
        try:
            raw_bytes = bucket.download(path)
            if not raw_bytes:
                logger.warning("Respuesta vacía al descargar %s", path)
                return None
            data = json.loads(raw_bytes)
            return data
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("No se pudo descargar JSON desde Supabase: %s", exc)
            return None

    def save_portfolio_json(self, data: Dict[str, Any], user_id: Optional[str] = None) -> None:
        """
        Guarda el JSON del portafolio en Supabase Storage mediante upsert.
        
        Args:
            data: Datos del portfolio a guardar
            user_id: UUID del usuario. Si se proporciona, guarda en {user_id}/Informes/
        """
        if not self._is_enabled():
            raise RuntimeError("Supabase deshabilitado; no se puede guardar remotamente.")

        bucket = self._get_bucket()
        path = SupabaseConfig.portfolio_json_path(user_id)

        temp_file = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        try:
            json.dump(data, temp_file, ensure_ascii=False, indent=2, default=str)
            temp_file.flush()
            temp_path = Path(temp_file.name)
        finally:
            temp_file.close()

        logger.info(
            "Subiendo JSON del portafolio a Supabase: %s/%s",
            SupabaseConfig.SUPABASE_BUCKET_NAME,
            path,
        )

        try:
            with open(temp_path, "rb") as file_obj:
                response = bucket.upload(
                    path,
                    file_obj,
                    {
                        "content-type": "application/json",
                        "upsert": "true",
                    },
                )
            error_message = self._extract_error(response)
            if error_message:
                raise RuntimeError(error_message)
        finally:
            try:
                temp_path.unlink(missing_ok=True)
            except Exception:  # pragma: no cover - limpieza best effort
                pass

    def upload_chart_asset(self, local_path: Path, user_id: Optional[str] = None) -> Optional[Dict[str, str]]:
        """
        Sube un archivo de gráfico (HTML/PNG) al prefijo configurado.
        
        Args:
            local_path: Ruta local del archivo a subir
            user_id: UUID del usuario. Si se proporciona, guarda en {user_id}/Graficos/
        
        Returns:
            Diccionario con path y public_url del archivo subido
        """
        if not self._is_enabled():
            logger.debug("Supabase deshabilitado; no se sube %s", local_path)
            return None

        if not local_path.exists():
            logger.debug("Archivo no encontrado para subir a Supabase: %s", local_path)
            return None

        bucket = self._get_bucket()
        remote_path = SupabaseConfig.remote_chart_path_for(local_path, user_id)

        mime_type, _ = guess_type(str(local_path))
        content_type = mime_type or "application/octet-stream"

        logger.info("Subiendo gráfico a Supabase: %s/%s", SupabaseConfig.SUPABASE_BUCKET_NAME, remote_path)

        with open(local_path, "rb") as file_obj:
            response = bucket.upload(
                remote_path,
                file_obj,
                {
                    "content-type": content_type,
                    "upsert": "true",
                },
            )

        error_message = self._extract_error(response)
        if error_message:
            raise RuntimeError(error_message)

        public_url: Optional[str] = None
        try:
            public_url = bucket.get_public_url(remote_path)
        except Exception:  # pragma: no cover - bucket privado
            try:
                signed_url = bucket.create_signed_url(remote_path, 3600)
                if isinstance(signed_url, dict):
                    public_url = signed_url.get("signedURL") or signed_url.get("signed_url")
                elif isinstance(signed_url, str):
                    public_url = signed_url
            except Exception:
                public_url = None

        result: Dict[str, str] = {"path": remote_path}
        if public_url:
            result["public_url"] = public_url

        return result

    def download_chart_asset(self, remote_path: str) -> Optional[bytes]:
        if not self._is_enabled():
            logger.debug("Supabase deshabilitado; no se descarga %s", remote_path)
            return None

        bucket = self._get_bucket()

        try:
            return bucket.download(remote_path)
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("No se pudo descargar gráfico %s: %s", remote_path, exc)
            return None


__all__ = ["SupabaseStorage"]

