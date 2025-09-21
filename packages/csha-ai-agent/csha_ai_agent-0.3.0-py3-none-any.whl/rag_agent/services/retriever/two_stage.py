import psycopg
import psycopg_pool
import logging
from typing import List, Dict, Any
from rag_agent.core.model_client import get_model_client, ModelConfig, ModelType
from rag_agent.core.config import settings
from rag_agent.services.retriever.base_retriever import BaseRetriever
from rag_agent.services.ner_extractor import NERKeywordExtractor

logger = logging.getLogger(__name__)


class TwoStageRetriever(BaseRetriever):
    """Two-stage retrieval system with document filtering and HyDE-based chunk scoring."""
    
    def __init__(
        self,
        dsn: str,
        top_k_stage1: int = 30,
        top_k_stage2: int = 14,
        sql_timeout_s: float = 30.0,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3,
    ):
        self.dsn = dsn
        self.top_k_stage1 = top_k_stage1
        self.top_k_stage2 = top_k_stage2
        self.sql_timeout_s = sql_timeout_s
        self.vector_weight = vector_weight
        self.keyword_weight = keyword_weight
        
        # Create connection pool for better performance
        self.pool = psycopg_pool.ConnectionPool(
            dsn,
            min_size=1,
            max_size=3,
            timeout=sql_timeout_s
        )

        # Initialize models
        self.embedding_model = settings.EMBEDDING_MODEL
        self.embedding_config = ModelConfig(
            model_type=ModelType.EMBEDDING,
            model_name=self.embedding_model
        )
        
        # Initialize components
        self.ner_extractor = NERKeywordExtractor()
        self.embedding_client = get_model_client(self.embedding_config)

    def _embed_query(self, query: str) -> List[float]:
        """Generate embedding for a query."""
        return self.embedding_client.embed_query(query)

    def _stage2_chunk_retrieval(self, enhanced_query: str, query_vector: List[float], document_uuids: List[str]) -> List[str]:
        """Stage 2: Retrieve chunks using enhanced query and document filtering."""
        try:
            # Load Stage 2 SQL query (simplified without HyDE)
            stage2_sql = (
                open(settings.SQL_DIR / "stage2_chunk_retrieval.sql").read()
                .replace("%TOP_K%", str(self.top_k_stage2))
            )

            with self.pool.connection() as db_connection:
                with db_connection.cursor() as db_cursor:
                    # Set timeout
                    db_cursor.execute(f"SET LOCAL statement_timeout = {int(self.sql_timeout_s * 1000)};")
                    
                    # Execute Stage 2 query
                    db_cursor.execute(
                        stage2_sql,
                        {
                            'query': enhanced_query,
                            'vector': query_vector,
                            'document_uuids': document_uuids,
                            'vector_weight': self.vector_weight,
                            'keyword_weight': self.keyword_weight
                        }
                    )
                    rows = db_cursor.fetchall()
                    
                    # Extract content chunks with links and combine chunks from same document
                    chunks_by_url = {}
                    for row in rows:
                        content_chunk = row[0]
                        link = row[2] if len(row) > 2 else ""
                        
                        if link in chunks_by_url:
                            # Combine chunks from the same document
                            chunks_by_url[link] += f"\n\n{content_chunk}"
                        else:
                            chunks_by_url[link] = content_chunk
                    
                    # Format combined chunks with proper tags for DEFAULT_TEMPLATE
                    chunks = []
                    for link, combined_content in chunks_by_url.items():
                        formatted_chunk = f"<text>{combined_content}</text>"
                        if link:
                            formatted_chunk += f"\n<reference><url>{link}</url></reference>"
                        chunks.append(formatted_chunk)
                    
                    logger.info(f"🧩 Stage 2: Retrieved {len(chunks)} chunks")
                    for i, chunk in enumerate(chunks, 1):  # Show all chunks
                        logger.info(f"   {i}. {chunk}")
                    
                    # Return chunks WITHOUT numbers for the model
                    return chunks
                    
        except Exception as e:
            logger.error(f"Error in Stage 2 chunk retrieval: {e}")
            return []

    def _stage1_document_filter(self, enhanced_query: str, query_vector: List[float]) -> List[Dict[str, Any]]:
        """Stage 1: Filter candidate documents using summaries."""
        try:
            # Load Stage 1 SQL query
            stage1_sql = (
                open(settings.SQL_DIR / "stage1_document_filter.sql").read()
                .replace("%TOP_K%", str(self.top_k_stage1))
            )

            with self.pool.connection() as db_connection:
                with db_connection.cursor() as db_cursor:
                    # Set timeout
                    db_cursor.execute(f"SET LOCAL statement_timeout = {int(self.sql_timeout_s * 1000)};")
                    
                    # Execute Stage 1 query
                    db_cursor.execute(
                        stage1_sql,
                        {
                            'query': enhanced_query,
                            'vector': query_vector,
                            'vector_weight': self.vector_weight,
                            'keyword_weight': self.keyword_weight
                        }
                    )
                    rows = db_cursor.fetchall()
                    
                    # Convert to list of dictionaries
                    documents = []
                    for row in rows:
                        documents.append({
                            'document_uuid': row[0],
                            'title': row[1],
                            'excerpt': row[2],
                            'combined_score': row[3]
                        })
                    
                    logger.info(f"📄 Stage 1: Retrieved {len(documents)} documents")
                    for i, doc in enumerate(documents[:3], 1):  # Show top 3
                        logger.info(f"   {i}. {doc['title'][:50]}... (score: {doc['combined_score']:.3f})")
                    return documents
                    
        except Exception as e:
            logger.error(f"Error in Stage 1 document filtering: {e}")
            return []


    def retrieve(self, query: str) -> List[str]:
        """
        Two-stage retrieval process:
        1. Extract keywords and enhance query
        2. Stage 1: Filter documents using summaries
        3. Stage 2: Retrieve chunks using enhanced query
        """
        logger.info(f"🚀 Starting two-stage retrieval for: '{query}'")
        try:
            # Step 1: Extract keywords and enhance query
            enhanced_query = self.ner_extractor.extract_keywords(query)
            query_vector = self._embed_query(enhanced_query)
            
            # Step 2: Stage 1 - Document filtering
            documents = self._stage1_document_filter(enhanced_query, query_vector)
            
            if not documents:
                logger.warning("No documents found in Stage 1")
                return []
            
            # Extract document UUIDs for Stage 2
            document_uuids = [doc['document_uuid'] for doc in documents]
            
            # Step 3: Stage 2 - Chunk retrieval using enhanced query
            chunks = self._stage2_chunk_retrieval(enhanced_query, query_vector, document_uuids)
            
            logger.info(f"🎯 Two-stage retrieval complete: {len(chunks)} final chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error in two-stage retrieval: {e}")
            return []
    
    def __del__(self):
        """Clean up connection pool when object is destroyed."""
        if hasattr(self, 'pool'):
            self.pool.close()
