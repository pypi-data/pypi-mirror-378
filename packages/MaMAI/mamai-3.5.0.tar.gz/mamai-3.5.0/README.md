# MaMa

Toolkit modulare per costruire pipeline RAG (Retrieval-Augmented Generation) su
documenti locali e interrogare un LLM tramite LangChain.

## Panoramica
- Indicizza PDF, CSV e pagine web in un vector store FAISS.
- Recupera i documenti pertinenti e compone prompt personalizzati per il modello.
- Gestisce sessioni, memoria conversazionale e configurazione tramite un file JSON.

## Requisiti
- Python 3.10+ (testato con 3.12).
- `pip` aggiornato.
- Dipendenze principali (versioni minime consigliate):
  - `langchain>=0.2.10`
  - `langchain-community`
  - `langchain-openai`
- `langchain-text-splitters`
- `faiss-cpu`
- `pypdf`
- `flask`

Installa tutto con:

```bash
pip install -U "langchain>=0.2.10" langchain-community langchain-openai \
  langchain-text-splitters faiss-cpu pypdf bs4 urllib3 requests
```

## Configurazione Rapida
1. Facoltativo: installa il pacchetto in modalità sviluppo.
   ```bash
   pip install -e .
   ```
2. (Solo per test offline) usa embeddings locali e un LLM di test impostando:
   ```bash
   export MAMA_EMBEDDINGS=simple
   ```
   Con le variabili di configurazione predefinite il modello "Dummy" viene
   caricato automaticamente e non richiede chiavi API.

## Test CLI di Ingestion & Prompt
1. Esegui il test end-to-end:
   ```bash
   make test
   ```
   Il target crea un PDF di prova, aggiorna `database/db.json`, indicizza i
   documenti in `test/kb/` ed esegue una domanda di esempio.
2. Verifica il log dettagliato in `test/logs/test.log`.
3. L’output standard termina con `TEST OK: ingestion and prompting completed.`

## Test Web (Flask)
1. Avvia il backend e l'interfaccia HTML di esempio:
   ```bash
   make web
   ```
2. Apri <http://127.0.0.1:5000> e prova l'input nella textarea.
3. Il backend espone `POST /ask` e restituisce `answer` e `documents` in JSON.
4. Per eseguire una domanda rapida da CLI senza server:
   ```bash
   python test/web/app.py --demo
   ```
5. Per avviare il server caricando automaticamente la chiave da `.env` e generare `flask.log`:
   ```bash
   bash test/start_web_test.sh
   ```

### Area Admin web
- Naviga su <http://127.0.0.1:5000/admin> per consultare:
  - elenco documenti indicizzati (estratto e sorgente);
  - statistiche sull’indice FAISS (numero vettori, dimensione embedding, spazio su disco);
  - modulo di upload per ingestare un nuovo PDF di test.
- I file caricati vengono processati con gli stessi helper di MaMa (split e inserimento in FAISS).

## Rilasciare una nuova versione su PyPI
1. Aggiorna `setup.py` con la nuova versione (es. 3.5.0) e assegna un tag Git.
2. Esegui la pipeline locale (test + build) con `python publish.py` oppure separatamente con `make test` e `make package`.
4. Crea una release GitHub (`git tag vX.Y.Z && git push --tags`).
5. Il workflow **Publish MaMa Package** eseguirà build e `test/cli_test.py`, quindi pubblicherà su PyPI usando `PYPI_API_TOKEN`.

## File Generati dal Test
- `database/db.json`: database JSON temporaneo per configurazione/sessions.
- `test/kb/`: archivio FAISS della knowledge base di prova.
- `test/pdf_src/`: PDF generato per l’ingestion.
- `test/logs/test.log`: log con esito e passaggi principali.
- `test/logs/web.log`: log dell'applicazione web di esempio.

Puoi eliminare tutto con `make clean` (vedi Makefile).

## Utilizzo con Modelli Reali
Per usare un modello OpenAI:
1. Popola `database/db.json` con `config.model = "OpenAi"` e i parametri
   necessari (`openai_api_key`, temperatura, ecc.).
2. Rimuovi `MAMA_EMBEDDINGS=simple` (verranno usati gli embeddings
   `HuggingFaceEmbeddings`).
3. Fornisci un prompt personalizzato nella sezione LLM del database o nella
   sessione utente.
