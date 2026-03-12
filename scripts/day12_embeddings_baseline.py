from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
from typing import Any
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
COLLECTION_NAME = "week2_day12_docs"
DATA_FILE = Path("data/day12_documents.json")
CACHE_DIR = Path(".cache/embeddings")
CACHE_FILE = CACHE_DIR / "day12_embedding_cache.json"
HF_CACHE_DIR = Path(".cache/huggingface")
QDRANT_URL = os.getenv("QDRANT_URL", "http://127.0.0.1:6333")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_embedding_cache() -> dict[str, list[float]]:
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    return {}


def save_embedding_cache(cache: dict[str, list[float]]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_documents() -> list[dict[str, Any]]:
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def get_model() -> SentenceTransformer:
    # Uses local HF cache directory under the repo
    os.environ.setdefault("HF_HOME", str(HF_CACHE_DIR.resolve()))
    return SentenceTransformer(MODEL_NAME)


def get_or_compute_embeddings(
    model: SentenceTransformer, documents: list[dict[str, Any]]
) -> list[list[float]]:
    cache = load_embedding_cache()
    vectors: list[list[float]] = []

    for doc in documents:
        text = doc["text"]
        key = sha256_text(text)

        if key in cache:
            vector = cache[key]
        else:
            vector = model.encode(text, normalize_embeddings=True).tolist()
            cache[key] = vector

        vectors.append(vector)

    save_embedding_cache(cache)
    return vectors


def recreate_collection(client: QdrantClient, vector_size: int) -> None:
    if client.collection_exists(COLLECTION_NAME):
        client.delete_collection(COLLECTION_NAME)

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=vector_size,
            distance=models.Distance.COSINE,
        ),
    )


def upsert_documents(
    client: QdrantClient, documents: list[dict[str, Any]], vectors: list[list[float]]
) -> None:
    points = []
    for idx, (doc, vector) in enumerate(zip(documents, vectors), start=1):
        points.append(
            models.PointStruct(
                id=idx,
                vector=vector,
                payload={
                    "doc_id": doc["id"],
                    "text": doc["text"],
                    "language": doc["language"],
                    "category": doc["category"],
                    "source": doc["source"],
                },
            )
        )

    client.upsert(collection_name=COLLECTION_NAME, points=points)


def run_search(client: QdrantClient, model: SentenceTransformer, query: str) -> None:
    query_vector = model.encode(query, normalize_embeddings=True).tolist()

    hits = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=3,
        with_payload=True,
    )

    print(f"\nQuery: {query}")
    for point in hits.points:
        payload = point.payload
        print(
            {
                "score": point.score,
                "doc_id": payload.get("doc_id"),
                "language": payload.get("language"),
                "category": payload.get("category"),
                "text": payload.get("text"),
            }
        )


def main() -> None:
    documents = load_documents()
    model = get_model()
    vectors = get_or_compute_embeddings(model, documents)

    if not vectors:
        raise RuntimeError("No vectors were generated.")

    client = QdrantClient(url=QDRANT_URL)
    recreate_collection(client, vector_size=len(vectors[0]))
    upsert_documents(client, documents, vectors)

    print(f"Loaded {len(documents)} documents into {COLLECTION_NAME}")
    print(f"Vector size: {len(vectors[0])}")
    print(f"Embedding cache file: {CACHE_FILE}")

    run_search(client, model, "How do I build APIs in Python?")
    run_search(client, model, " ہے؟ کیا سرچ ویکٹر ")


if __name__ == "__main__":
    main()
