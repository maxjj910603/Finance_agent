from __future__ import annotations

import json
import os
import urllib.error
import urllib.request


class EmbeddingService:
    def __init__(self) -> None:
        self.host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
        self.model = os.getenv("EMBEDDING_MODEL", "qllama/bge-small-zh-v1.5:latest")

    def embed_text(self, text: str) -> list[float]:
        if not text.strip():
            raise ValueError("text must not be empty")

        embedding = self._embed_with_embed_api(text)
        if embedding is not None:
            return embedding

        embedding = self._embed_with_legacy_api(text)
        if embedding is not None:
            return embedding

        raise RuntimeError("Failed to generate embedding from Ollama")

    def _embed_with_embed_api(self, text: str) -> list[float] | None:
        payload = {
            "model": self.model,
            "input": text,
        }
        data = self._post_json("/api/embed", payload)
        if data is None:
            return None

        embeddings = data.get("embeddings")
        if isinstance(embeddings, list) and embeddings:
            first = embeddings[0]
            if isinstance(first, list):
                return [float(x) for x in first]
        return None

    def _embed_with_legacy_api(self, text: str) -> list[float] | None:
        payload = {
            "model": self.model,
            "prompt": text,
        }
        data = self._post_json("/api/embeddings", payload)
        if data is None:
            return None

        embedding = data.get("embedding")
        if isinstance(embedding, list) and embedding:
            return [float(x) for x in embedding]
        return None

    def _post_json(self, path: str, payload: dict) -> dict | None:
        req = urllib.request.Request(
            url=f"{self.host}{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError):
            return None
