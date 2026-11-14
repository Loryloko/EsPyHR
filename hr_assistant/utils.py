
# AVANZAMENTO 2 - UTILITÀ E GESTIONE AI

# from openai import OpenAI
# from .config import Config
# 
# 
# client = OpenAI(
#     base_url=Config.AI_API_URL,
#     api_key=Config.AI_API_KEY
# )
# 
# 
# class LLMHelper:
# 
#     @staticmethod
#     def chat(messages):
#         return client.chat.completions.create(
#             model=Config.LLM_MODEL,
#             messages=messages,
#             stream=True
#         )
# 
#     @staticmethod
#     async def get_candidate_name(context):
#         response = client.chat.completions.create(
#             model=Config.LLM_MODEL,
#             messages=[
#                 {
#                     "role": "user",
#                     "content": f"""
#                     Dato il seguente contesto individua il nome e
#                     cognome del candidato e ritorna solo il nome
#                     e cognome del candidato.
# 
#                     Contesto: {context}
#                     """
#                 }
#             ]
#         )
# 
#         return response.choices[0].message.content
# 
#     @staticmethod
#     def create_prompt(context, question, candidate_name):
#         return f"""
#             Dato il seguente contesto:
# 
#             [[[
#             {context}
#             ]]]
# 
#             Rispondi alla domanda dell'utente:
#             [[[ {question} ]]]
# 
#             Spiega che nel file individuato c'è il profilo
#             più adatto.
# 
#             Assicurati di nominare il file e il candidato:
#             [[[ {candidate_name} ]]]
# 
#             Argomenta la scelta utilizzando il contenuto
#             del testo individuato nel contesto.
# 
#             Se non trovi corrispondenza in nessun CV,
#             non inventare.
#         """
 
# AVANZAMENTO 3 - UTILITÀ E GESTIONE AI OTTIMIZZATA

# from openai import OpenAI
# from .config import Config
# 
# client = OpenAI(
#     base_url=Config.AI_API_URL,
#     api_key=Config.AI_API_KEY
# )
# 
# 
# class LLMHelper:
# 
#     @staticmethod
#     def chat(messages):
#         return client.chat.completions.create(
#             model=Config.LLM_MODEL,
#             messages=messages,
#             stream=True
#         )
# 
#     @staticmethod
#     def create_prompt(context, question):
#         return f"""
#             Sei un assistente specializzato nel settore HR.
# 
#             Analizza attentamente il seguente contesto:
# 
#             [[[
#             {context}
#             ]]]
# 
#             Rispondi alla domanda dell'utente:
#             [[[ {question} ]]]
# 
#             Individua il candidato più adatto alla richiesta.
# 
#             Nella risposta:
#             - Indica nome e cognome del candidato, se presenti.
#             - Specifica il nome del file CV da cui hai ricavato
#               le informazioni.
#             - Argomenta la scelta utilizzando le informazioni
#               presenti nel contesto.
#             - Mantieni un tono professionale, sintetico e chiaro.
# 
#             Utilizza esclusivamente le informazioni fornite.
#             Se non trovi una corrispondenza nei CV, dichiaralo
#             senza inventare informazioni.
#         """

# AVANZAMENTO 4 - ESTRAZIONE INFORMAZIONI CANDIDATO

#from openai import OpenAI
#from .config import Config
#
#client = OpenAI(
#    api_key=Config.OPENAI_KEY
#)
#
#class LLMHelper:
#
#    @staticmethod
#    def chat(messages):
#        return client.chat.completions.create(
#            model=Config.LLM_MODEL,
#            messages=messages,
#            stream=True
#        )
#
#    @staticmethod
#    def create_prompt(context, question):
#        return f"""
#            Sei un assistente specializzato nel settore HR.
#
#            Analizza attentamente il seguente contesto:
#
#            [[[
#            {context}
#            ]]]
#
#            Rispondi alla domanda dell'utente:
#            [[[ {question} ]]]
#
#            Individua il candidato più adatto alla richiesta.
#
#            REGOLE PER L'ESTRAZIONE DEI DATI:
#            - Cerca nome e cognome nelle informazioni anagrafiche.
#            - Cerca il numero di telefono nelle informazioni di contatto.
#            - Cerca l'indirizzo email nelle informazioni di contatto.
#            - Se telefono o email sono presenti nel contesto, riportali
#              obbligatoriamente e senza modificarli.
#            - Non dichiarare un dato mancante se è effettivamente
#              presente nel contesto.
#            - Non confondere l'assenza di un dato nei frammenti
#              pertinenti con la sua assenza nelle informazioni
#              anagrafiche del candidato.
#
#            Nella risposta:
#            - Indica nome e cognome del candidato.
#            - Indica il numero di telefono, se disponibile.
#            - Indica l'indirizzo email, se disponibile.
#            - Specifica il nome del file CV.
#            - Argomenta la scelta utilizzando le informazioni
#              presenti nel contesto.
#            - Mantieni un tono professionale, sintetico e chiaro.
#
#            Utilizza esclusivamente le informazioni fornite.
#            Non inventare dati mancanti.
#            Se non trovi una corrispondenza nei CV, dichiaralo.
#            """
#
#    @staticmethod
#    def get_db_stats(db):
#        """Recupera le statistiche del database."""
#
#        stats = db.get_stats()
#
#        return (
#            f"CV archiviati: {stats['total_files']}\n"
#            f"Frammenti totali: {stats['total_chunks']}"
#        )

# AVANZAMENTO 4

from openai import OpenAI
from .config import Config

client = OpenAI(
    api_key=Config.OPENAI_KEY
)


class LLMHelper:

    @staticmethod
    def chat(messages):
        return client.chat.completions.create(
            model=Config.LLM_MODEL,
            messages=messages,
            stream=True
        )

    @staticmethod
    def create_prompt(context, question):
        return f"""
            Sei un assistente specializzato nel settore HR.

            Analizza attentamente il seguente contesto:

            [[[
            {context}
            ]]]

            Rispondi alla domanda dell'utente:
            [[[ {question} ]]]

            Individua il candidato più adatto alla richiesta.

            REGOLE PER L'ESTRAZIONE DEI DATI:
            - Cerca nome e cognome nelle informazioni anagrafiche.
            - Cerca il numero di telefono nelle informazioni di contatto.
            - Cerca l'indirizzo email nelle informazioni di contatto.
            - Se telefono o email sono presenti nel contesto, riportali
              obbligatoriamente e senza modificarli.
            - Non dichiarare un dato mancante se è effettivamente
              presente nel contesto.
            - Considera tutte le informazioni disponibili nel contesto
              relativo al candidato, anche se distribuite in frammenti diversi.
            - Non dichiarare un dato assente dal CV se potrebbe trovarsi
              in un altro frammento dello stesso documento.

            - Distingui le competenze esplicitamente dichiarate
              dalle competenze che potrebbero essere trasferibili.
            - Non considerare strumenti di sicurezza informatica,
              monitoraggio o networking come database.
            - Per la gestione dei database, cerca tecnologie
              esplicitamente indicate, come MySQL, PostgreSQL,
              MongoDB, Oracle Database o SQL Server.
            - Se una competenza richiesta non è esplicitamente
              presente nel CV, dichiarala come non verificata.
            - Non attribuire competenze sulla base di lauree,
              certificazioni o esperienze lavorative generiche.
            - Considera una competenza presente solo se è
              esplicitamente indicata nel CV del candidato.
            - Non dedurre competenze dalla professione,
              dall'esperienza lavorativa o dalla formazione.
            - Non inventare tecnologie, strumenti o certificazioni.
            - Se una tecnologia richiesta non compare nel CV,
              dichiara esplicitamente che non è documentata.
            - Distingui tra candidato parzialmente compatibile
              e candidato pienamente compatibile.
            - Non selezionare un candidato come idoneo se manca
              anche uno solo dei requisiti obbligatori richiesti.
            - Non considerare tecnologie simili, alternative o equivalenti
              come sostitutive del requisito richiesto.
            - Se l'utente richiede MySQL, considera soddisfatto il requisito
              esclusivamente quando MySQL è esplicitamente indicato nel CV.
            - PostgreSQL non soddisfa automaticamente un requisito MySQL
              e viceversa.
            - Distingui sempre tra candidato più vicino ai requisiti e
              candidato pienamente compatibile.
            - Se nessun candidato soddisfa tutti i requisiti, dichiaralo
              chiaramente senza selezionare un candidato come idoneo.

            Nella risposta:
            - Indica nome e cognome del candidato.
            - Indica il numero di telefono, se disponibile.
            - Indica l'indirizzo email, se disponibile.
            - Specifica il nome del file CV.
            - Argomenta la scelta utilizzando le informazioni
              presenti nel contesto.
            - Mantieni un tono professionale, sintetico e chiaro.

            Utilizza esclusivamente le informazioni fornite.
            Non inventare dati mancanti.
            Se non trovi una corrispondenza nei CV, dichiaralo.
            """

    @staticmethod
    def get_db_stats(db):
        """Recupera le statistiche del database."""

        stats = db.get_stats()

        return (
            f"CV archiviati: {stats['total_files']}\n"
            f"Frammenti totali: {stats['total_chunks']}"
        )
