from pathlib import Path


_SUPPORTED = {".txt", ".md", ".csv"}
_MAX_BYTES = 300_000  # ~300 KB per file


def read_file(path_str: str) -> tuple[str, str]:
    """Read a local file and return (display_name, content).
    Raises ValueError with a user-friendly message on failure.
    """
    path = Path(path_str).expanduser().resolve()
    if not path.exists():
        raise ValueError(f"Arquivo não encontrado: {path}")
    if not path.is_file():
        raise ValueError(f"Não é um arquivo: {path}")

    suffix = path.suffix.lower()

    if suffix == ".docx":
        return _read_docx(path)

    if suffix not in _SUPPORTED:
        raise ValueError(
            f"Formato não suportado: {suffix}. "
            "Use .txt, .md, .csv ou .docx"
        )

    raw = path.read_bytes()
    if len(raw) > _MAX_BYTES:
        raw = raw[:_MAX_BYTES]
    content = raw.decode("utf-8", errors="replace")
    return path.name, content


def _read_docx(path: Path) -> tuple[str, str]:
    try:
        from docx import Document  # type: ignore
    except ImportError:
        raise ValueError("python-docx não instalado — tente: pip install python-docx")

    doc = Document(str(path))
    lines: list[str] = []
    for para in doc.paragraphs:
        lines.append(para.text)
    for table in doc.tables:
        for row in table.rows:
            lines.append(" | ".join(c.text.strip() for c in row.cells))
    content = "\n".join(lines)
    if len(content.encode()) > _MAX_BYTES:
        content = content.encode()[:_MAX_BYTES].decode("utf-8", errors="replace")
    return path.name, content


def list_folder(path_str: str) -> list[Path]:
    """Return supported files in a folder (non-recursive)."""
    folder = Path(path_str).expanduser().resolve()
    if not folder.is_dir():
        raise ValueError(f"Pasta não encontrada: {folder}")
    supported = _SUPPORTED | {".docx"}
    return sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in supported)
