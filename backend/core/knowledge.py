"""Knowledge Engine v1."""


class KnowledgeRecord:
    """Represents a single structured knowledge item.

    Knowledge records are source-backed reference information. They are
    separate from memories, which represent experience-derived continuity.
    """

    def __init__(
        self,
        content: str,
        category: str,
        source: str,
        confidence: float,
        timestamp: str,
    ) -> None:
        self.content = content
        self.category = category
        self.source = source
        self.confidence = confidence
        self.timestamp = timestamp

    def __repr__(self) -> str:
        return (
            "KnowledgeRecord("
            f"content={self.content!r}, "
            f"category={self.category!r}, "
            f"source={self.source!r}, "
            f"confidence={self.confidence!r}, "
            f"timestamp={self.timestamp!r}"
            ")"
        )


class KnowledgeEngine:
    """Manages source-backed reference information.

    The Knowledge Engine owns knowledge records only. It does not manage
    memory, call external APIs, or perform model-based reasoning.
    """

    def __init__(self) -> None:
        self._knowledge: list[KnowledgeRecord] = []

    def create_knowledge(self, record: KnowledgeRecord) -> KnowledgeRecord:
        """Store a knowledge record and return it."""
        self._knowledge.append(record)
        return record

    def get_knowledge(self) -> list[KnowledgeRecord]:
        """Return all stored knowledge records."""
        return self._knowledge

    def retrieve_knowledge(self, query: str) -> list[KnowledgeRecord]:
        """Return records relevant to the query using keyword matching."""
        query_words = self._tokenize(query)
        if not query_words:
            return []

        scored_records = [
            (self._score_record(record, query_words), record)
            for record in self._knowledge
        ]
        relevant_records = [
            (score, record)
            for score, record in scored_records
            if score > 0
        ]
        relevant_records.sort(key=lambda item: item[0], reverse=True)

        return [record for _, record in relevant_records]

    def update_knowledge(
        self,
        record: KnowledgeRecord,
        confidence: float | None = None,
        source: str | None = None,
    ) -> KnowledgeRecord:
        """Update provided fields on a knowledge record and return it."""
        if confidence is not None:
            record.confidence = confidence

        if source is not None:
            record.source = source

        return record

    def _score_record(
        self,
        record: KnowledgeRecord,
        query_words: set[str],
    ) -> float:
        """Score deterministic relevance for v1 retrieval.

        Future versions can replace this with indexing, source reliability,
        freshness scoring, or semantic retrieval without changing the public
        KnowledgeEngine interface.
        """
        searchable_words = self._tokenize(
            f"{record.content} {record.category} {record.source}"
        )
        keyword_matches = len(query_words & searchable_words)

        if keyword_matches == 0:
            return 0.0

        return keyword_matches * (1.0 + record.confidence)

    def _tokenize(self, text: str) -> set[str]:
        """Convert text into normalized keyword tokens."""
        punctuation = ".,!?;:()[]{}\"'"
        return {
            word.strip(punctuation).lower()
            for word in text.split()
            if word.strip(punctuation)
        }
