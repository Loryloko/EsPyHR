# AVANZAMENTO 3 - ELABORAZIONE DOCUMENTI 

# import os
# import uuid
# from .config import Config
#
#
# class DocumentProcessor:
#
#     @staticmethod
#     def process_documents():
#         documents = []
#         metadatas = []
#         ids = []
#
#         for filename in os.listdir(Config.DOCUMENTS_DIR):
#             if filename.endswith(".txt"):
#                 with open(
#                     os.path.join(Config.DOCUMENTS_DIR, filename),
#                     "r",
#                     encoding="utf-8"
#                 ) as file:
#
#                     chunks = file.read().replace("\n", ".").split("### ")
#
#                     for chunk in chunks:
#                         if chunk.strip():
#                             documents.append(chunk)
#                             metadatas.append({"source": filename})
#                             ids.append(str(uuid.uuid4()))
#
#         return documents, metadatas, ids
#
#     @staticmethod
#     def read_first_lines(file_path, n_lines=100):
#         with open(file_path, "r", encoding="utf-8") as file:
#             return [
#                 line.strip()
#                 for line, _ in zip(file, range(n_lines))
#             ]


# AVANZAMENTO 4 - SINCRONIZZAZIONE DOCUMENTI

import os
import uuid
import hashlib
from .config import Config


class DocumentProcessor:

    @staticmethod
    def read_first_lines(file_path, n_lines=100):
        with open(file_path, "r", encoding="utf-8") as file:
            return [
                line.strip()
                for line, _ in zip(file, range(n_lines))
            ]

    @staticmethod
    def get_file_hash(file_path):
        """Calcola l'hash MD5 del contenuto del file."""
        hash_md5 = hashlib.md5()

        with open(file_path, "rb") as file:
            for chunk in iter(lambda: file.read(4096), b""):
                hash_md5.update(chunk)

        return hash_md5.hexdigest()

    @staticmethod
    def get_document_metadata(file_path):
        """Recupera i metadati del documento."""
        return {
            "hash": DocumentProcessor.get_file_hash(file_path),
            "last_modified": os.path.getmtime(file_path),
            "source": os.path.basename(file_path)
        }

    @staticmethod
    def split_text(text, chunk_size=800, overlap=100):
        """Divide il testo in blocchi con una sovrapposizione."""

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            if end < len(text):
                boundary = text.rfind(" ", start, end)

                if boundary > start:
                    end = boundary

            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end >= len(text):
                break

            next_start = max(start + 1, end - overlap)

            next_space = text.find(" ", next_start)

            if next_space != -1:
                next_start = next_space + 1

            start = next_start

        return chunks    
    
    @staticmethod
    def process_single_document(file_path):
        """Elabora un singolo documento dividendolo in blocchi."""
        documents = []
        metadatas = []
        ids = []

        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
            chunks = DocumentProcessor.split_text(text)
            file_metadata = DocumentProcessor.get_document_metadata(file_path)

            for chunk in chunks:
                if chunk.strip():
                    documents.append(chunk)
                    metadatas.append(file_metadata)
                    ids.append(str(uuid.uuid4()))

        return documents, metadatas, ids

    @staticmethod
    def process_documents(db, force=False):
        """Sincronizza i documenti con il database."""

        current_files = {
            filename: DocumentProcessor.get_document_metadata(
                os.path.join(Config.DOCUMENTS_DIR, filename)
            )
            for filename in os.listdir(Config.DOCUMENTS_DIR)
            if filename.endswith(".txt")
        }

        existing_files = db.get_tracked_files()

        # AVANZAMENTO 5 - REINDICIZZAZIONE FORZATA

        if force:
            for filename in existing_files:
                db.remove_document_by_source(filename)

            files_to_add = set(current_files.keys())
            files_to_update = set()
            files_to_remove = set()

        else:
            files_to_add = set(current_files.keys()) - set(existing_files.keys())

            files_to_remove = set(existing_files.keys()) - set(current_files.keys())

            files_to_update = {
                filename
                for filename in set(current_files.keys()) & set(existing_files.keys())
                if current_files[filename]["hash"] != existing_files[filename]["hash"]
            }

        for action, files in [
            ("add", files_to_add),
            ("update", files_to_update)
        ]:
            for filename in files:
                file_path = os.path.join(Config.DOCUMENTS_DIR, filename)

                documents, metadatas, ids = (
                    DocumentProcessor.process_single_document(file_path)
                )

                if action == "update":
                    db.remove_document_by_source(filename)

                if documents:
                    db.add_documents(documents, metadatas, ids)

        for filename in files_to_remove:
            db.remove_document_by_source(filename)

        return (
            len(files_to_add),
            len(files_to_update),
            len(files_to_remove)
        )