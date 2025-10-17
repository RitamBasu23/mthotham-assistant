# src/rag_chain.py
from typing import Dict, Any, Optional
from datetime import datetime
from zoneinfo import ZoneInfo
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

from langchain_community.vectorstores import Chroma
from langchain.llms import HuggingFacePipeline
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.embeddings import HuggingFaceEmbeddings

from src.config import settings
from src.prompts import SYSTEM_PRIMER, ANSWER_PROMPT
from src.router import route_intent


# ---------------------------------------------------------------------
# --- Vector DB (Chroma) using local HF embeddings ---
# ---------------------------------------------------------------------
def _get_vectordb() -> Chroma:
    embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model_name)
    return Chroma(
        persist_directory=settings.chroma_dir,
        embedding_function=embeddings,
        collection_name="mthotham",
    )


# ---------------------------------------------------------------------
# --- Local LLM (TinyLlama via HuggingFacePipeline) ---
# ---------------------------------------------------------------------
def _get_llm() -> HuggingFacePipeline:
    """
    Load a local TinyLlama model using HuggingFace transformers.
    No API token required. Uses GPU if available.
    """
    print(f"🔹 Loading model: {settings.llm_model_name} on device: {settings.device}")

    tokenizer = AutoTokenizer.from_pretrained(settings.llm_model_name)
    model = AutoModelForCausalLM.from_pretrained(
        settings.llm_model_name,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None,
    )

    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=512,
        temperature=0.2,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id,
        device=0 if torch.cuda.is_available() else -1,
    )

    return HuggingFacePipeline(pipeline=pipe)


# ---------------------------------------------------------------------
# --- Main RAG answer pipeline ---
# ---------------------------------------------------------------------
def answer(question: str, intent: Optional[str] = None) -> Dict[str, Any]:
    """
    RAG answer generation:
    1. Retrieve top documents from Chroma
    2. Insert context into prompt
    3. Generate grounded answer using TinyLlama
    """
    final_intent = intent or route_intent(question)

    llm = _get_llm()
    vectordb = _get_vectordb()
    retriever = vectordb.as_retriever(search_kwargs={"k": 4})

    prompt = PromptTemplate(
        template=ANSWER_PROMPT,
        input_variables=["context", "question"],
        partial_variables={"system_primer": SYSTEM_PRIMER},
    )

    # Pipeline: (question) -> retrieve -> prompt -> llm -> parse text
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
        "answer": output.strip(),
        "model": settings.llm_model_name,
        "time": datetime.now(ZoneInfo(settings.app_timezone)).isoformat(),
    }
