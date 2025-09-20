import pytest
from macro_embeddings_flow.main import MacroEtlEmbedding

def test_macro_etl(monkeypatch):
    # Patch extract → devuelve el parquet descargado (local path simulado)
    monkeypatch.setattr(
        "macro_embeddings_flow.extract.extract.extract_S3.extract",
        lambda url, *_: "datos_parquet/fake_chunk.parquet"
    )

    # Patch transform → devuelve la lista de chunks (simulada)
    monkeypatch.setattr(
        "macro_embeddings_flow.transform.transform.transform_embedding.transform",
        lambda parquet_path, *_: ["datos_parquet/fake_chunk_transformed.parquet"]
    )

    # Patch load → recibe los chunks y devuelve UNA sola URL en S3 (string)
    monkeypatch.setattr(
        "macro_embeddings_flow.load.load.loadEmbedding.load",
        lambda chunks, *_: "s3://mi-bucket/fake_chunk_transformed.parquet"
    )

    # Ejecutar pipeline (la función ya retorna la URL única)
    result = MacroEtlEmbedding("s3://mi-bucket/fake_chunk.parquet")

    assert result == "s3://mi-bucket/fake_chunk_transformed.parquet"

