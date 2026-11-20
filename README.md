# Smart Document Ingestion Lab

A small, function-based Python CLI for parsing documents, indexing them in a
local Chroma vector store, and querying them with OpenAI models.

## Ingestion flow

```text
File → type detection → parser/splitter → common TextNodes
     → text-embedding-3-small → Chroma → query engine (gpt-4.1-nano)
```

| File type | Parser |
| --- | --- |
| PDF | `SentenceSplitter` |
| HTML | `HTMLNodeParser` |
| Markdown | `SimpleFileNodeParser` |
| Python | `CodeSplitter` |

## Setup

Install dependencies and add your API key to `.env`:

```powershell
python -m pip install -r requirements.txt
```

```dotenv
OPENAI_API_KEY=
OPENAI_EMBEDDING_MODEL=
OPENAI_LLM_MODEL=
```

The empty model variables use `text-embedding-3-small` and `gpt-4.1-nano` by
default. Set `OPENAI_LLM_MODEL` if you intended a different nano model ID.

## Use

```powershell
python app.py ingest data
python app.py query "What is the main idea?"
```

The ingest command scans the given folder and its subfolders, indexing all PDF,
HTML, Markdown, and Python files it finds. Unsupported files are reported and
skipped. A single supported file path can also be passed instead of a folder.
The persistent Chroma database is stored in `storage\chroma`. Re-ingesting a
file replaces its previously indexed nodes. `Data_Loaders_Llama.ipynb` remains
available as the original parser tutorial.
