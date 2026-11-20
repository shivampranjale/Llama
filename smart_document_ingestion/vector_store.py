from smart_document_ingestion.config import CHROMA_DIR, get_api_key, get_embedding_model_name


def get_vector_store():
    import chromadb
    from llama_index.vector_stores.chroma import ChromaVectorStore

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection("smart_document_ingestion")
    return ChromaVectorStore(chroma_collection=collection), collection


def get_index():
    from llama_index.core import VectorStoreIndex
    from llama_index.embeddings.openai import OpenAIEmbedding

    vector_store, _ = get_vector_store()
    embedding_model = OpenAIEmbedding(
        model=get_embedding_model_name(),
        api_key=get_api_key(),
    )
    return VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        embed_model=embedding_model,
    )


def replace_source_nodes(nodes: list) -> int:
    if not nodes:
        raise ValueError("No nodes were provided for indexing.")

    index = get_index()
    _, collection = get_vector_store()
    source_names = {node.metadata["source_name"] for node in nodes}
    for source_name in source_names:
        collection.delete(where={"source_name": source_name})
    index.insert_nodes(nodes)
    return len(nodes)


def list_sources() -> list[str]:
    _, collection = get_vector_store()
    records = collection.get(include=["metadatas"])
    source_names = {
        metadata["source_name"]
        for metadata in records["metadatas"]
        if metadata and "source_name" in metadata
    }
    return sorted(source_names, key=str.casefold)
