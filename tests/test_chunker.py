"""Boundary and content-preservation checks for the custom chunker."""

import unittest
from unittest.mock import patch

import config
from chunker import split_documents
from ingest import Document, load_documents


class ChunkerTests(unittest.TestCase):
    def test_corpus_preserves_every_body_paragraph_exactly_once(self):
        for doc in load_documents("campus_life"):
            with self.subTest(source=doc.source):
                chunks = split_documents([doc])
                title, *body = doc.text.split("\n\n")
                reconstructed = []
                for index, chunk in enumerate(chunks):
                    self.assertTrue(chunk.text.startswith(title + "\n\n"))
                    reconstructed.extend(chunk.text.split("\n\n")[1:])
                    self.assertEqual(chunk.source, doc.source)
                    self.assertEqual(chunk.index, index)
                    self.assertEqual(chunk.produced_by, "chunker.py::split_documents")
                self.assertEqual(reconstructed, body)

    def test_short_post_stays_whole(self):
        doc = Document("short.txt", "Library\n\nTerm hours.\n\nReading week hours.")
        self.assertEqual([c.text for c in split_documents([doc])], [doc.text])

    def test_title_repeats_when_body_is_split(self):
        doc = Document("hours.txt", "Library\n\nOpen until two.\n\nSilent third floor.")
        with patch.object(config, "CHUNK_SIZE", 29):
            chunks = split_documents([doc])
        self.assertEqual([c.text for c in chunks], [
            "Library\n\nOpen until two.", "Library\n\nSilent third floor."
        ])

    def test_oversized_paragraph_is_not_cut_or_duplicated(self):
        paragraph = "Sophomores draw randomly; juniors use credit hours first."
        doc = Document("lottery.txt", "Lottery\n\n" + paragraph + "\n\nMarch selection.")
        with patch.object(config, "CHUNK_SIZE", 30):
            chunks = split_documents([doc])
        self.assertEqual([c.text for c in chunks], [
            "Lottery\n\n" + paragraph, "Lottery\n\nMarch selection."
        ])

    def test_empty_inputs_produce_no_chunks(self):
        self.assertEqual(split_documents([]), [])
        self.assertEqual(split_documents([Document("empty.txt", " \n\n ")]), [])

    def test_untitled_single_paragraph_keeps_all_text(self):
        doc = Document("plain.txt", "One paragraph that must remain complete.")
        with patch.object(config, "CHUNK_SIZE", 10):
            self.assertEqual([c.text for c in split_documents([doc])], [doc.text])

    def test_invalid_target_is_rejected(self):
        with patch.object(config, "CHUNK_SIZE", 0):
            with self.assertRaises(ValueError):
                split_documents([Document("test.txt", "Some text.")])


if __name__ == "__main__":
    unittest.main()
