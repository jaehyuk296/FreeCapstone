"""
패널 검색 RAG 시스템 - Part 1: 환경설정 및 초기화
ChromaDB + Claude Sonnet + kure-v1 임베딩
"""

import os
from typing import List, Dict, Any, Optional, Literal
import chromadb
from chromadb.config import Settings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
import re
import json

# ============================================
# 1. 환경 변수 설정
# ============================================

class Config:
    """시스템 설정"""
    
    # API Keys
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "your-api-key-here")
    
    # ChromaDB 설정
    CHROMA_PERSIST_DIRECTORY = "./chroma_db"
    CHROMA_COLLECTION_NAME = "panel_data"
    
    # 임베딩 모델 (kure-v1)
    EMBEDDING_MODEL_NAME = "nlpai-lab/KoE5"  # kure-v1 대체 모델
    EMBEDDING_DEVICE = "cpu"  # 또는 "cuda"
    
    # Claude 모델
    CLAUDE_MODEL = "claude-sonnet-4-20250514"
    CLAUDE_TEMPERATURE = 0
    
    # 검색 파라미터
    DEFAULT_TOP_K = 20
    SIMILARITY_THRESHOLD = 0.7


# ============================================
# 2. 임베딩 모델 초기화
# ============================================

def initialize_embeddings():
    """kure-v1 임베딩 모델 초기화"""
    embeddings = HuggingFaceEmbeddings(
        model_name=Config.EMBEDDING_MODEL_NAME,
        model_kwargs={'device': Config.EMBEDDING_DEVICE},
        encode_kwargs={'normalize_embeddings': True}
    )
    return embeddings


# ============================================
# 3. ChromaDB 클라이언트 초기화
# ============================================

def initialize_chroma_client():
    """ChromaDB 클라이언트 초기화"""
    client = chromadb.PersistentClient(
        path=Config.CHROMA_PERSIST_DIRECTORY,
        settings=Settings(
            anonymized_telemetry=False,
            allow_reset=True
        )
    )
    return client


# ============================================
# 4. Vector Store 초기화
# ============================================

def initialize_vectorstore(embeddings):
    """Langchain Vector Store 초기화"""
    vectorstore = Chroma(
        collection_name=Config.CHROMA_COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=Config.CHROMA_PERSIST_DIRECTORY
    )
    return vectorstore


# ============================================
# 5. Claude LLM 초기화
# ============================================

def initialize_llm():
    """Claude Sonnet LLM 초기화"""
    llm = ChatAnthropic(
        model=Config.CLAUDE_MODEL,
        temperature=Config.CLAUDE_TEMPERATURE,
        anthropic_api_key=Config.ANTHROPIC_API_KEY,
        max_tokens=4096
    )
    return llm


# ============================================
# 6. 전체 시스템 초기화
# ============================================

class PanelSearchSystem:
    """패널 검색 RAG 시스템 메인 클래스"""
    
    def __init__(self):
        """시스템 초기화"""
        print("🚀 패널 검색 RAG 시스템 초기화 중...")
        
        # 임베딩 모델
        print("📊 임베딩 모델 로딩...")
        self.embeddings = initialize_embeddings()
        
        # ChromaDB
        print("💾 ChromaDB 연결...")
        self.chroma_client = initialize_chroma_client()
        
        # Vector Store
        print("🔍 Vector Store 초기화...")
        self.vectorstore = initialize_vectorstore(self.embeddings)
        
        # Claude LLM
        print("🤖 Claude LLM 초기화...")
        self.llm = initialize_llm()
        
        print("✅ 시스템 초기화 완료!\n")
    
    def get_collection_stats(self):
        """컬렉션 통계 정보"""
        try:
            collection = self.chroma_client.get_collection(
                name=Config.CHROMA_COLLECTION_NAME
            )
            count = collection.count()
            return {
                "total_panels": count,
                "collection_name": Config.CHROMA_COLLECTION_NAME
            }
        except Exception as e:
            return {"error": str(e)}


# ============================================
# 7. 사용 예시
# ============================================

if __name__ == "__main__":
    # 시스템 초기화
    system = PanelSearchSystem()
    
    # 통계 확인
    stats = system.get_collection_stats()
    print(f"📊 패널 데이터: {stats.get('total_panels', 0):,}명")
    print(f"📦 컬렉션명: {stats.get('collection_name', 'N/A')}")