from enum import Enum
from typing import Any, Optional

import numpy as np

from texttools.base import BaseCategorizer
from texttools.handlers import ResultHandler


class EmbeddingCategorizer(BaseCategorizer):
    """
    Uses pre-stored embeddings on each Enum member.
    """

    def __init__(
        self,
        categories: Enum,
        embedding_model: Any,
        handlers: Optional[list[ResultHandler]] = None,
    ):
        """
        :param categories: your Enum class, whose members have `.embeddings`
        :param embedding_model: something with `.encode(text: str) -> list[float]`
        """
        super().__init__(categories, handlers)
        self.embedding_model = embedding_model

    def categorize(self, text: str) -> Enum:
        # 1. Preprocess
        text = self.preprocess(text)

        # 2. Encode the text
        vec = np.array(self.embedding_model.encode(text), dtype=float)

        # 3. Find best category
        best_cat = None
        best_score = -1.0

        for cat in self.categories:
            for proto in cat.embeddings:
                score = self._cosine_similarity(vec, proto)
                if score > best_score:
                    best_score = score
                    best_cat = cat

        self._dispatch({text: best_cat})
        return best_cat

    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        return float(a.dot(b) / (np.linalg.norm(a) * np.linalg.norm(b)))
