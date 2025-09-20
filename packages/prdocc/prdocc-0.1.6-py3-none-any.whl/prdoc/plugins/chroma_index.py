from pathlib import Path
from typing import List

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions


class ChromaDocIndex:
    def __init__(self, collection_name: str = "prdoc"):
        self.client = chromadb.Client(Settings(anonymized_telemetry=False))
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            ),
        )
        self.counter = 0  # unique chunk IDs

    def add_file(self, path: Path, content: str, chunk_size: int = 512):
        """
        Split a doc file into chunks and store in vector DB.
        """
        chunks = [content[i : i + chunk_size] for i in range(0, len(content), chunk_size)]
        ids = [f"{path}-{i}" for i in range(len(chunks))]
        metadata = [{"path": str(path)}] * len(chunks)
        self.collection.add(documents=chunks, metadatas=metadata, ids=ids)

    def query(self, text: str, k: int = 3) -> List[Path]:
        results = self.collection.query(query_texts=[text], n_results=k)
        paths = {Path(md["path"]) for md in results["metadatas"][0]}
        return list(paths)
