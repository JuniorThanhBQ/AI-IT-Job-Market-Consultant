from agents.supervisor.orchestrator import Intent, execute_agent_flow
from sqlmodel import Session, select

from app.modules.company.models import Company
from app.modules.job.models import Job
from app.utils.embeddings import generate_embedding_async


class ConsultantService:
    def __init__(self, db: Session):
        self.db = db

    async def process_intent_flow(self, intent: Intent, user_input: str) -> dict:
        user_vector = await generate_embedding_async(user_input)

        stmt = (
            select(Job, Company)
            .join(Company, Job.company_id == Company.id)  # type: ignore[arg-type]
            .order_by(Job.embedding.cosine_distance(user_vector))  # type: ignore[union-attr]
            .limit(5)
        )

        result = self.db.exec(stmt)
        top_documents = result.all()

        rag_context = ""
        for idx, (job, company) in enumerate(top_documents, start=1):
            rag_context += f"--- Document {idx} ---\n"
            rag_context += f"Công ty: {company.name} | Lĩnh vực: {company.industry}\n"
            rag_context += f"Thông tin Công ty: {company.vector_context}\n"
            rag_context += (
                f"Vị trí tuyển dụng: {job.title} | Seniority: {job.seniority.value}\n"
            )
            rag_context += f"Mô tả công việc: {job.vector_context}\n\n"

        final_state = await execute_agent_flow(intent, user_input, rag_context)
        return final_state
