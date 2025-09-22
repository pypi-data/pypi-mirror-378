# Outline to Typst Converter

Convert [Outline](https://www.getoutline.com/) exports to [Typst](https://typst.app/) markup.

## Features

- **ProseMirror JSON support**: Converts Outline's ProseMirror-based exports to Typst markup
- **Simple Python API**: Convert with a single function call
- **Preserves document structure**: Headings, lists, code blocks, and formatting are retained
- **Easy integration**: Designed for use in scripts, pipelines, or larger applications

---

## Installation

```bash
pip install outline-typst
```

---

## Usage

### Basic Example

```python
from outline_typst import convert

# Example: ProseMirror JSON
outline_json = {
  ...fulljson
}
typst = convert(outline_json)
print(typst)
```

---

## Testing

Run all tests:

```bash
uv run pytest
```

---

## License

MIT License. See [LICENSE](LICENSE).
