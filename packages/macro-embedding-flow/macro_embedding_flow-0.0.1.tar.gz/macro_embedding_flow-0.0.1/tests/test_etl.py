import pytest
from macro_embeddings_flow.main import MacroEtlEmbedding

def test_macro_etl(monkeypatch):
    monkeypatch.setattr(
        "macro_embeddings_flow.extract.extract.extract_S3.extract",
        lambda url, *_: "datos_parquet/fake_chunk.parquet"
    )
    monkeypatch.setattr(
        "macro_embeddings_flow.transform.transform.transform_embedding.transform",
        lambda parquet_path, *_: ["datos_parquet/fake_chunk_transformed.parquet"]
    )
    monkeypatch.setattr(
        "macro_embeddings_flow.load.load.loadEmbedding.load",
        lambda chunks: ["s3://mi-bucket/fake_chunk_transformed.parquet"]
    )
    
    urls3 = MacroEtlEmbedding("s3://mi-bucket/fake_chunk.parquet")
    assert urls3 == ["s3://mi-bucket/fake_chunk_transformed.parquet"]

