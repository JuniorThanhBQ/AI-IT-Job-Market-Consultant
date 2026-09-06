from rank_bm25 import BM25Okapi
from sqlmodel import Session, select

from app.modules.job.models import Job


class BM25Index:
    bm25: BM25Okapi | None = None
    job_ids: list[int] = []

    @classmethod
    def build(cls, session: Session) -> None:
        results = session.exec(select(Job.id, Job.vector_context)).all()
        if not results:
            cls.job_ids = []
            cls.bm25 = None
            return
        cls.job_ids = [row[0] for row in results if row[0] is not None]
        corpus = [row[1].lower().split() for row in results]
        cls.bm25 = BM25Okapi(corpus)

    @classmethod
    def search(cls, query: str, top_n: int = 30) -> list[tuple[int, float]]:
        if cls.bm25 is None or not cls.job_ids:
            return []
        tokens = query.lower().split()
        scores = cls.bm25.get_scores(tokens)
        indexed = sorted(enumerate(scores), key=lambda item: item[1], reverse=True)[
            :top_n
        ]
        return [(cls.job_ids[index], score) for index, score in indexed if score > 0.0]

    @classmethod
    def refresh(cls, session: Session) -> None:
        cls.build(session)
