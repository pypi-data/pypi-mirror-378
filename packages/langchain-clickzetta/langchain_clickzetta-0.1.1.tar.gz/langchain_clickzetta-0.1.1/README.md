# LangChain ClickZetta Integration

An integration package connecting ClickZetta and LangChain.

LangChain integration for ClickZetta, providing SQL queries, vector storage, and full-text search capabilities.

## Features

- **SQL Queries**: Natural language to SQL conversion and execution
- **Vector Storage**: Efficient vector storage and similarity search
- **Full-text Search**: Advanced text search capabilities with inverted index
- **Chat History**: Persistent conversation memory
- **Hybrid Search**: Combine vector and full-text search
- **True Hybrid Store**: Single table with both vector and inverted indexes (ClickZetta native)
- **Key-Value Store**: LangChain BaseStore implementation for persistent key-value storage
- **Document Store**: Structured document storage with metadata support
- **File Store**: Binary file storage using ClickZetta Volume
- **Volume Store**: Native ClickZetta Volume storage for large binary data

## Installation

```bash
pip install langchain-clickzetta
```

## Quick Start

### Basic Setup

```python
from langchain_clickzetta import ClickZettaEngine

# Create engine
engine = ClickZettaEngine(
    service="your-service",
    instance="your-instance",
    workspace="your-workspace",
    schema="your-schema",
    username="your-username",
    password="your-password",
    vcluster="your-vcluster"
)
```

### Vector Storage

```python
from langchain_clickzetta import ClickZettaVectorStore
from langchain_community.embeddings import DashScopeEmbeddings

# Setup embeddings
embeddings = DashScopeEmbeddings(
    dashscope_api_key="your-api-key",
    model="text-embedding-v4"
)

# Create vector store
vector_store = ClickZettaVectorStore(
    engine=engine,
    embeddings=embeddings,
    table_name="my_vectors"
)

# Add documents
texts = ["Hello world", "LangChain is great"]
vector_store.add_texts(texts)

# Search
results = vector_store.similarity_search("greeting", k=2)
```

### True Hybrid Search

```python
from langchain_clickzetta import ClickZettaHybridStore, ClickZettaUnifiedRetriever

# Create hybrid store (single table with vector + full-text indexes)
hybrid_store = ClickZettaHybridStore(
    engine=engine,
    embeddings=embeddings,
    table_name="hybrid_docs"
)

# Add documents
hybrid_store.add_texts([
    "ClickZetta is a high-performance analytics database",
    "LangChain enables building applications with LLMs"
])

# Create unified retriever
retriever = ClickZettaUnifiedRetriever(
    hybrid_store=hybrid_store,
    search_type="hybrid",  # "vector", "fulltext", or "hybrid"
    alpha=0.5  # Balance between vector and full-text search
)

# Search with hybrid approach
results = retriever.get_relevant_documents("analytics database")
```

### SQL Chain

```python
from langchain_clickzetta import ClickZettaSQLChain
from langchain_community.llms import Tongyi

llm = Tongyi(dashscope_api_key="your-api-key")

sql_chain = ClickZettaSQLChain.from_engine(
    engine=engine,
    llm=llm
)

result = sql_chain.invoke({"query": "How many tables are there?"})
print(result["result"])
```

### Key-Value Store

```python
from langchain_clickzetta import ClickZettaStore

# Create key-value store
store = ClickZettaStore(
    engine=engine,
    table_name="my_store"
)

# Store and retrieve data
store.mset([("key1", b"value1"), ("key2", b"value2")])
values = store.mget(["key1", "key2"])
print(values)  # [b'value1', b'value2']
```

### Document Store

```python
from langchain_clickzetta import ClickZettaDocumentStore

# Create document store
doc_store = ClickZettaDocumentStore(
    engine=engine,
    table_name="documents"
)

# Store document with metadata
doc_store.store_document(
    doc_id="doc1",
    content="This is a sample document",
    metadata={"author": "John", "category": "sample"}
)

# Retrieve document
content, metadata = doc_store.get_document("doc1")
```

### File Store

```python
from langchain_clickzetta import ClickZettaFileStore

# Create file store using ClickZetta Volume
file_store = ClickZettaFileStore(
    engine=engine,
    volume_type="user",
    subdirectory="my_files"
)

# Store binary file
with open("image.png", "rb") as f:
    content = f.read()
file_store.store_file("images/logo.png", content, "image/png")

# Retrieve file
file_content, mime_type = file_store.get_file("images/logo.png")
```

### Chat History

```python
from langchain_clickzetta import ClickZettaChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

# Create chat history
chat_history = ClickZettaChatMessageHistory(
    engine=engine,
    session_id="session123",
    table_name="chat_history"
)

# Add messages
chat_history.add_message(HumanMessage(content="Hello"))
chat_history.add_message(AIMessage(content="Hi there!"))

# Retrieve messages
messages = chat_history.messages
```

## Documentation

For more detailed documentation, see the main repository README and examples.

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

This package is released under the MIT License.