import logging
import rag_agent.core.logging_config
logger = logging.getLogger(__name__)

import asyncio
from typing import List, AsyncGenerator
from langchain_openai import ChatOpenAI

from rag_agent.core.config import settings, Settings
from rag_agent.services.retriever.base_retriever import BaseRetriever
from rag_agent.services.retriever.hybrid import HybridRetriever
from rag_agent.services.retriever.two_stage import TwoStageRetriever
from rag_agent.core.model_client import get_model_client, ModelConfig, ModelType
from rag_agent.core.enums import RetrievalMethod

from rag_agent.core.prompt_templates import DEFAULT_TEMPLATE


def get_context(
    query: str,
    retriever: BaseRetriever,
) -> List[str]:
    """Get the context for the query."""
    return retriever.retrieve(query)


async def handle_query(
    query: str,
    retriever: BaseRetriever,
    model_client: ChatOpenAI,
    prompt_template: str
) -> AsyncGenerator[str, None]:
    """
    Run one retrieval+generation cycle:
    1. Get context
    2. Stream LLM response
    """
    context_parts = get_context(query, retriever)
    if not context_parts:
        logger.warning("No context parts found for query: %s", query)
        return

    context = " ".join(context_parts).replace("\n", "\n\t")
    
    # Build the prompt
    prompt = prompt_template.format(query=query, context=context)
    
    response = ""
    async for response_chunk in model_client.astream(prompt):
        if hasattr(response_chunk, 'content'):
            chunk_content = response_chunk.content
        else:
            chunk_content = str(response_chunk)
        response += chunk_content
        yield chunk_content
    
    logger.info(f"✅ Response generated ({len(response)} characters):")
    logger.info(f"   {response}")


def make_retriever(
    *,
    method: RetrievalMethod,
    DSN: str,
    TOP_K: int,
    SQL_TIMEOUT_S: float,
    VECTOR_WEIGHT: float,
    KEYWORD_WEIGHT: float,
) -> BaseRetriever:
    """Return a retriever based on the method."""
    if method == RetrievalMethod.HYBRID:
        return HybridRetriever(
            dsn=DSN,
            top_k=TOP_K,
            sql_timeout_s=SQL_TIMEOUT_S,
            vector_weight=VECTOR_WEIGHT,
            keyword_weight=KEYWORD_WEIGHT
        )
    elif method == RetrievalMethod.TWO_STAGE:
        return TwoStageRetriever(
            dsn=DSN,
            top_k_stage1=10,  # Stage 1: filter documents (reduced from 30)
            top_k_stage2=TOP_K,  # Stage 2: final chunks
            sql_timeout_s=SQL_TIMEOUT_S,
            vector_weight=VECTOR_WEIGHT,
            keyword_weight=KEYWORD_WEIGHT
        )
    elif method is RetrievalMethod.KEYWORD or method is RetrievalMethod.VECTOR:
        raise ValueError(f"{method} retreival method has not been implemented yet.") 
    else:
        raise ValueError(f"Unsupported retrieval method: {method}")


async def retrieval_augmented_generation(query: str) -> AsyncGenerator[str, None]:
    # Get the model client directly
    model_config = ModelConfig(
        model_type=ModelType.QUERY,
        model_name=settings.QUERY_MODEL,
        streaming=True
    )
    model_client = get_model_client(model_config)

    retriever = make_retriever(
            method=settings.RETRIEVAL_METHOD,
            DSN=settings.DSN,
            TOP_K=settings.TOP_K,
            SQL_TIMEOUT_S=settings.SQL_TIMEOUT_S,
            VECTOR_WEIGHT=settings.VECTOR_WEIGHT,
            KEYWORD_WEIGHT=settings.KEYWORD_WEIGHT
    )

    async for response_chunk in handle_query(
        query,
        retriever,
        model_client,
        DEFAULT_TEMPLATE
    ):
        yield response_chunk


async def main() -> None:
    """CLI REPL: read a query and log response."""
    while True:
        raw_query = await asyncio.to_thread(
            input, "\nEnter your query (or 'quit' to exit):\n>>> "
        )
        query = raw_query.strip()
        if not query or query.lower() == "quit":
            break

        # Process the query and let logging handle the output
        async for response_chunk in retrieval_augmented_generation(query):
            pass  # Just consume the chunks, logging will show the full response


if __name__ == "__main__":
    asyncio.run(main())