"""
Server Agent for pyprik - FastAPI server providing LLM-powered search endpoints.
"""

import logging
from typing import Dict, Any, List, Optional, Union
import pandas as pd
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .llm_agent import (
    smart_product_search, 
    explain_search_results, 
    conversational_search,
    LLMConfig,
    setup_default_llm,
    get_default_llm_config
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for API
class SearchRequest(BaseModel):
    """Request model for product search."""
    requirements: Dict[str, Any] = Field(..., description="Search requirements as key-value pairs")
    top_n: int = Field(default=5, ge=1, le=50, description="Number of top results to return")
    natural_response: bool = Field(default=True, description="Whether to return natural language response")

class ConversationalSearchRequest(BaseModel):
    """Request model for conversational search."""
    query: str = Field(..., description="Natural language search query")

class ExplainRequest(BaseModel):
    """Request model for explaining search results."""
    requirements: Dict[str, Any] = Field(..., description="Original search requirements")
    
class LLMConfigRequest(BaseModel):
    """Request model for LLM configuration."""
    model: str = Field(default="openai", description="LLM provider (openai or gemini)")
    llm_name: str = Field(default="gpt-3.5-turbo", description="Specific model name")
    api_key: Optional[str] = Field(default=None, description="API key (optional if set in environment)")

class DatasetUploadRequest(BaseModel):
    """Request model for dataset upload."""
    data: List[Dict[str, Any]] = Field(..., description="Dataset as list of dictionaries")

class SearchResponse(BaseModel):
    """Response model for search results."""
    success: bool
    response: Union[str, Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None

# Global dataset storage (in production, use proper database)
_current_dataset: Optional[pd.DataFrame] = None

class PyPrikServerAgent:
    """FastAPI server agent for pyprik LLM functionality."""
    
    def __init__(self, title: str = "PyPrik LLM Server Agent", version: str = "1.0.0"):
        """Initialize the server agent."""
        self.app = FastAPI(
            title=title,
            version=version,
            description="LLM-powered intelligent search server for pyprik"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes."""
        
        @self.app.get("/")
        async def root():
            """Root endpoint with API information."""
            return {
                "message": "PyPrik LLM Server Agent",
                "version": "1.0.0",
                "endpoints": {
                    "POST /search": "Intelligent product search",
                    "POST /conversational-search": "Natural language search",
                    "POST /explain": "Explain search results",
                    "POST /configure-llm": "Configure LLM settings",
                    "POST /upload-dataset": "Upload dataset for searching",
                    "GET /dataset-info": "Get current dataset information",
                    "GET /health": "Health check"
                }
            }
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {"status": "healthy", "llm_configured": get_default_llm_config().client is not None}
        
        @self.app.post("/configure-llm", response_model=Dict[str, Any])
        async def configure_llm_endpoint(config: LLMConfigRequest):
            """Configure LLM settings."""
            try:
                setup_default_llm(config.model, config.llm_name, config.api_key)
                return {
                    "success": True,
                    "message": f"LLM configured: {config.model} - {config.llm_name}",
                    "model": config.model,
                    "llm_name": config.llm_name
                }
            except Exception as e:
                logger.error(f"Error configuring LLM: {e}")
                raise HTTPException(status_code=400, detail=f"Configuration error: {str(e)}")
        
        @self.app.post("/upload-dataset", response_model=Dict[str, Any])
        async def upload_dataset(dataset_request: DatasetUploadRequest):
            """Upload dataset for searching."""
            global _current_dataset
            try:
                _current_dataset = pd.DataFrame(dataset_request.data)
                return {
                    "success": True,
                    "message": f"Dataset uploaded successfully",
                    "rows": len(_current_dataset),
                    "columns": list(_current_dataset.columns)
                }
            except Exception as e:
                logger.error(f"Error uploading dataset: {e}")
                raise HTTPException(status_code=400, detail=f"Dataset upload error: {str(e)}")
        
        @self.app.get("/dataset-info")
        async def get_dataset_info():
            """Get information about current dataset."""
            global _current_dataset
            if _current_dataset is None:
                return {"dataset_loaded": False, "message": "No dataset loaded"}
            
            return {
                "dataset_loaded": True,
                "rows": len(_current_dataset),
                "columns": list(_current_dataset.columns),
                "sample_data": _current_dataset.head(3).to_dict('records')
            }
        
        @self.app.post("/search", response_model=SearchResponse)
        async def search_products(request: SearchRequest):
            """Intelligent product search with optional natural language response."""
            global _current_dataset
            
            if _current_dataset is None:
                raise HTTPException(status_code=400, detail="No dataset loaded. Upload a dataset first.")
            
            try:
                result = smart_product_search(
                    dataset=_current_dataset,
                    requirements=request.requirements,
                    top_n=request.top_n,
                    natural_response=request.natural_response,
                    llm_config=get_default_llm_config()
                )
                
                if isinstance(result, str):
                    # Natural language response
                    return SearchResponse(
                        success=True,
                        response=result,
                        metadata={
                            "type": "natural_language",
                            "requirements": request.requirements,
                            "top_n": request.top_n
                        }
                    )
                else:
                    # DataFrame response
                    return SearchResponse(
                        success=True,
                        response=result.to_dict('records'),
                        metadata={
                            "type": "structured_data",
                            "requirements": request.requirements,
                            "results_count": len(result)
                        }
                    )
                    
            except Exception as e:
                logger.error(f"Error in search: {e}")
                raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")
        
        @self.app.post("/conversational-search", response_model=SearchResponse)
        async def conversational_search_endpoint(request: ConversationalSearchRequest):
            """Natural language conversational search."""
            global _current_dataset
            
            if _current_dataset is None:
                raise HTTPException(status_code=400, detail="No dataset loaded. Upload a dataset first.")
            
            try:
                result = conversational_search(
                    dataset=_current_dataset,
                    user_query=request.query,
                    llm_config=get_default_llm_config()
                )
                
                return SearchResponse(
                    success=True,
                    response=result,
                    metadata={
                        "type": "conversational",
                        "original_query": request.query
                    }
                )
                
            except Exception as e:
                logger.error(f"Error in conversational search: {e}")
                raise HTTPException(status_code=500, detail=f"Conversational search error: {str(e)}")
        
        @self.app.post("/explain", response_model=SearchResponse)
        async def explain_results(request: ExplainRequest):
            """Explain search results in detail."""
            global _current_dataset
            
            if _current_dataset is None:
                raise HTTPException(status_code=400, detail="No dataset loaded. Upload a dataset first.")
            
            try:
                # First get the search results
                from .pyprik import find_top_matching
                results = find_top_matching(_current_dataset, request.requirements, top_n=5)
                
                # Then explain them
                explanation = explain_search_results(
                    dataset=_current_dataset,
                    requirements=request.requirements,
                    results=results,
                    llm_config=get_default_llm_config()
                )
                
                return SearchResponse(
                    success=True,
                    response=explanation,
                    metadata={
                        "type": "explanation",
                        "requirements": request.requirements,
                        "results_analyzed": len(results)
                    }
                )
                
            except Exception as e:
                logger.error(f"Error explaining results: {e}")
                raise HTTPException(status_code=500, detail=f"Explanation error: {str(e)}")

def create_server_agent() -> PyPrikServerAgent:
    """Create and return a server agent instance."""
    return PyPrikServerAgent()

def run_server(host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
    """
    Run the PyPrik LLM server.
    
    Args:
        host: Host address
        port: Port number
        reload: Enable auto-reload for development
    """
    server_agent = create_server_agent()
    
    logger.info(f"Starting PyPrik LLM Server on {host}:{port}")
    uvicorn.run(server_agent.app, host=host, port=port, reload=reload)

if __name__ == "__main__":
    # Example usage
    run_server(reload=True)