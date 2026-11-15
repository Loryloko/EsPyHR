
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

# AVANZAMENTO 6.2
    @staticmethod
    def classify_intent(user_question, active_cv=None):
        """
        Classifica la richiesta dell'utente.

        active_cv: descrizione (file + prime righe) del CV di cui si sta
        già parlando. Se è None non c'è nessun candidato in discussione.
        """
        if active_cv:
            state = f"""
          STATO DELLA CONVERSAZIONE:
          L'utente sta già parlando di questo candidato:
          [[[
          {active_cv}
          ]]]

          REGOLE CON UN CANDIDATO GIÀ IN DISCUSSIONE:
          - Nel dubbio scegli info_cv: è l'opzione predefinita.
          - Una domanda che usa pronomi o riferimenti al candidato
            (lui, lei, ha, sa, parla, questo candidato, quel CV...)
            oppure che chiede dettagli su esperienze, studi,
            competenze, lingue, certificazioni, contatti o età
            è info_cv, anche se non cita il nome.
          - Scegli search_cv SOLO se l'utente chiede esplicitamente
            un candidato diverso/nuovo (es. "cerca un altro",
            "trovami", "chi altro") oppure descrive nuovi requisiti
            per individuare un profilo (es. "chi ha esperienza in X?").

          ESEMPI:
          - "Dove ha lavorato?" -> info_cv
          - "Qual è la sua email?" -> info_cv
          - "Parla inglese?" -> info_cv
          - "Ha esperienza con Docker?" -> info_cv
          - "Chi ha esperienza con Docker?" -> search_cv
          - "Cerco un idraulico" -> search_cv
          - "Mostrami un altro candidato" -> search_cv
          """
        else:
            state = """
          STATO DELLA CONVERSAZIONE:
          Nessun candidato è ancora stato individuato.
          """


        intent_prompt = f"""
          Sei un assistente AI che gestisce richieste relative
          ai curriculum vitae.
          
          Devi classificare la richiesta dell'utente in una
          delle seguenti categorie:
          
          - search_cv: quando l'utente vuole trovare o individuare
            un candidato in base a competenze, esperienze,
            qualifiche o caratteristiche richieste.
          
          - info_cv: quando l'utente vuole ottenere informazioni
            specifiche su un candidato, ad esempio contatti,
            formazione, esperienze lavorative o competenze.
          
          IMPORTANTE:
          - Una richiesta relativa a nome, telefono o email
            di un candidato è classificata come info_cv.
          - Una richiesta che approfondisce un candidato già
            individuato è sempre info_cv.
          - Non classificare come search_cv una domanda solo
            perché contiene il nome di un candidato.
          - search_cv deve essere utilizzato quando l'obiettivo
            principale è individuare un candidato che soddisfi
            determinati requisiti.

          {state}

          Domanda dell'utente: "{user_question}"
          
          Rispondi esclusivamente con "search_cv" oppure "info_cv".
          Non aggiungere spiegazioni.
          """

        response = client.chat.completions.create(
            model=Config.LLM_MODEL,
            messages=[
                {"role": "user", "content": intent_prompt}
            ],
            temperature=0
        )

        answer = response.choices[0].message.content.strip().lower()

        if "info_cv" in answer:
            return "info_cv"
        if "search_cv" in answer:
            return "search_cv"
        return answer
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
#             REGOLE PER L'ESTRAZIONE DEI DATI:
#             - Cerca nome e cognome nelle informazioni anagrafiche.
#             - Cerca il numero di telefono nelle informazioni di contatto.
#             - Cerca l'indirizzo email nelle informazioni di contatto.
#             - Se telefono o email sono presenti nel contesto, riportali
#               obbligatoriamente e senza modificarli.
#             - Non dichiarare un dato mancante se è effettivamente
#               presente nel contesto.
#             - Considera tutte le informazioni disponibili nel contesto
#               relativo al candidato, anche se distribuite in frammenti diversi.
#             - Non dichiarare un dato assente dal CV se potrebbe trovarsi
#               in un altro frammento dello stesso documento.
# 
#             - Distingui le competenze esplicitamente dichiarate
#               dalle competenze che potrebbero essere trasferibili.
#             - Non considerare strumenti di sicurezza informatica,
#               monitoraggio o networking come database.
#             - Per la gestione dei database, cerca tecnologie
#               esplicitamente indicate, come MySQL, PostgreSQL,
#               MongoDB, Oracle Database o SQL Server.
#             - Se una competenza richiesta non è esplicitamente
#               presente nel CV, dichiarala come non verificata.
#             - Non attribuire competenze sulla base di lauree,
#               certificazioni o esperienze lavorative generiche.
#             - Considera una competenza presente solo se è
#               esplicitamente indicata nel CV del candidato.
#             - Non dedurre competenze dalla professione,
#               dall'esperienza lavorativa o dalla formazione.
#             - Non inventare tecnologie, strumenti o certificazioni.
#             - Se una tecnologia richiesta non compare nel CV,
#               dichiara esplicitamente che non è documentata.
#             - Distingui tra candidato parzialmente compatibile
#               e candidato pienamente compatibile.
#             - Non selezionare un candidato come idoneo se manca
#               anche uno solo dei requisiti obbligatori richiesti.
#             - Non considerare tecnologie simili, alternative o equivalenti
#               come sostitutive del requisito richiesto.
#             - Se l'utente richiede MySQL, considera soddisfatto il requisito
#               esclusivamente quando MySQL è esplicitamente indicato nel CV.
#             - PostgreSQL non soddisfa automaticamente un requisito MySQL
#               e viceversa.
#             - Distingui sempre tra candidato più vicino ai requisiti e
#               candidato pienamente compatibile.
#             - Se nessun candidato soddisfa tutti i requisiti, dichiaralo
#               chiaramente senza selezionare un candidato come idoneo.
# 
#             Nella risposta:
#             - Indica nome e cognome del candidato.
#             - Indica il numero di telefono, se disponibile.
#             - Indica l'indirizzo email, se disponibile.
#             - Specifica il nome del file CV.
#             - Argomenta la scelta utilizzando le informazioni
#               presenti nel contesto.
#             - Mantieni un tono professionale, sintetico e chiaro.
# 
#             Utilizza esclusivamente le informazioni fornite.
#             Non inventare dati mancanti.
#             Se non trovi una corrispondenza nei CV, dichiaralo.
#             """

# AVANZAMENTO 6.2
    @staticmethod
    def create_prompt(context, question, context_lines):
        return f"""
        Sei un assistente esperto nella selezione del personale.
        Devi analizzare il seguente contesto e rispondere
        alla domanda dell'utente nel modo più chiaro ed efficace possibile.

        CONTENUTO DEL DOCUMENTO ANALIZZATO:
        [[[
        {context}
        ]]]

        DOMANDA DELL'UTENTE:
        [[[ {question} ]]]

        Se l'utente sta cercando un CV:
        - Conferma che nel file individuato è presente un candidato adatto.
        - Spiega perché è adatto, citando competenze ed esperienze rilevanti.
        - Indica il nome del file in cui si trova il profilo.

        Se l'utente sta chiedendo informazioni su un CV già individuato:
        - Rispondi in modo conciso e diretto.
        - Fornisci solo l'informazione richiesta.
        - Evita dettagli superflui o ripetizioni.

        In entrambi i casi:
        - Utilizza il contesto aggiuntivo per individuare
          il nome del candidato e le altre informazioni utili.
        - Utilizza esclusivamente le informazioni fornite.
        - Non inventare dati mancanti.
        - Rispondi in italiano corretto.

        CONTESTO AGGIUNTIVO:
        [[[
        {context_lines}
        ]]]
        """

    # AVANZAMENTO 6.2 - PROMPT APPROFONDIMENTO CV
    @staticmethod
    def create_info_prompt(context, question):
        return f"""
            Sei un assistente specializzato nel settore HR.

            Devi rispondere a una domanda di approfondimento
            relativa a un candidato già individuato.

            CV DEL CANDIDATO:
            [[[
            {context}
            ]]]

            DOMANDA DELL'UTENTE:
            {question}

            REGOLE:
            - Rispondi esclusivamente utilizzando il CV fornito.
            - Non cercare altri candidati.
            - Non confrontare il candidato con altri profili.
            - Riporta nome, telefono ed email solo se pertinenti
              alla domanda e presenti nel CV.
            - Non inventare informazioni.
            - Se l'informazione non è presente, dichiaralo.
            - Rispondi in modo professionale e sintetico.
        """

    @staticmethod
    def get_db_stats(db):
        """Recupera le statistiche del database."""

        stats = db.get_stats()

        return (
            f"CV archiviati: {stats['total_files']}\n"
            f"Frammenti totali: {stats['total_chunks']}"
        )
