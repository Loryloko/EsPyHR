# AVANZAMENTO 0 - CHAT CHAINLIT BASE

# import chainlit as cl
#
# @cl.on_message
# async def handle_message(message: cl.Message):
#     response = f"Ciao, mi hai scritto: {message.content}!"
#     await cl.Message(response).send()

# AVANZAMENTO 1 - HR ASSISTANT

# import chainlit as cl
# import ollama
# import chromadb
# import os
# import uuid
# 
# from dotenv import load_dotenv
# from chromadb.utils import embedding_functions
# 
# load_dotenv()
# 
# openai_key = os.getenv("OPENAI_API_KEY")
# 
# if not openai_key:
#     raise ValueError("OPENAI_API_KEY non trovata nel file .env")


# FASE 1 - LETTURA FILE E CHUNKING

# documents_dir = "resumes"
# 
# documents = []
# metadatas = []
# ids = []
# 
# for filename in os.listdir(documents_dir):
#     if filename.endswith(".txt"):
#         with open(os.path.join(documents_dir, filename), "r", encoding="utf-8") as file:
#             content = file.read()
# 
#             candidate_name = content.splitlines()[0].replace("###", "").strip()
# 
#             chunks = content.replace("\n", ".").split("### ")
# 
#             for chunk in chunks:
#                 if chunk.strip():
#                     documents.append(chunk)
# 
#                     metadatas.append({
#                         "source": filename,
#                         "candidate": candidate_name
#                     })
# 
#                     guid = str(uuid.uuid4())
#                     ids.append(guid)

# FASE 2 - EMBEDDINGS E DATABASE VETTORIALE

# openai_ef = embedding_functions.OpenAIEmbeddingFunction(
#     api_key=openai_key,
#     model_name="text-embedding-3-small"
# )
# 
# chroma_client = chromadb.Client()
# 
# try:
#     chroma_client.delete_collection(name="CVs")
# except Exception:
#     pass
# 
# collection = chroma_client.create_collection(
#     name="CVs",
#     embedding_function=openai_ef
#     )
# 
# collection.add(
#     documents=documents,
#     metadatas=metadatas,
#     ids=ids
# )

# FASE 3 - GESTIONE DELLA CONVERSAZIONE CON CHAINLIT E OLLAMA

# @cl.on_chat_start
# async def on_chat_start():
#     cl.user_session.set(
#         "messages",
#         [
#             {
#                 "role": "system",
#                 "content": "Sei un assistente specializzato nel mondo HR. Rispondi alle domande basandoti sui CV forniti."
#             }
#         ]
#     )
# 
# 
# @cl.on_message
# async def on_message(message: cl.Message):
#     user_question = message.content
# 
#     results = collection.query(
#         query_texts=[user_question],
#         n_results=3
#     )
# 
#     documents_found = results["documents"][0]
#     sources_found = results["metadatas"][0]
# 
#     context = ""
# 
#     for document, metadata in zip(documents_found, sources_found):
#         context += (
#             f"\nCandidato: {metadata['candidate']}"
#             f"\nFonte: {metadata['source']}"
#             f"\nInformazioni: {document}\n"
#         )
#     messages = cl.user_session.get("messages")
# 
#     messages.append({
#         "role": "user",
#         "content": f"""
#         Rispondi alla domanda utilizzando esclusivamente i CV forniti.
# 
#         Indica chiaramente il nome del candidato, se presente.
#         Specifica il file CV da cui hai ricavato le informazioni.
#         Se non trovi il nome, non inventarlo.
# 
#         CV disponibili:
#         {context}
# 
#         Domanda: {user_question}
#         """
#     })
# 
#     response = ollama.chat(
#         model="llama3.2",
#         messages=messages,
#         stream=True
#     )
# 
#     response_message = cl.Message(content="")
# 
#     for chunk in response:
#         token = chunk["message"]["content"]
#         await response_message.stream_token(token)
# 
#     await response_message.send()
# 
#     messages.append({
#         "role": "assistant",
#         "content": response_message.content
#     })

# AVANZAMENTO 2 - HR ASSISTANT MODULARE

# import os
# import chainlit as cl
# 
# from .document_processor import DocumentProcessor
# from .database import Database
# from .config import Config
# from .utils import LLMHelper
# 
# 
# documents, metadatas, ids = DocumentProcessor.process_documents()
# 
# db = Database()
# db.add_documents(documents, metadatas, ids)
# 
# @cl.on_chat_start
# def start():
#     cl.user_session.set(
#         "messages",
#         [
#             {
#                 "role": "system",
#                 "content": """
#                     Sei un assistente specializzato nel mondo HR,
#                     rispondi in modo professionale, sintetico e pragmatico.
#                     Il tuo ruolo è individuare il candidato ideale
#                     rispetto alle richieste dell'utente.
#                 """,
#             }
#         ],
#     )
# 
# 
# @cl.on_message
# async def handle_message(message: cl.Message):
# 
#     user_question = message.content
# 
#     results = db.query(user_question)
# 
#     filename = results["metadatas"][0][0]["source"]
# 
#     context_lines = DocumentProcessor.read_first_lines(
#         os.path.join(Config.DOCUMENTS_DIR, filename), 10
#     )
# 
#     context = (
#         f"CONTESTO: nome file {filename} "
#         f"ecco il paragrafo più significativo: "
#         f"{results['documents'][0][0]}"
#     )
# 
#     candidate_name = await LLMHelper.get_candidate_name(context_lines)
# 
#     prompt = LLMHelper.create_prompt(
#         context,
#         user_question,
#         candidate_name
#     )
# 
#     messages = cl.user_session.get("messages", [])
#     messages.append({"role": "user", "content": prompt})
# 
#     response_message = cl.Message(content="")
#     await response_message.send()
# 
#     try:
#         stream = LLMHelper.chat(messages)
# 
#         for chunk in stream:
#             token = chunk.choices[0].delta.content
# 
#             if token:
#                 await response_message.stream_token(token)
# 
#         messages.append({
#             "role": "assistant",
#             "content": response_message.content
#         })
# 
#         await response_message.update()
# 
#     except Exception as e:
#         error_message = f"An error occurred: {str(e)}"
#         await cl.Message(content=error_message).send()
#         print(error_message)
# 
#     cl.user_session.set("messages", messages)
# 

# AVANZAMENTO 3 - HR ASSISTANT CON SINCRONIZZAZIONE DOCUMENTI

# import chainlit as cl
# 
# from .document_processor import DocumentProcessor
# from .database import Database
# from .config import Config
# from .utils import LLMHelper
# 
# db = Database()
# 
# added, updated, removed = DocumentProcessor.process_documents(db)
# 
# print("Sincronizzazione documenti completata:")
# print(f"Nuovi documenti: {added}")
# print(f"Documenti aggiornati: {updated}")
# print(f"Documenti rimossi: {removed}")
# 
# @cl.on_chat_start
# def start():
#     cl.user_session.set(
#         "messages",
#         [
#             {
#                 "role": "system",
#                 "content": """
#                     Sei un assistente specializzato nel mondo HR,
#                     rispondi in modo professionale, sintetico e pragmatico.
#                     Il tuo ruolo è individuare il candidato ideale
#                     rispetto alle richieste dell'utente.
#                 """,
#             }
#         ],
#     )
# 
# 
# @cl.on_message
# async def handle_message(message: cl.Message):
# 
#     user_question = message.content
# 
#     results = db.query(user_question)
# 
#     filename = results["metadatas"][0][0]["source"]
# 
#     context = (
#         f"CONTESTO: nome file {filename} "
#         f"ecco il paragrafo più significativo: "
#         f"{results['documents'][0][0]}"
#     )
# 
#     prompt = LLMHelper.create_prompt(
#         context,
#         user_question
#     )
# 
#     messages = cl.user_session.get("messages", [])
#     messages.append({"role": "user", "content": prompt})
# 
#     response_message = cl.Message(content="")
#     await response_message.send()
# 
#     try:
#         print("Invio richiesta a Ollama...")
# 
#         stream = LLMHelper.chat(messages)
# 
#         print("Connessione a Ollama riuscita.")
# 
#         for chunk in stream:
#             token = chunk.choices[0].delta.content
# 
#             if token:
#                 await response_message.stream_token(token)
# 
#         messages.append({
#             "role": "assistant",
#             "content": response_message.content
#         })
# 
#         await response_message.update()
# 
#     except Exception as e:
#         print(f"ERRORE COMPLETO: {repr(e)}")
# 
#         error_message = f"An error occurred: {str(e)}"
#         await cl.Message(content=error_message).send()
# 
#     cl.user_session.set("messages", messages)

# AVANZAMENTO 4 - HR ASSISTANT CON ESTRAZIONE CONTATTI

import os
import traceback
import chainlit as cl

from .document_processor import DocumentProcessor
from .database import Database
from .config import Config
from .utils import LLMHelper

# AVANZAMENTO 8
import shutil

db = Database()

dp = DocumentProcessor()
added, updated, removed = dp.process_documents(db)

print("Sincronizzazione documenti completata:")
print(f"Nuovi documenti: {added}")
print(f"Documenti aggiornati: {updated}")
print(f"Documenti rimossi: {removed}")

def cv_path(filename):
    return os.path.join(Config.DOCUMENTS_DIR, filename)

def find_requested_file(question):
    """Individua se l'utente ha indicato un documento specifico."""

    available_files = db.get_tracked_files()

    question_lower = question.casefold()

    for filename in available_files:
        if filename.casefold() in question_lower:
            return filename

    return None

@cl.on_chat_start
async def start():
    cl.user_session.set(
        "messages",
        [
            {
                "role": "system",
                "content": """
                    Sei un assistente specializzato nel mondo HR,
                    rispondi in modo professionale, sintetico e pragmatico.
                    Il tuo ruolo è individuare il candidato ideale
                    rispetto alle richieste dell'utente.
                """,
            }
        ],
    )

    # AVANZAMENTO 6.2
    cl.user_session.set("last_cv_file", None)

    stats_action = cl.Action(
        name="db_stats",
        label="Statistiche Database",
        payload={}
    )

    reindex_action = cl.Action(
        name="db_reindex",
        label="Reindex Database",
        payload={}
    )

    remove_action = cl.Action(
        name="db_remove",
        label="Svuota completamente il Database",
        payload={}
    )

    await cl.Message(
        author="system_assistant",
        content="Benvenuto nell'HR Assistant! Seleziona un'azione:",
        actions=[stats_action, reindex_action, remove_action]
    ).send()

async def _process_and_index_file(file_path: str, file_name: str) -> str:
    """Elabora e indicizza il documento, restituendo un messaggio di esito."""
    documents, metadatas, ids = dp.process_single_document(file_path)

    if documents:
        # se il file esisteva già, elimina i vecchi frammenti (niente duplicati)
        db.remove_document_by_source(file_name)
        db.add_documents(documents, metadatas, ids)
        return f"File '{file_name}' caricato e indicizzato con successo."

    return f"Errore nel processare il file '{file_name}'."


async def _file_upload(file) -> str:
    file_name = os.path.basename(file.name)
    src_file_path = file.path
    dst_file_path = os.path.join(Config.DOCUMENTS_DIR, file_name)

    os.makedirs(Config.DOCUMENTS_DIR, exist_ok=True)
    shutil.move(src_file_path, dst_file_path)

    return await _process_and_index_file(dst_file_path, file_name)


@cl.action_callback("db_remove")
async def remove_db(action: cl.Action):

    db.delete_collection()
    cl.user_session.set("last_cv_file", None)

    await cl.Message(
        author="system_assistant",
        content=(
            
            "Il database è stato completamente svuotato. "
            "Per ricostruirlo premi **Reindex Database**."
        )
    ).send()

@cl.on_message
async def handle_message(message: cl.Message):

    if message.elements:
        await cl.Message(author="system_assistant", content="Caricamento e indicizzazione documenti").send()

        files = [
            file
            for file in message.elements
            if file.name.lower().endswith(tuple(DocumentProcessor.SUPPORTED_EXTENSIONS))
        ]

        if files:
            upload_results = [await _file_upload(file) for file in files]
        else:
            upload_results = ["Nessun file caricato"]

        await cl.Message(author="system_assistant", content="\n".join(upload_results)).send()
        await cl.Message(author="system_assistant", content=f"Caricati {len(files)} file").send()

        if not message.content.strip():
            return

    user_question = message.content

    # AVANZAMENTO 6.2
    messages = cl.user_session.get("messages", [])
    active_file = cl.user_session.get("last_cv_file")

    requested_file = find_requested_file(user_question)

    if requested_file:
        intent = "search_cv"
        filename = requested_file
    
    else:
        intent = LLMHelper.classify_intent(user_question, active_file)
        print(f"Intento: {intent} | CV attivo: {active_file} | " f"Documento richiesto: {requested_file}")
    
    if intent == "info_cv" and not active_file:
        intent = "search_cv"

    if intent == "search_multiple":
        
        candidate_files = db.get_tracked_files()
        candidates_context = []
    
        for candidate_file in candidate_files:
        
            results = db.get_document_chunks(candidate_file)
    
            if results["documents"]:
            
                full_document = "\n\n".join(results["documents"])
    
                candidates_context.append(
                    f"FILE: {candidate_file}\n"
                    f"CONTENUTO:\n{full_document}"
                )
    
        if not candidates_context:
            await cl.Message(
                author="system_assistant",
                content="Non ho trovato documenti da analizzare."
            ).send()
            return
    
        context = "\n\n".join(candidates_context)
    
        prompt = f"""
            Sei un assistente specializzato nella selezione del personale.
    
            Devi analizzare tutti i documenti forniti e rispondere
            alla richiesta dell'utente.
    
            DOCUMENTI DISPONIBILI:
            {context}
    
            RICHIESTA:
            {user_question}
    
            REGOLE:
            - Analizza tutti i documenti, non soltanto il primo.
            - Individua tutti i candidati che soddisfano i requisiti.
            - Per ciascun candidato indica nome, cognome, anni di
              esperienza e ruolo, quando disponibili e pertinenti.
            - Specifica sempre il nome del file di provenienza.
            - Non includere candidati che non soddisfano i requisiti.
            - Non inventare informazioni mancanti.
            - Se un dato non è presente, dichiaralo.
            - Se nessun candidato soddisfa i requisiti, dichiaralo.
            - Rispondi in italiano, in modo chiaro e ordinato.
        """

    elif intent == "search_cv":

        if requested_file:
            results = db.get_document_chunks(filename)
                        
            if not results["documents"]:
                await cl.Message(
                    author="system_assistant",
                    content=f"Non ho trovato informazioni pertinenti nel documento {filename}."
                ).send()
                return

            documents = results["documents"]

        else:

            results = db.query(user_question, n_results=8)
            
            for i, (metadata, distance) in enumerate(
                zip(results["metadatas"][0], results["distances"][0]), start=1
            ):
                print(
                    f"Risultato {i}: "
                    f"{metadata.get('source')} | "
                    f"Distanza: {distance:.4f}"
                )

            if not results["documents"] or not results["documents"][0]:
                await cl.Message(
                    author="system_assistant",
                    content=f"Non ho trovato informazioni pertinenti nel documento."
                ).send()
                return

            # AVANZAMENTO 7 - SELEZIONE DEL CV PIÙ PERTINENTE

            candidate_files = []
            candidates_context = []

            for document, metadata in zip(
                results["documents"][0],
                results["metadatas"][0]
            ):
                source = metadata.get("source")

                if source not in candidate_files:
                    candidate_files.append(source)

                candidates_context.append(
                    f"FILE: {source}\n"
                    f"CONTENUTO: {document}"
                )

            filename = LLMHelper.select_cv(
                user_question,
                "\n\n".join(candidates_context),
                candidate_files
            )

            if filename is None:
                await cl.Message(
                    author="system_assistant",
                    content=(
                        "Non ho trovato un candidato che soddisfi "
                        "i requisiti richiesti nei CV individuati."
                    )
                ).send()
                return

            full_results = db.get_document_chunks(filename)

            documents = full_results["documents"]
        full_cv = "\n\n".join(documents)

        context = (
            f" DOCUMENTO: {filename}\n\n"
            f" CONTENUTO COMPLETO:\n{full_cv}"
        )

        prompt = LLMHelper.create_prompt(
            context,
            user_question,
            ""
        )

    elif intent == "info_cv":

        filename = active_file

        results = db.get_document_chunks(filename)

        if not results["documents"]:
            await cl.Message(
                author="system_assistant",
                content=f"Non ho trovato informazioni sul documento {filename}."
            ).send()
            return

        full_cv = "\n\n".join(results["documents"])

        context = (
            f" DOCUMENTO: {filename}\n\n"
            f" CONTENUTO COMPLETO:\n{full_cv}"
        )

        prompt = LLMHelper.create_info_prompt(
            context,
            user_question
        )

    else:
        await cl.Message(
            author="system_assistant",
            content=(
                "Non ho capito la richiesta. "
                "Puoi chiedermi di cercare un candidato "
                "oppure di approfondire un CV già individuato."
            )
        ).send()
        return

    call_messages = messages + [{"role": "user", "content": prompt}]

    response_message = cl.Message(author="hr_assistant", content="")
    await response_message.send()

    try:
        stream = LLMHelper.chat(call_messages)

        for chunk in stream:
            token = chunk.choices[0].delta.content

            if token:
                await response_message.stream_token(token)

        await response_message.update()

        messages.append({
            "role": "user",
            "content": user_question
        })

        messages.append({
            "role": "assistant",
            "content": response_message.content
        })

        cl.user_session.set("messages", messages)

        if intent == "search_multiple":
            cl.user_session.set("last_cv_file", None)
        else:
            cl.user_session.set("last_cv_file", filename)

    except Exception as e:
        traceback.print_exc(limit=-15, chain=False)
        print(f"ERRORE COMPLETO: {repr(e)}")

        error_message = f"An error occurred: {str(e)}"
        await cl.Message(author="hr_assistant", content=error_message).send()

@cl.action_callback("db_stats")
async def show_db_stats(action: cl.Action):

    stats = LLMHelper.get_db_stats(db)

    await cl.Message(
        author="system_assistant",
        content=f"**Statistiche Database**\n\n{stats}"
    ).send()

@cl.action_callback("db_reindex")
async def reindex_db(action: cl.Action):

    await cl.Message(
        author="system_assistant",
        content="Reindicizzazione del database in corso..."
    ).send()

    added, updated, removed = dp.process_documents(db, force=True)

    await cl.Message(
        author="system_assistant",
        content=(
            "**Reindicizzazione completata!**\n\n"
            f"CV elaborati: {added + updated}\n"
            f"CV rimossi: {removed}"
        )
    ).send()