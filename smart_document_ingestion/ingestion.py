import hashlib
import tempfile
from pathlib import Path


SUPPORTED_FILE_TYPES = {
    ".pdf": "pdf",
    ".html": "html",
    ".htm": "html",
    ".md": "markdown",
    ".py": "python",
}


def detect_file_type(filename: str) -> str:
    extension = Path(filename).suffix.lower()
    file_type = SUPPORTED_FILE_TYPES.get(extension)
    if file_type is None:
        supported = ", ".join(SUPPORTED_FILE_TYPES)
        raise ValueError(
            f"Unsupported file type '{extension or filename}'. Supported extensions: {supported}."
        )
    return file_type


def load_documents(file_path: Path, file_type: str):
    from llama_index.core import Document, SimpleDirectoryReader

    if file_type == "html":
        return [
            Document(
                text=file_path.read_text(encoding="utf-8", errors="replace"),
                metadata={"file_name": file_path.name},
            )
        ]
    return SimpleDirectoryReader(input_files=[str(file_path)]).load_data()


def parse_documents(documents: list, file_type: str) -> list:
    from llama_index.core.node_parser import (
        CodeSplitter,
        HTMLNodeParser,
        SentenceSplitter,
        SimpleFileNodeParser,
    )

    if file_type == "pdf":
        parser = SentenceSplitter(chunk_size=1024, chunk_overlap=100)
    elif file_type == "html":
        parser = HTMLNodeParser()
    elif file_type == "markdown":
        parser = SimpleFileNodeParser()
    elif file_type == "python":
        parser = CodeSplitter(
            language="python",
            chunk_lines=40,
            chunk_lines_overlap=10,
            max_chars=1500,
        )
    else:
        raise ValueError(f"Unsupported parser file type: {file_type}")
    return parser.get_nodes_from_documents(documents)


def normalize_nodes(nodes: list, source_name: str, file_type: str) -> list:
    from llama_index.core.schema import TextNode

    common_nodes = []
    for node_number, node in enumerate(nodes):
        metadata = {
            key: value if isinstance(value, (str, int, float, bool)) else str(value)
            for key, value in node.metadata.items()
        }
        metadata.update({"source_name": source_name, "file_type": file_type})
        node_id = hashlib.sha256(
            f"{source_name}:{node_number}:{node.text}".encode("utf-8")
        ).hexdigest()
        common_nodes.append(
            TextNode(id_=node_id, text=node.text, metadata=metadata)
        )
    return common_nodes


def ingest_file(file_path: Path, source_name: str) -> list:
    file_type = detect_file_type(source_name)
    documents = load_documents(file_path, file_type)
    parsed_nodes = parse_documents(documents, file_type)
    if not parsed_nodes:
        raise ValueError(f"No content was extracted from '{source_name}'.")
    return normalize_nodes(parsed_nodes, source_name, file_type)


def ingest_directory(directory_path: Path) -> tuple[list, list[str]]:
    if not directory_path.is_dir():
        raise NotADirectoryError(f"Folder not found: {directory_path}")

    files = sorted(path for path in directory_path.rglob("*") if path.is_file())
    supported_files = [
        path for path in files if path.suffix.lower() in SUPPORTED_FILE_TYPES
    ]
    skipped_files = [
        path.relative_to(directory_path).as_posix()
        for path in files
        if path.suffix.lower() not in SUPPORTED_FILE_TYPES
    ]
    if not supported_files:
        raise ValueError(
            f"No supported files found in '{directory_path}'. "
            "Supported types: PDF, HTML, Markdown, and Python."
        )

    nodes = []
    for file_path in supported_files:
        source_name = file_path.relative_to(directory_path).as_posix()
        nodes.extend(ingest_file(file_path, source_name))
    return nodes, skipped_files


def ingest_uploaded_file(source_name: str, content: bytes) -> list:
    suffix = Path(source_name).suffix.lower()
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temporary_file:
            temporary_file.write(content)
            temporary_path = Path(temporary_file.name)
        return ingest_file(temporary_path, source_name)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
