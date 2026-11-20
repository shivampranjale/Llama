from smart_document_ingestion.config import get_api_key, get_llm_model_name
from smart_document_ingestion.vector_store import get_index


def query_documents(question: str, similarity_top_k: int = 5):
    from llama_index.llms.openai import OpenAI

    if not question.strip():
        raise ValueError("Enter a question before searching.")
    index = get_index()
    query_engine = index.as_query_engine(
        llm=OpenAI(model=get_llm_model_name(), api_key=get_api_key()),
        similarity_top_k=similarity_top_k,
    )
    return query_engine.query(question)
