from ..contracts.contractsChunks import Extractor
import logging
from pathlib import Path 
import boto3
import os



logging.basicConfig(
    level=logging.INFO,              # Nivel mínimo de logs a mostrar
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='embedding.log',             # Opcional: guarda los logs en un archivo
    filemode='a'                    # 'a' append, 'w' overwrite
)

class extract_S3(Extractor):
    @classmethod
    def extract(self, s3_url: str) -> str:
        try:
            # Crear cliente S3
            s3 = boto3.client(
                "s3",
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=os.getenv("AWS_DEFAULT_REGION"),
            )

            # Validar URL
            if not s3_url.startswith("s3://"):
                raise ValueError("La URL debe comenzar con s3://")

            bucket, key = s3_url.replace("s3://", "").split("/", 1)

            # Crear carpeta destino si no existe
            output_dir = Path("datos_parquet")
            output_dir.mkdir(parents=True, exist_ok=True)

            # Nombre del archivo local
            local_file = output_dir / Path(key).name

            # Descargar
            s3.download_file(bucket, key, str(local_file))
            logging.info(f"📥 Archivo descargado en: {local_file}")

            return str(local_file)

        except Exception as e:
            logging.error(f"❌ Error al descargar {s3_url}: {e}", exc_info=True)
            return None