# src/rag_chain.py
from typing import Dict, Any, Optional
from datetime import datetime
from zoneinfo import ZoneInfo

from langchain_community.vectorstores import Chroma
from langchain_community.llms import HuggingFaceHub
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import HuggingFaceEmbeddings

from src.config import settings
from src.prompts import SYSTEM_PRIMER, ANSWER_PROMPT
from src.router import route_intent


# --- Vector DB (Chroma) using HF embeddings ---
def _get_vectordb() -> Chroma:
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    return Chroma(
        persist_directory=settings.chroma_dir,
        embedding_function=embeddings,
        collection_name="mthotham",
    )


# --- LLM (Hugging Face Inference API) ---
def _get_llm() -> HuggingFaceHub:
    return HuggingFaceHub(
        repo_id=settings.hf_model,
        huggingfacehub_api_token=settings.hf_api_token,
        model_kwargs={"temperature": 0.2, "max_new_tokens": 512},
    )


def answer(question: str, intent: Optional[str] = None) -> Dict[str, Any]:
    """RAG answer: retrieve context from Chroma, generate via HF Inference."""
    final_intent = intent or route_intent(question)

    llm = _get_llm()
    vectordb = _get_vectordb()
    retriever = vectordb.as_retriever(search_kwargs={"k": 4})

    prompt = PromptTemplate(
        template=ANSWER_PROMPT,
        input_variables=["context", "question"],
        partial_variables={"system_primer": SYSTEM_PRIMER},
    )

    # Pipe: (question) -> retrieve -> prompt -> llm -> text
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    output = chain.invoke(question)

    return {
        "ok": True,
        "question": question,
        "intent": final_intent,
        "answer": output,
        "model": settings.hf_model,
        "time": datetime.now(ZoneInfo(settings.app_timezone)).isoformat(),
    }
