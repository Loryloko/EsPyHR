# AVANZAMENTO 2 - ELABORAZIONE DOCUMENTI 

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


# AVANZAMENTO 3 - SINCRONIZZAZIONE DOCUMENTI

import os
import uuid
import hashlib
from .config import Config

# AVANZAMENTO 7

from typing import Tuple, List, Dict, Any
from markitdown import MarkItDown
from zipfile import ZipFile
import tempfile
import mimetypes

# AVANZAMENTO 5

from .semantic_chunking import SemanticChunking

class DocumentProcessor:

# AVANZAMENTO 7

    SUPPORTED_EXTENSIONS = {
        # Document formats
        ".txt": "text",
        ".pdf": "document",
        ".doc": "document",
        ".docx": "document",
        ".ppt": "presentation",
        ".pptx": "presentation",
        ".xls": "spreadsheet",
        ".xlsx": "spreadsheet",
        # Web formats
        ".html": "web",
        ".htm": "web",
        # Data formats
        ".csv": "data",
        ".json": "data",
        ".xml": "data",
        # Archive formats
        ".zip": "archive",
    }

    def __init__(self):
        self.md_converter = MarkItDown()


    @staticmethod
    def read_first_lines(file_path, n_lines=100):
# AVANZAMENTO 7
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return [
                    line.strip()
                    for line, _ in zip(file, range(n_lines))
                ]
            
        except UnicodeDecodeError:
            return []        

    @staticmethod
    def get_file_hash(file_path):
        """Calcola l'hash MD5 del contenuto del file."""
        hash_md5 = hashlib.md5()

        with open(file_path, "rb") as file:
            for chunk in iter(lambda: file.read(4096), b""):
                hash_md5.update(chunk)

        return hash_md5.hexdigest()

# AVANZAMENTO 7
    def get_document_metadata(self, file_path):
        """Recupera i metadati del documento."""

        extension = os.path.splitext(file_path)[1].lower()
        file_type = self.SUPPORTED_EXTENSIONS.get(extension, "unknown")

        metadata = {
            "hash": self.get_file_hash(file_path),
            "last_modified": os.path.getmtime(file_path),
            "source": os.path.basename(file_path),
            "file_type": file_type,
            "mime_type": mimetypes.guess_type(file_path)[0] or "application/octet-stream",
            "extension": extension,
        }

        return metadata
#    @staticmethod
#    def get_document_metadata(file_path):
#        """Recupera i metadati del documento."""
#        return {
#            "hash": DocumentProcessor.get_file_hash(file_path),
#            "last_modified": os.path.getmtime(file_path),
#            "source": os.path.basename(file_path)
#        }
# AVANZAMENTO 7
    def _process_zip_file(self, zip_path):
        """Estrae e converte i documenti supportati contenuti in un archivio ZIP."""

        results = []

        with tempfile.TemporaryDirectory() as temp_dir:
            with ZipFile(zip_path, "r") as zip_file:

                for index, item in enumerate(zip_file.infolist()):

                    if item.is_dir():
                        continue

                    extension = os.path.splitext(item.filename)[1].lower()

                    if extension not in self.SUPPORTED_EXTENSIONS:
                        continue

                    if extension == ".zip":
                        continue

                    filename = os.path.basename(item.filename)
                    temp_path = os.path.join(temp_dir, f"{index}_{filename}")

                    with zip_file.open(item) as source:
                        with open(temp_path, "wb") as destination:
                            destination.write(source.read())

                    content = self._convert_to_markdown(temp_path)

                    if content:
                        results.append((filename, content))

            return results

    def _convert_to_markdown(self, file_path):
        """Converte un documento in formato Markdown."""
        extension = os.path.splitext(file_path)[1].lower()

        if extension in [".md", ".py"]:
            try:
                with open(file_path, "r", encoding="utf-8-sig") as file:
                    return file.read()

            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                return ""
            
        try:
            result = self.md_converter.convert(file_path)
            print("Converted to Markdown:", result)
            return result.text_content
            
        except Exception as e:
            print(f"Error converting {file_path} to Markdown: {e}")
            return ""
        
# AVANZAMENTO 5

#    @staticmethod
    def process_single_document(
            self,file_path: str
        ) -> tuple[list[str], list[Dict], list[str]]:
        """Elabora un documento dividendolo in blocchi."""

        documents = []
        metadatas = []
        ids = []

#        with open(file_path, "r", encoding="utf-8") as file:
#            text = file.read()

# AVANZAMENTO 7
        extension = os.path.splitext(file_path)[1].lower()
        file_type = self.SUPPORTED_EXTENSIONS.get(extension)

        if not file_type:
            return [], [], []

        content = ""

        if file_type == "archive":
            content = self._process_zip_file(file_path)
        else:
            filename = os.path.basename(file_path)
            content = self._convert_to_markdown(file_path)
            content = [(filename, content)]
        
        file_metadata = self.get_document_metadata(file_path)

        for filename, content in content:
            if not content or not content.strip():
                continue

            try:
                chunking = SemanticChunking(
                    breakpoint_percentile=70,
                    buffer_size=1
                )

                chunks = chunking.chunk_text(content)

                for chunk in chunks:
                    if not chunk or not chunk.strip():
                        continue

                    documents.append(chunk)

                    metadata = file_metadata.copy()

                    if file_type == "archive":
                        metadata["internal_source"] = filename

                    metadatas.append(metadata)
                    ids.append(str(uuid.uuid4()))

                print(
                    f"Documento elaborato: {filename} | "
                    f"Frammenti: {len(chunks)}"
                )

            except Exception as e:
                print(f"Errore durante l'elaborazione del documento {filename}: {e}")
                raise

        return documents, metadatas, ids
        
#    @staticmethod
    def process_documents(self, db, force=False):
        """Sincronizza i documenti con il database."""
# AVANZAMENTO 7
        processor = DocumentProcessor()

        current_files = {
            filename: processor.get_document_metadata(
                os.path.join(Config.DOCUMENTS_DIR, filename)
            )
            for filename in os.listdir(Config.DOCUMENTS_DIR)
#            if filename.endswith(".txt")
# AVANZAMENTO 7
            if os.path.splitext(filename)[1].lower() in DocumentProcessor.SUPPORTED_EXTENSIONS
        }

        existing_files = db.get_tracked_files()

        # AVANZAMENTO 4 - REINDICIZZAZIONE FORZATA

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
# AVANZAMENTO 7
                    processor.process_single_document(file_path)
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