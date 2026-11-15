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


db = Database()

added, updated, removed = DocumentProcessor.process_documents(db)

print("Sincronizzazione documenti completata:")
print(f"Nuovi documenti: {added}")
print(f"Documenti aggiornati: {updated}")
print(f"Documenti rimossi: {removed}")

def cv_path(filename):
    return os.path.join(Config.DOCUMENTS_DIR, filename)

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

    await cl.Message(
        content="Benvenuto nell'HR Assistant! Seleziona un'azione:",
        actions=[stats_action, reindex_action]
    ).send()

@cl.on_message
async def handle_message(message: cl.Message):

    user_question = message.content

    # AVANZAMENTO 6.2
    messages = cl.user_session.get("messages", [])
    active_file = cl.user_session.get("last_cv_file")

    if active_file:
        active_cv_summary = (
            f"File: {active_file}\n"
            + "\n".join(
                DocumentProcessor.read_first_lines(cv_path(active_file), 8)
            )
        )
        intent = LLMHelper.classify_intent(user_question, active_cv_summary)
    else:
        intent = "search_cv"

    print(f"Intento: {intent} | CV attivo: {active_file}")


    if intent == "search_cv":

        results = db.query(user_question)

        if not results["documents"] or not results["documents"][0]:
            await cl.Message(
                content="Non ho trovato informazioni pertinenti nei CV."
            ).send()
            return

        # AVANZAMENTO 4 - RAGGRUPPAMENTO DEI FRAMMENTI PER CV
# 
#         best_filename = results["metadatas"][0][0]["source"]
# 
#         candidates = {}
# 
#         for document, metadata in zip(
#             results["documents"][0],
#             results["metadatas"][0]
#         ):
# 
#             filename = metadata["source"]
# 
#             if filename != best_filename:
#                 continue
#             if filename not in candidates:
#                 candidates[filename] = {
#                     "info": DocumentProcessor.read_first_lines(
#                         os.path.join(Config.DOCUMENTS_DIR, filename), 10
#                     ),
#                     "documents": []
#                 }
# 
#             candidates[filename]["documents"].append(document)
# 
#         context_parts = []
# 
#         for filename, candidate in candidates.items():
#             context_parts.append(f"""
#                 FILE CV: {filename}
# 
#                 INFORMAZIONI DEL CANDIDATO:
#                 {chr(10).join(candidate["info"])}
# 
#                 FRAMMENTI PIÙ PERTINENTI:
#                 {" ".join(candidate["documents"])}
#             """)
# 
#         context = "\n\n".join(context_parts)
# 
#         cl.user_session.set("last_cv_context", context)
#         cl.user_session.set(
#             "last_cv_header",
#             ", ".join(candidates.keys())
#         )

        filename = results["metadatas"][0][0]["source"]

        context_lines = DocumentProcessor.read_first_lines(
            cv_path(filename), 20
        )

        context = (
            f" **Nome file**: {filename}\n"
            f" **Estratto dal CV:**\n"
            f"```{results['documents'][0][0]}```"
        )

        prompt = LLMHelper.create_prompt(
            context,
            user_question,
            context_lines
        )


    # AVANZAMENTO 6.2
    elif intent == "info_cv":

        filename = active_file

        full_cv = "\n".join(
            DocumentProcessor.read_first_lines(cv_path(filename), 2000)
        )

        prompt = LLMHelper.create_info_prompt(
            f"File: {filename}\n{full_cv}",
            user_question
        )

    else:
        await cl.Message(
            content=(
                "Non ho capito la richiesta. "
                "Puoi chiedermi di cercare un candidato "
                "oppure di approfondire un CV già individuato."
            )
        ).send()
        return

    call_messages = messages + [{"role": "user", "content": prompt}]

    response_message = cl.Message(content="")
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
            "content": f"{user_question}\n(CV di riferimento: {filename})"
        })
        messages.append({
            "role": "assistant",
            "content": response_message.content
        })

        cl.user_session.set("messages", messages)

        cl.user_session.set("last_cv_file", filename)

    except Exception as e:
        traceback.print_exc(limit=-15, chain=False)
        print(f"ERRORE COMPLETO: {repr(e)}")

        error_message = f"An error occurred: {str(e)}"
        await cl.Message(content=error_message).send()

@cl.action_callback("db_stats")
async def show_db_stats(action: cl.Action):

    stats = LLMHelper.get_db_stats(db)

    await cl.Message(
        content=f"**Statistiche Database**\n\n{stats}"
    ).send()

@cl.action_callback("db_reindex")
async def reindex_db(action: cl.Action):

    await cl.Message(
        content="Reindicizzazione del database in corso..."
    ).send()

    added, updated, removed = DocumentProcessor.process_documents(
        db,
        force=True
    )

    await cl.Message(
        content=(
            "**Reindicizzazione completata!**\n\n"
            f"CV elaborati: {added + updated}\n"
            f"CV rimossi: {removed}"
        )
    ).send()