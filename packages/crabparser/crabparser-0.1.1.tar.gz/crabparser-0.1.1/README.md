# CrabParser 🦀

> High-performance text parsing library written in Rust with Python bindings

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/crabparser.svg)](https://badge.fury.io/py/crabparser)
[![Python versions](https://img.shields.io/pypi/pyversions/crabparser.svg)](https://pypi.org/project/crabparser/)

CrabParser is a blazingly fast text parsing library that splits documents and code files into semantic chunks. Built with Rust for maximum performance and memory efficiency, it provides Python bindings for easy integration into your projects.

## Key Features

- 🚀 **Pure Rust Performance** - 10x faster than pure Python implementations
- 📄 **Multi-Format Support** - Handles TXT, PDF, DOCX, CSV, and 12+ programming languages
- 🛡️ **Bulletproof Encoding** - Never fails on any file, handles all encodings gracefully
- 💾 **Memory Efficient** - ChunkedText keeps data in Rust memory with Python access
- ⚡ **Parallel Processing** - Leverages Rayon for concurrent operations
- 🧩 **Semantic Chunking** - Respects document structure (paragraphs, sentences, code blocks)

## Installation

```bash
pip install crabparser
```

## Quick Start

```python
from crabparser import TextParser, ChunkedText

# Create a parser instance
parser = TextParser(
    chunk_size=1000,          # Maximum characters per chunk
    respect_paragraphs=True,  # Keep paragraphs together
    respect_sentences=True    # Split at sentence boundaries
)

# Parse text
text = "Your long document text here..."
chunks = parser.parse(text)
print(f"Split into {len(chunks)} chunks")

# Parse with memory-efficient ChunkedText
chunked = parser.parse_chunked(text)
print(f"First chunk: {chunked[0]}")
print(f"Total size: {chunked.total_size} bytes")

# Parse files directly (auto-detects format)
chunks = parser.parse_file("document.pdf")  # Works with PDF, DOCX, CSV, TXT, and code files

# Save chunks to files
parser.save_chunks(chunks, "output_dir", "document")
```

## Supported Formats

### Documents
- **PDF** - Extracts and preserves text content
- **DOCX** - Full support for Word documents
- **CSV** - Intelligent handling of structured data
- **TXT** - Universal text files with encoding detection

### Programming Languages
Semantic code parsing that respects function and class boundaries:

- Python, JavaScript, TypeScript, Rust
- Go, Java, C#, C++
- Ruby, PHP, Swift, Kotlin

## API Reference

### TextParser

The main parser class for processing text and files.

```python
parser = TextParser(
    chunk_size=1000,          # Maximum size of each chunk
    respect_paragraphs=True,  # Maintain paragraph boundaries
    respect_sentences=True    # Maintain sentence boundaries
)
```

**Methods:**
- `parse(text: str) -> List[str]` - Parse text into chunks
- `parse_chunked(text: str) -> ChunkedText` - Memory-efficient parsing
- `parse_file(path: str) -> List[str]` - Parse any supported file
- `parse_file_chunked(path: str) -> ChunkedText` - Memory-efficient file parsing
- `save_chunks(chunks, output_dir, base_name) -> int` - Save chunks to files

### ChunkedText

Memory-efficient container that keeps chunks in Rust memory.

```python
# Access chunks without loading all into Python memory
chunked[0]            # First chunk
chunked[-1]           # Last chunk
len(chunked)          # Number of chunks
chunked.total_size    # Total size in bytes
chunked.source_file   # Source file path (if applicable)

# Iteration
for chunk in chunked:
    process(chunk)

# Get slice of chunks
batch = chunked.get_slice(0, 10)  # Get first 10 chunks
```

## Advanced Examples

### Processing Large PDFs

```python
from crabparser import TextParser

parser = TextParser(chunk_size=2000)

# Parse a large PDF file
chunks = parser.parse_file("research_paper.pdf")

# Process chunks
for i, chunk in enumerate(chunks):
    print(f"Chunk {i+1}: {chunk[:100]}...")
```

### Code File Parsing

```python
# Parse Python code while respecting function boundaries
parser = TextParser(
    chunk_size=1500,
    respect_paragraphs=True  # Keeps functions/classes together
)

chunks = parser.parse_file("main.py")
```

### Batch Processing with Memory Efficiency

```python
from pathlib import Path
from crabparser import TextParser

parser = TextParser(chunk_size=1000)
output_base = Path("output")

for file_path in Path("documents").glob("*.pdf"):
    # Use memory-efficient parsing
    chunked = parser.parse_file_chunked(str(file_path))

    # Process without loading all chunks into memory
    for i in range(len(chunked)):
        chunk = chunked[i]  # Only loads this chunk
        # Process chunk...

    # Save results
    parser.save_chunks(chunked, str(output_base), file_path.stem)
```

## Performance

CrabParser is designed for speed and efficiency:

- **10x faster** than pure Python text processing
- **Parallel chunk processing** using Rayon
- **Zero-copy operations** where possible
- **Memory-efficient** chunk streaming

## Links

- [GitHub Repository](https://github.com/Overstrider/CrabParser)
- [Bug Reports](https://github.com/Overstrider/CrabParser/issues)
- [PyPI Package](https://pypi.org/project/crabparser/)

## License

MIT License - see the [LICENSE](https://github.com/Overstrider/CrabParser/blob/main/LICENSE) file for details.

---

Made with 🦀 and ❤️ by the open-source community