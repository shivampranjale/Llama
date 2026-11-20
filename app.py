import argparse
from pathlib import Path

from smart_document_ingestion.ingestion import ingest_directory, ingest_file
from smart_document_ingestion.query import query_documents
from smart_document_ingestion.vector_store import replace_source_nodes


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ingest documents and query them with Smart Document Ingestion Lab."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    ingest_command = commands.add_parser(
        "ingest", help="Ingest supported documents from a folder or a single file."
    )
    ingest_command.add_argument("path", type=Path)

    query_command = commands.add_parser("query", help="Ask a question about ingested documents.")
    query_command.add_argument("question")

    arguments = parser.parse_args()
    if arguments.command == "ingest":
        if arguments.path.is_dir():
            nodes, skipped_files = ingest_directory(arguments.path)
            node_count = replace_source_nodes(nodes)
            print(
                f"Indexed {node_count} nodes from "
                f"{len({node.metadata['source_name'] for node in nodes})} files."
            )
            if skipped_files:
                print("Skipped unsupported files: " + ", ".join(skipped_files))
        elif arguments.path.is_file():
            nodes = ingest_file(arguments.path, arguments.path.name)
            node_count = replace_source_nodes(nodes)
            print(f"Indexed {node_count} nodes from {arguments.path.name}.")
        else:
            raise FileNotFoundError(f"File or folder not found: {arguments.path}")
    else:
        response = query_documents(arguments.question)
        print(response)
        for source_node in response.source_nodes:
            print(f"\nSource: {source_node.node.metadata.get('source_name', 'Unknown')}")
            print(source_node.node.text)


if __name__ == "__main__":
    main()
