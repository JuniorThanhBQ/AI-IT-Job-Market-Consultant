import httpx
import logging
from app.utils.embeddings import get_gemini_api_key

logger = logging.getLogger(__name__)

MARKET_ANALYSIS_PROMPT = """Bạn là một chuyên gia phân tích thị trường việc làm ngành IT.
Dưới đây là các dữ liệu công việc và công ty liên quan nhất trên thị trường hiện tại:

{rag_context}

Yêu cầu từ người dùng:
"{user_input}"

Nhiệm vụ: Dựa vào tập dữ liệu trên, hãy phân tích thị trường, xu hướng, yêu cầu kỹ năng và trả lời trực tiếp câu hỏi của người dùng một cách chuyên nghiệp.

YÊU CẦU BẮT BUỘC VỀ ĐỊNH DẠNG:
Chỉ trả về văn bản thuần túy (plain text). TUYỆT ĐỐI KHÔNG sử dụng cú pháp Markdown (không dùng dấu * để in đậm, in nghiêng, không dùng # tạo tiêu đề, không tạo danh sách gạch đầu dòng, không code block). Nếu cần liệt kê, hãy dùng số thứ tự thông thường (1., 2., 3.).
"""


async def run_market_analysis(user_input: str, rag_context: str) -> str:
    prompt = MARKET_ANALYSIS_PROMPT.format(
        rag_context=rag_context, user_input=user_input
    )

    api_key = get_gemini_api_key()

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            result_text = data["candidates"][0]["content"]["parts"][0]["text"]
            return result_text.strip()
    except Exception:
        logger.exception("Error calling Gemini API for market analysis")
        return "Xin lỗi, hiện tại tôi không thể phân tích thị trường do lỗi kết nối với AI."
