import os
import shutil
import logging
from typing import List

from Mama.cbLLM import cbLLM
from Mama.utils import generate_random_token, get_session, save_kb

# Updated LangChain imports
try:
    from langchain_core.prompts import PromptTemplate  # type: ignore
except Exception:
    from langchain import PromptTemplate  # type: ignore

try:
    from langchain.chains.summarize import load_summarize_chain  # type: ignore
except Exception:
    load_summarize_chain = None  # type: ignore

try:
    from langchain_community.vectorstores import FAISS  # type: ignore
except Exception:
    from langchain.vectorstores import FAISS  # type: ignore

try:
    from langchain_community.document_loaders import PyPDFDirectoryLoader, CSVLoader  # type: ignore
except Exception:
    from langchain.document_loaders import PyPDFDirectoryLoader  # type: ignore
    from langchain.document_loaders.csv_loader import CSVLoader  # type: ignore

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter  # type: ignore
except Exception:
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter  # type: ignore
    except Exception:
        RecursiveCharacterTextSplitter = None  # type: ignore

try:
    from langchain_core.documents import Document  # type: ignore
except Exception:
    from langchain.schema import Document  # type: ignore

from Mama.embedding_factory import get_embeddings

def index_documents(folder) -> List[Document] :
    logging.info("Reading folder: "+folder)
    #loader = DirectoryLoader(folder, show_progress=True)
    loader = PyPDFDirectoryLoader(folder)
    docs = loader.load()
    logging.info(f"Read {len(docs)} documents")
    if RecursiveCharacterTextSplitter:
        try:
            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
        except TypeError:
            splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=500, chunk_overlap=0)  # fallback
        splits = splitter.split_documents(documents=docs)
    else:
        splits = docs
    return splits

def train_on_documents(kb_dir, kb_id, src_dir, documents = [], title="", description="", return_summary=False) -> str:
    summary = ""
    logging.debug(documents)

    if not documents or len(documents) == 0:
        logging.info("Reading folder: "+src_dir)
        loader = PyPDFDirectoryLoader(src_dir)
        docs = loader.load()
        logging.info(f"Read {len(docs)} documents")

        i = 0
        if RecursiveCharacterTextSplitter:
            try:
                splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
            except TypeError:
                splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=500, chunk_overlap=0)
        else:
            splitter = None
        for document in docs:
            logging.info(f"Splitting doc {i+1}") 
            logging.debug(f"DOC={document}")
            s = splitter.split_documents(documents=[document]) if splitter else [document]
            logging.info(f"generated {len(s)} splits for document {i+1}")
            logging.info(f"Saving doc nr. {i+1}")
            _save_vector_store(kb_dir, kb_id, s, title=title, description=description)
            i=i+1
    else:
        _save_vector_store(kb_dir, kb_id, documents, title=title, description=description)
    
    if return_summary == True and documents and len(documents) > 0:
        try:
            llm = None
            try:
                llm = cbLLM().get_llm()
            except Exception as e:
                logging.info(f"Error loading llm {e}")
                return ""
            
            # Skip summarization for Dummy/offline LLMs or if chain unavailable
            if not llm or load_summarize_chain is None:
                logging.info("Cannot load LLM")
                return ""
            
            prompt_template = """Scrivi IN ITALIANO un sommario conciso e il link di partenza (SOURCE LINK) the seguente testo:
                "{text}"
                Inizia la risposta con "il presente documento"
                SOMMARIO CONCISO:
                SOURCE LINK:"""
            prompt = PromptTemplate(template=prompt_template, input_variables=["text"])
            try:
                chain = load_summarize_chain(llm, chain_type='map_reduce', map_prompt=prompt)
                # Some versions expect list of Documents
                summary = chain.invoke([documents[0]]) if hasattr(chain, "invoke") else chain.run([documents[0]])
            except Exception as e:
                logging.info(f"Errore nel caricare il summari del documento: {e}")
                summary = ""
            
            logging.info(f"---- SUMMARY PRODOTTO: {summary}")
            
        except Exception as e:
            logging.info(f"Errore nel caricare il summari del documento: {e}")

    return summary

def train_tmp_single_doc(user_id, sDir, kb_root_dir, session_id="", kb_id="") -> str :
    logging.debug(f"train_tmp_single_doc:: recevied params user_id={user_id}, session_id={session_id}, sDir={sDir}")

    sDocumentID = generate_random_token(16)
    sSrcDir = user_id+"-"+sDocumentID
    summary = ""
    
    logging.debug("mkdir: "+sSrcDir)
    try :
        os.mkdir(sSrcDir)
        logging.debug("copy document from: "+sDir+" to "+sSrcDir)
        shutil.move(sDir, sSrcDir)
    except Exception as e:
        logging.info(f"train_tmp_single_doc::exception during directory operations: {e}")
        return ""
    
    if session_id:
        session = get_session(user_id, session_id)
        if session:
            kb_id = session.get("kb_id", [])
        else:
            logging.debug("train_tmp_single_doc::invalid session")
            return ""

    if not kb_id:
        logging.debug("train_tmp_single_doc::invalid KB_ID")
        return ""
    
    summary = ""
    try:
        summary = train_single_doc(kb_root_dir, kb_id, sSrcDir)
        logging.debug("removing "+sDir)
        shutil.rmtree(sSrcDir)
    except Exception as e:
        logging.info(f"train_tmp_single_doc::exception during directory operations: {e}")
        
    return summary

def train_single_doc(kb_root_dir, kb_id, source_dir) -> str:
    summary = ""
    try:
        documents = index_documents(source_dir)
        if not documents:
            logging.info(f"Nessun documento trovato")
            return ""
        
        summary = train_on_documents(kb_root_dir, kb_id, src_dir="", documents=documents, title="", description="", return_summary=False)
        
    except Exception as e:
        logging.info(f"Errore nel caricare il documento: {e}")

    return summary

def train_on_csv(kb_root_dir, kb_id, title, description, filename, field_names, delimiter, quote_char, source_column):
    try:
        csv_args={
            'delimiter': delimiter,
            'quotechar': quote_char,
            'fieldnames': field_names
        }

        kb_path = kb_root_dir+"/"+kb_id

        loader = CSVLoader(file_path=filename, csv_args=csv_args, source_column=source_column)
        if not loader:
            logging.info(f"No Loader found")
            return False

        data = loader.load()

        if not data:
            logging.info(f"Nessun dato trovato")
            return False
        
        if os.path.exists(kb_path):
            faiss = FAISS.load_local(kb_path, embeddings=get_embeddings(), allow_dangerous_deserialization=True)
            faiss.add_documents(documents=data)
           
        else:
            faiss = FAISS.from_documents(documents=data, embedding=get_embeddings())

        logging.debug("Saving index...")
        if faiss:
            faiss.save_local(kb_path)
            save_kb(kb_id, title, description)
        else:
            logging.debug(f"Error saving on FAISS {kb_path}")
            return False

    except Exception as e:
        logging.info(f"Errore nel caricare il documento: {e}")
        return False

    return True


def _save_vector_store(kb_dir, kb_id, documents, title, description):
    embeddings = get_embeddings()
    kb_path = kb_dir+"/"+kb_id
    try:
        if os.path.exists(kb_path):
            faiss = FAISS.load_local(kb_path, embeddings=embeddings, allow_dangerous_deserialization=True)
            faiss.add_documents(documents=documents)
           
        else:
            faiss = FAISS.from_documents(documents=documents, embedding=embeddings) #TODO: Capire come mai c'era [documents[0]]

        logging.debug("Saving index...")
        faiss.save_local(kb_path)
        
        save_kb(kb_id, title, description)
     
    except Exception as e:
        logging.info(f"Errore nel salvare il document store: {e}")
