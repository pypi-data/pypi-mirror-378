from macro_embeddings_flow.extract.extract import extract_S3
from macro_embeddings_flow.transform.transform import transform_embedding
from macro_embeddings_flow.load.load import loadEmbedding
import logging
from dotenv import load_dotenv

# Cargar variables de entorno si tienes un .env
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='embedding.log',
    filemode='a'
)


def MacroEtlEmbedding(url: str) -> str | None:
    """
    Se le pasa la URL de un archivo parquet en S3, descarga los chunks,
    los transforma a embeddings de 768 dimensiones y los vuelve a subir a S3.
    Retorna la lista de URLs de los embeddings subidos.

    You pass the URL of an S3 file with chunks, download it, transform it
    into 768-dimensional embeddings, and upload them back to S3.
    """

    # 1️⃣ Extraer
    archivo = extract_S3.extract(url)
    if not archivo:
        logging.error(f"Error al descargar los chunks desde {url}")
        return None

    # 2️⃣ Transformar
    embedding_data = transform_embedding.transform(archivo)
    if not embedding_data:
        logging.error(f"Error al transformar los chunks desde {url}")
        return None

    # 3️⃣ Cargar a S3
    s3_embedding = loadEmbedding.load(embedding_data)
    if not s3_embedding:
        logging.error(f"Error al subir chunks a S3 desde {url}")
        return None

    # 4️⃣ Retornar URLs de S3
    return s3_embedding
