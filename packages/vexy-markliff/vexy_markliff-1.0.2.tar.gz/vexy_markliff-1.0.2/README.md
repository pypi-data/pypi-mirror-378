# Vexy Markliff

A Python package and CLI tool for bidirectional conversion between Markdown/HTML and XLIFF 2.1 format, enabling high-fidelity localization workflows.

## Features

- **Bidirectional Conversion**: Seamless Markdown ↔ XLIFF and HTML ↔ XLIFF conversion
- **XLIFF 2.1 Compliant**: Full compliance with OASIS XLIFF 2.1 standard
- **Format Style Module**: Preserves HTML attributes and structure using fs:fs and fs:subFs
- **ITS 2.0 Support**: Native integration with W3C Internationalization Tag Set
- **Flexible Modes**: One-document and two-document translation workflows
- **Round-trip Fidelity**: Lossless Markdown → XLIFF → Markdown conversion
- **Intelligent Segmentation**: Smart sentence splitting for translation units
- **Skeleton Management**: External skeleton files for document structure preservation
- **Rich CLI**: Comprehensive command-line interface built with Fire
- **Modern Python**: Type hints, Pydantic models, and async support

## Installation

```bash
uv pip install --system vexy-markliff
```

or

```bash
uv add vexy-markliff
```

## Quick Start

### CLI Usage

```bash
# Convert Markdown to XLIFF
vexy-markliff md2xliff document.md document.xlf

# Convert HTML to XLIFF
vexy-markliff html2xliff page.html page.xlf

# Convert XLIFF back to Markdown
vexy-markliff xliff2md translated.xlf result.md

# Two-document mode (parallel source and target)
vexy-markliff md2xliff --mode=two-doc source.md target.md aligned.xlf
```

### Python API

```python
from vexy_markliff import VexyMarkliff

# Initialize converter
converter = VexyMarkliff()

# Convert Markdown to XLIFF
with open("document.md", "r") as f:
    markdown_content = f.read()

xliff_content = converter.markdown_to_xliff(
    markdown_content,
    source_lang="en",
    target_lang="es"
)

# Save XLIFF
with open("document.xlf", "w") as f:
    f.write(xliff_content)
```

## Advanced Usage

### Configuration

Create a `vexy-markliff.yaml` configuration file:

```yaml
source_language: en
target_language: es

markdown:
  extensions:
    - tables
    - footnotes
    - task_lists
  html_passthrough: true

xliff:
  version: "2.1"
  format_style: true
  its_support: true

segmentation:
  split_sentences: true
  sentence_splitter: nltk
```

Use the configuration:

```bash
vexy-markliff md2xliff --config=vexy-markliff.yaml input.md output.xlf
```

### Two-Document Mode

Process parallel source and target documents for alignment:

```python
from vexy_markliff import VexyMarkliff, TwoDocumentMode

converter = VexyMarkliff()

# Load source and target content
with open("source.md", "r") as f:
    source = f.read()
with open("target.md", "r") as f:
    target = f.read()

# Process parallel documents
result = converter.process_parallel(
    source_content=source,
    target_content=target,
    mode=TwoDocumentMode.ALIGNED
)

# Generate XLIFF with aligned segments
xliff_content = result.to_xliff()
```

### Custom Processing Pipeline

```python
from vexy_markliff import Pipeline, MarkdownParser, XLIFFGenerator

# Build custom pipeline
pipeline = Pipeline()
pipeline.add_stage(MarkdownParser())
pipeline.add_stage(CustomProcessor())  # Your custom processor
pipeline.add_stage(XLIFFGenerator())

# Process content
result = pipeline.process(markdown_content)
```

## Supported Formats

### Markdown Elements
- CommonMark compliant base
- Tables (GitHub Flavored Markdown)
- Task lists
- Strikethrough
- Footnotes
- Front matter (YAML/TOML)
- Raw HTML passthrough

### HTML Elements
- All HTML5 structural elements
- Text content elements (p, h1-h6, etc.)
- Inline formatting (strong, em, a, etc.)
- Tables with complex structures
- Forms and inputs
- Media elements (img, video, audio)
- Web Components and custom elements

### XLIFF Features
- XLIFF 2.1 Core compliance
- Format Style (fs) module for attribute preservation
- ITS 2.0 metadata support
- Translation unit notes
- Preserve space handling
- External skeleton files
- Inline element protection

## How It Works

1. **Parsing**: Markdown is parsed using markdown-it-py, HTML using lxml
2. **HTML Conversion**: Markdown is converted to HTML as intermediate format
3. **Content Extraction**: Translatable content is identified and extracted
4. **Structure Preservation**: Document structure is stored in skeleton files
5. **XLIFF Generation**: Content is formatted as XLIFF 2.1 with Format Style attributes
6. **Round-trip**: Translated XLIFF is merged with skeleton to reconstruct the original format

## Development

This project uses [Hatch](https://hatch.pypa.io/) for development workflow management.

### Setup Development Environment

```bash
# Install hatch if you haven't already
pip install hatch

# Create and activate development environment
hatch shell

# Run tests
hatch run test

# Run tests with coverage
hatch run test-cov

# Run linting
hatch run lint

# Format code
hatch run format
```

### Testing

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=vexy_markliff

# Run specific test file
python -m pytest tests/test_markdown_parser.py

# Run with verbose output
python -m pytest -xvs
```

## Documentation

Full documentation is available in the `docs/` folder:

- `500-intro.md` - Introduction to HTML-XLIFF handling
- `510-512-prefs-html*.md` - HTML element handling specifications
- `513-prefs-md.md` - Markdown element handling specifications
- `530-vexy-markliff-spec.md` - Complete technical specification

## Contributing

Contributions are welcome! Please ensure:

1. All tests pass
2. Code follows PEP 8 style guidelines
3. Type hints are provided
4. Documentation is updated

## License

MIT License

## Acknowledgments

Built on the XLIFF 2.1 OASIS standard and leverages:
- markdown-it-py for Markdown parsing
- lxml for XML/HTML processing
- Fire for CLI interface
- Pydantic for data validation