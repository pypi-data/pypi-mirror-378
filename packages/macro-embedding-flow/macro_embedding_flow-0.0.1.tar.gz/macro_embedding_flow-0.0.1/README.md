# macro-embedding-flow

`macro-embedding-flow` es una librería de Python para transformar archivos **Parquet** en embeddings de 768 dimensiones usando modelos de **Sentence Transformers**, y subirlos nuevamente a S3 ya procesados.

---

## Español

### Descripción
Esta librería permite procesar un archivo Parquet chunk desde un bucket S3 y generar embeddings de 768 dimensiones. El resultado se guarda como un nuevo archivo Parquet y se sube al mismo bucket S3, en la ruta indicada por la variable de entorno `AWS_S3_PREFIX_EMBEDDINGS`.

### Instalación
```bash
pip install macro-embedding-flow
```
```bash
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_DEFAULT_REGION=
AWS_BUCKET_NAME=
AWS_S3_PREFIX_EMBEDDINGS=
```
##Uso básico

```bash
from macro_embedding_flow import transform

# URL S3 del archivo parquet chunk
s3_url = "s3://mi-bucket/path/al/chunk.parquet"

# Transformar y subir embeddings
transform(s3_url)
```



# macro-embedding-flow

`macro-embedding-flow` is a Python library for transforming Parquet files into 768-dimensional embeddings using Sentence Transformers models and uploading them back to S3 after processing.

---

## English

### Description
This library allows you to process a Parquet chunk file from an S3 bucket and generate 768-dimensional embeddings. The result is saved as a new Parquet file and uploaded to the same S3 bucket, in the path specified by the `AWS_S3_PREFIX_EMBEDDINGS` environment variable.

### Facility
```bash
pip install macro-embedding-flow
```
```bash
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_DEFAULT_REGION=
AWS_BUCKET_NAME=
AWS_S3_PREFIX_EMBEDDINGS=
```
##Basic use

```bash
from macro_embedding_flow import transform

# S3 URL of the parquet chunk file
s3_url = "s3://mi-bucket/path/al/chunk.parquet"

# Transform and upload embeddings
transform(s3_url)
```