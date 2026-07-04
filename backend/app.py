"""
LPSE Chatbot RAG Backend
FastAPI + ChromaDB + 9router (LLM) + SQLite (SIRUP) + Web Search (Regulasi)
"""
import os
import re
import json
import time
import sqlite3
import pandas as pd
from datetime import datetime
from typing import Optional, List, Dict, Any
from urllib.parse import quote
import httpx
import requests

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# LangChain & Chroma
from langchain_community.document_loaders import WebLoader, TextLoader, UnstructuredURLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# ============================================================================
# CONFIG
# ============================================================================
PORT = 5015
SIRUP_DB = '/root/.openclaw/workspace/App/sirup_bulukumba/bulukumba.db'
CHROMA_DIR = '/root/.openclaw/workspace/App/lpse_chatbot/backend/chroma_db'
DATA_DIR = '/root/.openclaw/workspace/App/lpse_chatbot/backend/data'

# 9router config (free tier)
NINEROUTER_API_KEY = os.environ.get('NINEROUTER_API_KEY', '')
NINEROUTER_BASE = 'https://api.9router.com/v1'
MODEL = '9router/Cal_Combo'

# ============================================================================
# APP
# ============================================================================
app = FastAPI(title="LPSE Bulukumba RAG Chatbot", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# HELPERS
# ============================================================================
def get_sirup_conn():
    return sqlite3.connect(SIRUP_DB)

def init_chroma():
    os.makedirs(CHROMA_DIR, exist_ok=True)
    # Simple OpenAI-compatible embedding (using 9router as OpenAI replacement)
    embeddings = OpenAIEmbeddings(
        openai_api_key=NINEROUTER_API_KEY or 'dummy',
        openai_api_base=NINEROUTER_BASE,
        model='9router/bge-m3'
    )
    return Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)

def parse_budget(budget_str):
    if not budget_str:
        return 0
    return float(str(budget_str).replace('Rp ', '').replace(',', ''))

def format_rp(num):
    if not num:
        return 'Rp 0'
    return f"Rp {int(num):,.0f}".replace(',', '.')

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================
class ChatRequest(BaseModel):
    query: str
    history: Optional[List[Dict[str, str]]] = []
    source_filter: Optional[str] = None  # 'sirup', 'regulasi', 'all'

class SearchRequest(BaseModel):
    keyword: str
    source: Optional[str] = 'all'

# ============================================================================
# REGULASI SOURCES
# ============================================================================
REGULASI_SOURCES = {
    'lkpp': {
        'name': 'LKPP',
        'base_url': 'https://lppp.go.id',
        'search_url': 'https://lppp.go.id/pengadaan-barang-dan-jasa/cari?query={q}',
    },
    'inaproc': {
        'name': 'INAPROC',
        'base_url': 'https://inaproc.id',
        'search_url': 'https://inaproc.id/id/search?q={q}',
    },
    'jdih': {
        'name': 'JDIH',
        'base_url': 'https://jdih.bsu.go.id',
        'search_url': 'https://jdih.bsu.go.id/index.php/search?q={q}',
    },
    'peraturan': {
        'name': 'Peraturan.id',
        'base_url': 'https://peraturan.id',
        'search_url': 'https://peraturan.id/?search={q}',
    },
}

REGULASI_DOCS = [
    # Perpres & PP terkait Pengadaan Barang/Jasa
    {'url': 'https://peraturan.id/perpres/2024/12', 'title': 'Perpres 12/2024 - Pengadaan Barang/Jasa Pemerintah'},
    {'url': 'https://peraturan.id/pp/2021/5', 'title': 'PP 5/2021 - Penyelenggaraan Sistem Pemerintahan Berbasis Elektronik'},
    {'url': 'https://lppm.go.id/pengadaan', 'title': 'LKPP - Panduan Pengadaan'},
]

# ============================================================================
# DATA INGESTION: SIRUP BULUKUMBA → CHROMA
# ============================================================================
def ingest_sirup():
    """Ingest SIRUP Bulukumba data to ChromaDB"""
    print("[INGEST] Starting SIRUP Bulukumba ingestion...")
    conn = get_sirup_conn()
    
    # Get all procurement packages
    df = pd.read_sql("""
        SELECT id, package_name, satker, procurement_type, procurement_method,
               "Cara Pengadaan", budget, work_description, funding_source,
               is_umkm, "Tahun Anggaran", risk_score
        FROM procurement
        WHERE "Tahun Anggaran" >= 2024
        ORDER BY id DESC
    """, conn)
    
    if df.empty:
        print("[INGEST] No SIRUP data found")
        return {'status': 'empty', 'count': 0}
    
    documents = []
    for _, row in df.iterrows():
        budget_num = parse_budget(row.get('budget'))
        
        # Format as document text for embedding
        doc_text = f"""
Paket Pengadaan #{row['id']}

Nama Paket: {row['package_name']}
Satuan Kerja: {row['satker']}
Tahun Anggaran: {row.get('Tahun Anggaran')}
Jenis Pengadaan: {row['procurement_type']}
Metode Pengadaan: {row['procurement_method']}
Cara Pengadaan: {row.get('Cara Pengadaan')}
Sumber Dana: {row['funding_source']}
Nilai HPS: {format_rp(budget_num)}
Keterangan UMKM: {row['is_umkm']}
Deskripsi Pekerjaan: {row['work_description']}
""".strip()
        
        documents.append({
            'text': doc_text,
            'metadata': {
                'source': 'sirup',
                'id': row['id'],
                'package_name': row['package_name'],
                'satker': row['satker'],
                'type': row['procurement_type'],
                'budget': budget_num,
                'tahun': row.get('Tahun Anggaran'),
                'url': f'https://sirup.lkpp.go.id/paket/{row["id"]}'
            }
        })
    
    conn.close()
    
    # Store to Chroma
    try:
        vectordb = init_chroma()
        
        # Clear old SIRUP data
        try:
            vectordb.delete(where={'source': 'sirup'})
        except:
            pass
        
        # Add documents
        texts = [d['text'] for d in documents]
        metadatas = [d['metadata'] for d in documents]
        
        vectordb.add_texts(texts=texts, metadatas=metadatas)
        vectordb.persist()
        
        print(f"[INGEST] Ingested {len(documents)} SIRUP documents")
        return {'status': 'success', 'count': len(documents)}
    except Exception as e:
        print(f"[INGEST] Error: {e}")
        return {'status': 'error', 'error': str(e)}

# ============================================================================
# DATA INGESTION: REGULASI FROM WEB
# ============================================================================
def fetch_regulasi_content(url: str) -> Optional[str]:
    """Fetch content from regulation websites"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            # Simple HTML to text
            text = resp.text
            # Remove scripts and styles
            text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL)
            text = re.sub(r'<style.*?</style>', '', text, flags=re.DOTALL)
            text = re.sub(r'<[^>]+>', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            return text[:5000]  # Limit length
    except Exception as e:
        print(f"[REGULASI] Error fetching {url}: {e}")
    return None

def ingest_regulasi():
    """Ingest regulation documents to ChromaDB"""
    print("[INGEST] Starting Regulasi ingestion...")
    documents = []
    
    for reg in REGULASI_DOCS:
        content = fetch_regulasi_content(reg['url'])
        if content:
            documents.append({
                'text': f"{reg['title']}\n\n{content}",
                'metadata': {
                    'source': 'regulasi',
                    'title': reg['title'],
                    'url': reg['url']
                }
            })
    
    if not documents:
        print("[INGEST] No regulasi content fetched")
        return {'status': 'empty', 'count': 0}
    
    try:
        vectordb = init_chroma()
        
        # Clear old regulasi data
        try:
            vectordb.delete(where={'source': 'regulasi'})
        except:
            pass
        
        texts = [d['text'] for d in documents]
        metadatas = [d['metadata'] for d in documents]
        
        vectordb.add_texts(texts=texts, metadatas=metadatas)
        vectordb.persist()
        
        print(f"[INGEST] Ingested {len(documents)} regulasi documents")
        return {'status': 'success', 'count': len(documents)}
    except Exception as e:
        print(f"[INGEST] Error: {e}")
        return {'status': 'error', 'error': str(e)}

# ============================================================================
# LLM CALL VIA 9router
# ============================================================================
def call_llm(prompt: str, context: str = '') -> str:
    """Call 9router LLM for chat completion"""
    if not NINEROUTER_API_KEY:
        # Fallback demo response
        return "[DEMO] 9router API key belum diset. Response ini hanya untuk testing."
    
    headers = {
        'Authorization': f'Bearer {NINEROUTER_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    system_prompt = """Kamu adalah asisten AI untuk LPSE Kabupaten Bulukumba.
Kamu membantu menjawab pertanyaan seputar pengadaan barang dan jasa pemerintah Indonesia.
Selalu jawab dalam Bahasa Indonesia.
Jika informasi tidak ada di context, katakan bahwa kamu tidak tahu dan sarankan untuk mencari di sumber resmi seperti LKPP atau INAPROC.
Jika pertanyaan tentang paket pengadaan tertentu, gunakan data dari SIRUP Bulukumba."""

    full_prompt = f"{system_prompt}\n\nKonteks:\n{context}\n\nPertanyaan: {prompt}\n\nJawaban:"
    
    payload = {
        'model': MODEL,
        'messages': [{'role': 'user', 'content': full_prompt}],
        'max_tokens': 1024,
        'temperature': 0.7
    }
    
    try:
        resp = requests.post(
            f'{NINEROUTER_BASE}/chat/completions',
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if resp.status_code == 200:
            result = resp.json()
            return result['choices'][0]['message']['content']
        else:
            print(f"[LLM] Error: {resp.status_code} - {resp.text}")
            return f"[Error: API returned {resp.status_code}]"
    except Exception as e:
        print(f"[LLM] Error: {e}")
        return f"[Error: {str(e)}]"

# ============================================================================
# RAG QUERY PIPELINE
# ============================================================================
def rag_query(user_query: str, source_filter: str = 'all', top_k: int = 5) -> Dict[str, Any]:
    """RAG query pipeline: retrieve → augment → generate"""
    
    try:
        vectordb = init_chroma()
        
        # Build filter
        where_filter = None
        if source_filter == 'sirup':
            where_filter = {'source': 'sirup'}
        elif source_filter == 'regulasi':
            where_filter = {'source': 'regulasi'}
        
        # Retrieve
        retriever = vectordb.as_retriever(
            search_kwargs={
                'k': top_k,
                'filter': where_filter
            }
        )
        
        docs = retriever.get_relevant_documents(user_query)
        
        # Build context
        context_parts = []
        sources_used = set()
        
        for doc in docs:
            context_parts.append(f"[Source: {doc.metadata.get('source', 'unknown')}]\n{doc.page_content}")
            sources_used.add(doc.metadata.get('source', 'unknown'))
        
        context = '\n\n---\n\n'.join(context_parts)
        
        if not context:
            # Fallback: query SIRUP directly
            context = query_sirup_fallback(user_query)
        
        # Generate response
        response = call_llm(user_query, context)
        
        return {
            'answer': response,
            'sources': list(sources_used),
            'retrieved_count': len(docs),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"[RAG] Error: {e}")
        return {
            'answer': f"Maaf, terjadi error: {str(e)}",
            'sources': [],
            'retrieved_count': 0,
            'error': str(e)
        }

def query_sirup_fallback(query: str, limit: int = 5) -> str:
    """Direct SQLite query fallback for SIRUP"""
    conn = get_sirup_conn()
    
    # Simple keyword matching
    keywords = query.lower().split()
    where_clauses = []
    params = []
    
    for kw in keywords:
        where_clauses.append("(package_name LIKE ? OR satker LIKE ? OR work_description LIKE ?)")
        p = f'%{kw}%'
        params.extend([p, p, p])
    
    where_sql = ' AND '.join(where_clauses) if where_clauses else '1=1'
    
    df = pd.read_sql(f"""
        SELECT id, package_name, satker, procurement_type, budget
        FROM procurement
        WHERE {where_sql}
        ORDER BY id DESC
        LIMIT {limit}
    """, conn, params=params)
    conn.close()
    
    if df.empty:
        return "Tidak ditemukan data terkait di SIRUP Bulukumba."
    
    result = "Data dari SIRUP Bulukumba:\n\n"
    for _, row in df.iterrows():
        result += f"• {row['package_name']}\n"
        result += f"  SATKER: {row['satker']}\n"
        result += f"  Jenis: {row['procurement_type']}\n"
        result += f"  Nilai: {format_rp(parse_budget(row.get('budget')))}\n\n"
    
    return result

# ============================================================================
# WEB SEARCH FOR REGULATIONS
# ============================================================================
def search_regulasi_web(query: str) -> List[Dict[str, str]]:
    """Search for regulations on web"""
    results = []
    
    # Search each source
    for source_id, info in REGULASI_SOURCES.items():
        search_url = info['search_url'].format(q=quote(query))
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            resp = requests.get(search_url, headers=headers, timeout=10)
            if resp.status_code == 200:
                results.append({
                    'source': info['name'],
                    'url': search_url,
                    'title': f'Hasil pencarian di {info["name"]}'
                })
        except Exception as e:
            print(f"[SEARCH] Error on {source_id}: {e}")
    
    return results

# ============================================================================
# API ENDPOINTS
# ============================================================================
@app.get("/")
def root():
    return {
        'name': 'LPSE Bulukumba RAG Chatbot',
        'version': '1.0',
        'status': 'running'
    }

@app.get("/health")
def health():
    return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}

@app.post("/chat")
def chat(req: ChatRequest):
    """Main chat endpoint with RAG"""
    result = rag_query(
        user_query=req.query,
        source_filter=req.source_filter or 'all'
    )
    return result

@app.post("/search")
def search(req: SearchRequest):
    """Direct search in SIRUP database"""
    conn = get_sirup_conn()
    
    keywords = req.keyword.lower().split()
    where_clauses = []
    params = []
    
    for kw in keywords:
        where_clauses.append("(package_name LIKE ? OR satker LIKE ? OR work_description LIKE ?)")
        p = f'%{kw}%'
        params.extend([p, p, p])
    
    where_sql = ' AND '.join(where_clauses) if where_clauses else '1=1'
    source_filter = ' AND source = ?' if req.source == 'sirup' else ''
    if source_filter:
        params.append(req.source)
    
    df = pd.read_sql(f"""
        SELECT id, package_name, satker, procurement_type, budget, work_description
        FROM procurement
        WHERE {where_sql}{source_filter}
        ORDER BY id DESC
        LIMIT 20
    """, conn, params=params if source_filter else params[:len(params)//3*3])  # Adjust params
    
    conn.close()
    
    results = []
    for _, row in df.iterrows():
        results.append({
            'id': row['id'],
            'package_name': row['package_name'],
            'satker': row['satker'],
            'type': row['procurement_type'],
            'budget': format_rp(parse_budget(row.get('budget'))),
            'description': row.get('work_description', '')[:200]
        })
    
    return {'results': results, 'count': len(results)}

@app.post("/ingest")
def ingest():
    """Trigger data ingestion to ChromaDB"""
    sirup_result = ingest_sirup()
    regulasi_result = ingest_regulasi()
    
    return {
        'sirup': sirup_result,
        'regulasi': regulasi_result,
        'timestamp': datetime.now().isoformat()
    }

@app.get("/stats")
def stats():
    """Get system stats"""
    conn = get_sirup_conn()
    cursor = conn.execute("SELECT COUNT(*) as cnt FROM procurement")
    procurement_count = cursor.fetchone()['cnt']
    
    cursor = conn.execute("SELECT COUNT(*) as cnt FROM realisasi")
    realization_count = cursor.fetchone()['cnt']
    
    conn.close()
    
    # Chroma stats
    try:
        vectordb = init_chroma()
        chroma_count = vectordb._collection.count()
    except:
        chroma_count = 0
    
    return {
        'procurement_packages': procurement_count,
        'realization_records': realization_count,
        'chroma_documents': chroma_count,
        'sirup_db': SIRUP_DB,
        'chroma_dir': CHROMA_DIR
    }

# ============================================================================
# MAIN
# ============================================================================
if __name__ == '__main__':
    print(f"Starting LPSE Chatbot RAG Backend on port {PORT}")
    uvicorn.run(app, host='0.0.0.0', port=PORT)