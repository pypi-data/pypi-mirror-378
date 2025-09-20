from abc import ABC, abstractmethod


class Extractor(ABC):
    @abstractmethod
    def extract(self, s3_url: str)-> str:
        """Recibe un S3 url (parquet) y devuelve otro S3 url (parquet procesado)."""
        """Receives an S3 URL (parquet) and returns another S3 URL (processed parquet)."""
        pass

class Transformation(ABC):
    @abstractmethod
    def transform(self, parquet_path: str)-> str:
        """transformacion de datos parquets y deja datos embeddings"""
        """transformation of parquet data and leaves data embeddings"""
        pass


class Loader(ABC):
    @abstractmethod
    def load(self, embedding_path: str)-> str:
        """carga del archivo parquet en se y devuelve url del s3 con los embeddings"""
        """Load the parquet file in se and return the s3 url with the embeddings"""
        pass