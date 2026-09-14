"""Stage 2: title-preserving paragraph chunks for the campus_life posts.

`split_documents` is the Milestone 3 replacement. It packs intact paragraphs
under a repeated source title, with a soft size target and no body overlap.
`fallback_split` keeps the starter's original fixed-window strategy available.
"""

from dataclasses import dataclass

import config
from ingest import Document


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in week 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Pack whole campus-post paragraphs, repeating their identifying title.

    CHUNK_SIZE is a soft limit: a single paragraph is never cut to meet it.
    There is no body overlap. Short posts stay whole; longer posts split only
    at existing blank lines, and every output retains its source and producer.
    """
    if config.CHUNK_SIZE <= 0:
        raise ValueError("CHUNK_SIZE must be positive")

    chunks: list[Chunk] = []
    for doc in documents:
        paragraphs = [p.strip() for p in doc.text.split("\n\n") if p.strip()]
        if not paragraphs:
            continue

        # The selected corpus uses a one-line title separated from its body.
        # An ordinary untitled, multi-line paragraph remains ordinary content.
        has_title = len(paragraphs) > 1 and "\n" not in paragraphs[0]
        title = paragraphs[0] if has_title else ""
        body = paragraphs[1:] if has_title else paragraphs
        prefix = title + "\n\n" if title else ""
        pending: list[str] = []
        index = 0

        for paragraph in body:
            candidate = prefix + "\n\n".join([*pending, paragraph])
            if pending and len(candidate) > config.CHUNK_SIZE:
                chunks.append(Chunk(
                    text=prefix + "\n\n".join(pending),
                    source=doc.source,
                    index=index,
                    produced_by="chunker.py::split_documents",
                ))
                index += 1
                pending = []
            pending.append(paragraph)

        if pending:
            chunks.append(Chunk(
                text=prefix + "\n\n".join(pending),
                source=doc.source,
                index=index,
                produced_by="chunker.py::split_documents",
            ))

    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
