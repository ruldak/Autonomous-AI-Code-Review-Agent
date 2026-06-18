from langchain_groq import ChatGroq
from app.config import settings
from app.models.review_models import ReviewResult
from app.agents.prompts.review_prompts import REVIEW_PROMPT
from app.utils.logger import logger

def add_line_numbers(code: str) -> str:
    """Menambahkan nomor baris eksplisit ke setiap baris kode agar LLM tidak menebak-nebak."""
    lines = code.split('\n')
    # Hitung jumlah digit agar rata kanan (misal: baris 1 sampai 100)
    max_digits = len(str(len(lines)))
    numbered_lines = []
    for i, line in enumerate(lines, start=1):
        # Format: "  1 | import os"
        numbered_lines.append(f"{i:>{max_digits}} | {line}")
    return '\n'.join(numbered_lines)

def get_llm():
    return ChatGroq(
        model="openai/gpt-oss-120b", 
        temperature=0.1,
        max_tokens=4096,
        groq_api_key=settings.GROQ_API_KEY,
    )

async def analyze_code_with_ai(filename: str, code: str, ast_info: dict) -> ReviewResult:
    """Mengirim kode dan AST ke Groq LLM untuk dianalisis."""
    if not settings.GROQ_API_KEY:
        logger.warning("GROQ_API_KEY not set. Skipping AI analysis.")
        return ReviewResult(findings=[], summary="AI analysis skipped: No API key.")

    logger.info("Starting AI analysis", filename=filename)
    
    llm = get_llm()
    
    # Format AST info menjadi string yang mudah dibaca LLM
    functions = ast_info.get('functions', [])
    classes = ast_info.get('classes', [])
    ast_summary = f"Functions: {', '.join(functions) if functions else 'None'}\nClasses: {', '.join(classes) if classes else 'None'}"
    
    # Ekstrak bahasa dari ekstensi file
    language = filename.split('.')[-1] if '.' in filename else 'text'

    code_with_lines = add_line_numbers(code)

    # Chain: Prompt -> LLM dengan Structured Output
    chain = REVIEW_PROMPT | llm.with_structured_output(ReviewResult)
    
    try:
        result = await chain.ainvoke({
            "language": language,
            "code": code_with_lines,
            "ast_info": ast_summary
        })
        logger.info("AI analysis completed", filename=filename, findings_count=len(result.findings))
        return result
    except Exception as e:
        logger.error("AI analysis failed", error=str(e), filename=filename)
        return ReviewResult(findings=[], summary=f"AI analysis failed: {str(e)}")