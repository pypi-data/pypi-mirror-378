import logging
from typing import Optional, Set
from ..instruments import Instruments


def is_package_installed(package_name: str) -> bool:
    """Check if a package is installed"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False


def init_instrumentations(
    instruments: Optional[Set[Instruments]] = None,
    block_instruments: Optional[Set[Instruments]] = None,
) -> bool:
    """
    Initialize OpenTelemetry instrumentations for specified libraries.
    
    Args:
        instruments: Set of instruments to enable. If None, enables all available.
        block_instruments: Set of instruments to explicitly block.
    
    Returns:
        bool: True if at least one instrument was successfully initialized.
    """
    block_instruments = block_instruments or set()
    
    # Default to all instruments if none specified
    if instruments is None:
        instruments = set(Instruments)
    
    # Remove blocked instruments
    instruments = instruments - block_instruments
    
    instrument_count = 0
    
    for instrument in instruments:
        try:
            if _init_single_instrument(instrument):
                instrument_count += 1
        except Exception as e:
            logging.warning(f"Failed to initialize {instrument.value} instrumentation: {e}")
    
    if instrument_count == 0:
        logging.warning("No instrumentations were successfully initialized")
        return False
    
    logging.info(f"Successfully initialized {instrument_count} instrumentations")
    return True


def _init_single_instrument(instrument: Instruments) -> bool:
    """Initialize a single instrument"""
    
    if instrument == Instruments.OPENAI:
        return _init_openai()
    elif instrument == Instruments.ANTHROPIC:
        return _init_anthropic()
    elif instrument == Instruments.COHERE:
        return _init_cohere()
    elif instrument == Instruments.MISTRAL:
        return _init_mistral()
    elif instrument == Instruments.OLLAMA:
        return _init_ollama()
    elif instrument == Instruments.GROQ:
        return _init_groq()
    elif instrument == Instruments.TOGETHER:
        return _init_together()
    elif instrument == Instruments.REPLICATE:
        return _init_replicate()
    elif instrument == Instruments.TRANSFORMERS:
        return _init_transformers()
    elif instrument == Instruments.BEDROCK:
        return _init_bedrock()
    elif instrument == Instruments.SAGEMAKER:
        return _init_sagemaker()
    elif instrument == Instruments.VERTEXAI:
        return _init_vertexai()
    elif instrument == Instruments.GOOGLE_GENERATIVEAI:
        return _init_google_generativeai()
    elif instrument == Instruments.WATSONX:
        return _init_watsonx()
    elif instrument == Instruments.ALEPHALPHA:
        return _init_alephalpha()
    elif instrument == Instruments.PINECONE:
        return _init_pinecone()
    elif instrument == Instruments.QDRANT:
        return _init_qdrant()
    elif instrument == Instruments.CHROMA:
        return _init_chroma()
    elif instrument == Instruments.MILVUS:
        return _init_milvus()
    elif instrument == Instruments.WEAVIATE:
        return _init_weaviate()
    elif instrument == Instruments.LANCEDB:
        return _init_lancedb()
    elif instrument == Instruments.MARQO:
        return _init_marqo()
    elif instrument == Instruments.LANGCHAIN:
        return _init_langchain()
    elif instrument == Instruments.LLAMA_INDEX:
        return _init_llama_index()
    elif instrument == Instruments.HAYSTACK:
        return _init_haystack()
    elif instrument == Instruments.CREW:
        return _init_crew()
    elif instrument == Instruments.MCP:
        return _init_mcp()
    elif instrument == Instruments.REDIS:
        return _init_redis()
    elif instrument == Instruments.REQUESTS:
        return _init_requests()
    elif instrument == Instruments.URLLIB3:
        return _init_urllib3()
    elif instrument == Instruments.PYMYSQL:
        return _init_pymysql()
    else:
        logging.warning(f"Unknown instrument: {instrument}")
        return False


# Individual instrument initializers
def _init_openai() -> bool:
    """Initialize OpenAI instrumentation"""
    if not is_package_installed("openai"):
        return False
    
    try:
        from opentelemetry.instrumentation.openai import OpenAIInstrumentor
        instrumentor = OpenAIInstrumentor()
        if not instrumentor.is_instrumented_by_opentelemetry:
            instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Failed to initialize OpenAI instrumentation: {e}")
        return False


def _init_anthropic() -> bool:
    """Initialize Anthropic instrumentation"""
    if not is_package_installed("anthropic"):
        return False
    
    try:
        from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor
        instrumentor = AnthropicInstrumentor()
        if not instrumentor.is_instrumented_by_opentelemetry:
            instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Failed to initialize Anthropic instrumentation: {e}")
        return False


def _init_cohere() -> bool:
    """Initialize Cohere instrumentation"""
    if not is_package_installed("cohere"):
        return False
    
    try:
        from opentelemetry.instrumentation.cohere import CohereInstrumentor
        instrumentor = CohereInstrumentor()
        if not instrumentor.is_instrumented_by_opentelemetry:
            instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Failed to initialize Cohere instrumentation: {e}")
        return False


def _init_mistral() -> bool:
    """Initialize Mistral instrumentation"""
    if not is_package_installed("mistralai"):
        return False
    
    try:
        from opentelemetry.instrumentation.mistralai import MistralAiInstrumentor
        instrumentor = MistralAiInstrumentor()
        if not instrumentor.is_instrumented_by_opentelemetry:
            instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Failed to initialize Mistral instrumentation: {e}")
        return False


def _init_ollama() -> bool:
    """Initialize Ollama instrumentation"""
    if not is_package_installed("ollama"):
        return False
    
    try:
        from opentelemetry.instrumentation.ollama import OllamaInstrumentor
        instrumentor = OllamaInstrumentor()
        if not instrumentor.is_instrumented_by_opentelemetry:
            instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Failed to initialize Ollama instrumentation: {e}")
        return False


def _init_groq() -> bool:
    """Initialize Groq instrumentation"""
    if not is_package_installed("groq"):
        return False
    
    try:
        from opentelemetry.instrumentation.groq import GroqInstrumentor
        instrumentor = GroqInstrumentor()
        if not instrumentor.is_instrumented_by_opentelemetry:
            instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Failed to initialize Groq instrumentation: {e}")
        return False


def _init_together() -> bool:
    """Initialize Together instrumentation"""
    if not is_package_installed("together"):
        return False
    
    try:
        from opentelemetry.instrumentation.together import TogetherInstrumentor
        instrumentor = TogetherInstrumentor()
        if not instrumentor.is_instrumented_by_opentelemetry:
            instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Failed to initialize Together instrumentation: {e}")
        return False


def _init_replicate() -> bool:
    """Initialize Replicate instrumentation"""
    if not is_package_installed("replicate"):
        return False
    
    try:
        from opentelemetry.instrumentation.replicate import ReplicateInstrumentor
        instrumentor = ReplicateInstrumentor()
        if not instrumentor.is_instrumented_by_opentelemetry:
            instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Failed to initialize Replicate instrumentation: {e}")
        return False


def _init_transformers() -> bool:
    """Initialize Transformers instrumentation"""
    if not is_package_installed("transformers"):
        return False
    
    try:
        from opentelemetry.instrumentation.transformers import TransformersInstrumentor
        instrumentor = TransformersInstrumentor()
        if not instrumentor.is_instrumented_by_opentelemetry:
            instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Failed to initialize Transformers instrumentation: {e}")
        return False


def _init_bedrock() -> bool:
    """Initialize AWS Bedrock instrumentation"""
    if not is_package_installed("boto3"):
        return False
    
    try:
        from opentelemetry.instrumentation.bedrock import BedrockInstrumentor
        instrumentor = BedrockInstrumentor()
        if not instrumentor.is_instrumented_by_opentelemetry:
            instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Failed to initialize Bedrock instrumentation: {e}")
        return False


def _init_sagemaker() -> bool:
    """Initialize AWS SageMaker instrumentation"""
    if not is_package_installed("boto3"):
        return False
    
    try:
        from opentelemetry.instrumentation.sagemaker import SageMakerInstrumentor
        instrumentor = SageMakerInstrumentor()
        if not instrumentor.is_instrumented_by_opentelemetry:
            instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Failed to initialize SageMaker instrumentation: {e}")
        return False


def _init_vertexai() -> bool:
    """Initialize Google Vertex AI instrumentation"""
    if not is_package_installed("google.cloud.aiplatform"):
        return False
    
    try:
        from opentelemetry.instrumentation.vertexai import VertexAIInstrumentor
        instrumentor = VertexAIInstrumentor()
        if not instrumentor.is_instrumented_by_opentelemetry:
            instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Failed to initialize Vertex AI instrumentation: {e}")
        return False


def _init_google_generativeai() -> bool:
    """Initialize Google Generative AI instrumentation"""
    if not is_package_installed("google.generativeai"):
        return False
    
    try:
        from opentelemetry.instrumentation.google_generativeai import GoogleGenerativeAiInstrumentor
        instrumentor = GoogleGenerativeAiInstrumentor()
        if not instrumentor.is_instrumented_by_opentelemetry:
            instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Failed to initialize Google Generative AI instrumentation: {e}")
        return False


def _init_watsonx() -> bool:
    """Initialize IBM Watson X instrumentation"""
    if not is_package_installed("ibm_watsonx_ai"):
        return False
    
    try:
        from opentelemetry.instrumentation.watsonx import WatsonxInstrumentor
        instrumentor = WatsonxInstrumentor()
        if not instrumentor.is_instrumented_by_opentelemetry:
            instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Failed to initialize Watson X instrumentation: {e}")
        return False


def _init_alephalpha() -> bool:
    """Initialize Aleph Alpha instrumentation"""
    if not is_package_installed("aleph_alpha_client"):
        return False
    
    try:
        from opentelemetry.instrumentation.alephalpha import AlephAlphaInstrumentor
        instrumentor = AlephAlphaInstrumentor()
        if not instrumentor.is_instrumented_by_opentelemetry:
            instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Failed to initialize Aleph Alpha instrumentation: {e}")
        return False


def _init_pinecone() -> bool:
    """Initialize Pinecone instrumentation"""
    if not is_package_installed("pinecone"):
        return False
    
    try:
        from opentelemetry.instrumentation.pinecone import PineconeInstrumentor
        instrumentor = PineconeInstrumentor()
        if not instrumentor.is_instrumented_by_opentelemetry:
            instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Failed to initialize Pinecone instrumentation: {e}")
        return False


def _init_qdrant() -> bool:
    """Initialize Qdrant instrumentation"""
    if not is_package_installed("qdrant_client"):
        return False
    
    try:
        from opentelemetry.instrumentation.qdrant import QdrantInstrumentor
        instrumentor = QdrantInstrumentor()
        if not instrumentor.is_instrumented_by_opentelemetry:
            instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Failed to initialize Qdrant instrumentation: {e}")
        return False


def _init_chroma() -> bool:
    """Initialize Chroma instrumentation"""
    if not is_package_installed("chromadb"):
        return False
    
    try:
        from opentelemetry.instrumentation.chromadb import ChromaInstrumentor
        instrumentor = ChromaInstrumentor()
        if not instrumentor.is_instrumented_by_opentelemetry:
            instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Failed to initialize Chroma instrumentation: {e}")
        return False


def _init_milvus() -> bool:
    """Initialize Milvus instrumentation"""
    if not is_package_installed("pymilvus"):
        return False
    
    try:
        from opentelemetry.instrumentation.milvus import MilvusInstrumentor
        instrumentor = MilvusInstrumentor()
        if not instrumentor.is_instrumented_by_opentelemetry:
            instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Failed to initialize Milvus instrumentation: {e}")
        return False


def _init_weaviate() -> bool:
    """Initialize Weaviate instrumentation"""
    if not is_package_installed("weaviate"):
        return False
    
    try:
        from opentelemetry.instrumentation.weaviate import WeaviateInstrumentor
        instrumentor = WeaviateInstrumentor()
        if not instrumentor.is_instrumented_by_opentelemetry:
            instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Failed to initialize Weaviate instrumentation: {e}")
        return False


def _init_lancedb() -> bool:
    """Initialize LanceDB instrumentation"""
    if not is_package_installed("lancedb"):
        return False
    
    try:
        from opentelemetry.instrumentation.lancedb import LanceDBInstrumentor
        instrumentor = LanceDBInstrumentor()
        if not instrumentor.is_instrumented_by_opentelemetry:
            instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Failed to initialize LanceDB instrumentation: {e}")
        return False


def _init_marqo() -> bool:
    """Initialize Marqo instrumentation"""
    if not is_package_installed("marqo"):
        return False
    
    try:
        from opentelemetry.instrumentation.marqo import MarqoInstrumentor
        instrumentor = MarqoInstrumentor()
        if not instrumentor.is_instrumented_by_opentelemetry:
            instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Failed to initialize Marqo instrumentation: {e}")
        return False


def _init_langchain() -> bool:
    """Initialize LangChain instrumentation"""
    if not is_package_installed("langchain"):
        return False
    
    try:
        from opentelemetry.instrumentation.langchain import LangchainInstrumentor
        instrumentor = LangchainInstrumentor()
        if not instrumentor.is_instrumented_by_opentelemetry:
            instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Failed to initialize LangChain instrumentation: {e}")
        return False


def _init_llama_index() -> bool:
    """Initialize LlamaIndex instrumentation"""
    if not is_package_installed("llama_index"):
        return False
    
    try:
        from opentelemetry.instrumentation.llama_index import LlamaIndexInstrumentor
        instrumentor = LlamaIndexInstrumentor()
        if not instrumentor.is_instrumented_by_opentelemetry:
            instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Failed to initialize LlamaIndex instrumentation: {e}")
        return False


def _init_haystack() -> bool:
    """Initialize Haystack instrumentation"""
    if not is_package_installed("haystack"):
        return False
    
    try:
        from opentelemetry.instrumentation.haystack import HaystackInstrumentor
        instrumentor = HaystackInstrumentor()
        if not instrumentor.is_instrumented_by_opentelemetry:
            instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Failed to initialize Haystack instrumentation: {e}")
        return False


def _init_crew() -> bool:
    """Initialize CrewAI instrumentation"""
    if not is_package_installed("crewai"):
        return False
    
    try:
        from opentelemetry.instrumentation.crewai import CrewAIInstrumentor
        instrumentor = CrewAIInstrumentor()
        if not instrumentor.is_instrumented_by_opentelemetry:
            instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Failed to initialize CrewAI instrumentation: {e}")
        return False


def _init_mcp() -> bool:
    """Initialize MCP instrumentation"""
    if not is_package_installed("mcp"):
        return False
    
    try:
        from opentelemetry.instrumentation.mcp import MCPInstrumentor
        instrumentor = MCPInstrumentor()
        if not instrumentor.is_instrumented_by_opentelemetry:
            instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Failed to initialize MCP instrumentation: {e}")
        return False


def _init_redis() -> bool:
    """Initialize Redis instrumentation"""
    if not is_package_installed("redis"):
        return False
    
    try:
        from opentelemetry.instrumentation.redis import RedisInstrumentor
        instrumentor = RedisInstrumentor()
        if not instrumentor.is_instrumented_by_opentelemetry:
            instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Failed to initialize Redis instrumentation: {e}")
        return False


def _init_requests() -> bool:
    """Initialize Requests instrumentation"""
    if not is_package_installed("requests"):
        return False
    
    try:
        from opentelemetry.instrumentation.requests import RequestsInstrumentor
        instrumentor = RequestsInstrumentor()
        if not instrumentor.is_instrumented_by_opentelemetry:
            instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Failed to initialize Requests instrumentation: {e}")
        return False


def _init_urllib3() -> bool:
    """Initialize urllib3 instrumentation"""
    if not is_package_installed("urllib3"):
        return False
    
    try:
        from opentelemetry.instrumentation.urllib3 import URLLib3Instrumentor
        instrumentor = URLLib3Instrumentor()
        if not instrumentor.is_instrumented_by_opentelemetry:
            instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Failed to initialize urllib3 instrumentation: {e}")
        return False


def _init_pymysql() -> bool:
    """Initialize PyMySQL instrumentation"""
    if not is_package_installed("pymysql"):
        return False
    
    try:
        from opentelemetry.instrumentation.pymysql import PyMySQLInstrumentor
        instrumentor = PyMySQLInstrumentor()
        if not instrumentor.is_instrumented_by_opentelemetry:
            instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Failed to initialize PyMySQL instrumentation: {e}")
        return False 