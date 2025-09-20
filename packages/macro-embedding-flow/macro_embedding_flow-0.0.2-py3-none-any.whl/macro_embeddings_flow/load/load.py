from ..contracts.contractsChunks import Loader
import boto3 
import logging
import os
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,              # Nivel mínimo de logs a mostrar
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='embedding.log',             # Opcional: guarda los logs en un archivo
    filemode='a'                    # 'a' append, 'w' overwrite
)

class loadEmbedding(Loader):
    @classmethod
    def load(self, embedding_path: str) -> str:
        try:
            path = Path(embedding_path)
            if not path.exists():
                logging.error(f"❌ El archivo parquet no existe: {embedding_path}")
                return None

            s3_bucket = os.environ.get("AWS_BUCKET_NAME")
            s3_prefix = os.environ.get("AWS_S3_PREFIX_EMBEDDINGS", "").strip("/")

            if not s3_bucket:
                logging.error("❌ No se encontró la variable de entorno AWS_BUCKET_NAME")
                return None

            s3 = boto3.client(
                "s3",
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=os.getenv("AWS_DEFAULT_REGION"),
            )

            file_name = path.name
            s3_key = f"{s3_prefix}/{file_name}" if s3_prefix else file_name

            s3.upload_file(str(path), s3_bucket, s3_key)
            logging.info(f"☁️ Embedding subido a S3: s3://{s3_bucket}/{s3_key}")

            return f"s3://{s3_bucket}/{s3_key}"
        except Exception as e:
            logging.error(f"❌ Error al subir {embedding_path} a S3: {e}", exc_info=True)
            return None
