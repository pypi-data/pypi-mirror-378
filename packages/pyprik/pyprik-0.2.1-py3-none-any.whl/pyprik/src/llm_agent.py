"""
LLM Agent module for pyprik - provides natural language responses for data matching tasks.
Integrates with the existing pyprik functionality to create intelligent, conversational responses.
"""

import os
import logging
from typing import Dict, Any, Optional, Union
import pandas as pd
from .pyprik import find_top_matching, find_matching

# Configure logging
logger = logging.getLogger(__name__)

class LLMConfig:
    """Configuration class for LLM settings."""
    
    def __init__(self, model: str = "openai", llm_name: str = "gpt-3.5-turbo", api_key: str = None):
        """
        Initialize LLM configuration.
        
        Args:
            model: LLM provider ("openai" or "gemini")
            llm_name: Specific model name
            api_key: API key (if None, will try to get from environment)
        """
        self.model = model.lower()
        self.llm_name = llm_name
        self.api_key = api_key or self._get_api_key_from_env()
        self.client = None
        self._initialize_client()
    
    def _get_api_key_from_env(self) -> Optional[str]:
        """Get API key from environment variables."""
        if self.model == "openai":
            return os.getenv("OPENAI_API_KEY")
        elif self.model == "gemini":
            return os.getenv("GEMINI_API_KEY")
        return None
    
    def _initialize_client(self):
        """Initialize the LLM client."""
        if not self.api_key:
            logger.warning(f"No API key found for {self.model}. Set environment variable.")
            return
        
        try:
            if self.model == "openai":
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
            elif self.model == "gemini":
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(self.llm_name)
            logger.info(f"LLM client initialized: {self.model} - {self.llm_name}")
        except ImportError as e:
            logger.error(f"Failed to import {self.model} library: {e}")
        except Exception as e:
            logger.error(f"Failed to initialize {self.model} client: {e}")

class PyPrikLLMAgent:
    """
    LLM Agent for pyprik that provides natural language responses for data matching tasks.
    """
    
    def __init__(self, llm_config: LLMConfig = None):
        """
        Initialize the PyPrik LLM Agent.
        
        Args:
            llm_config: LLM configuration object
        """
        self.llm_config = llm_config or LLMConfig()
        
    def generate_response(self, prompt: str, context_data: Dict[str, Any]) -> str:
        """
        Generate natural language response using LLM.
        
        Args:
            prompt: Instructions for the LLM
            context_data: Context data including search results
            
        Returns:
            Generated response string
        """
        if not self.llm_config.client:
            return "LLM not configured. Please set up API keys."
        
        try:
            full_prompt = self._prepare_prompt(prompt, context_data)
            
            if self.llm_config.model == "openai":
                response = self.llm_config.client.chat.completions.create(
                    model=self.llm_config.llm_name,
                    messages=[{"role": "user", "content": full_prompt}],
                    max_tokens=500,
                    temperature=0.7
                )
                return response.choices[0].message.content
            
            elif self.llm_config.model == "gemini":
                response = self.llm_config.client.generate_content(full_prompt)
                return response.text if response.text else "No response generated."
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return f"Error generating response: {str(e)}"
    
    def _prepare_prompt(self, prompt: str, context_data: Dict[str, Any]) -> str:
        """Prepare the full prompt with context data."""
        context_str = f"Search Context:\n"
        
        if 'requirements' in context_data:
            context_str += f"User Requirements: {context_data['requirements']}\n"
        
        if 'results' in context_data:
            results_df = context_data['results']
            if isinstance(results_df, pd.DataFrame) and not results_df.empty:
                context_str += f"Search Results:\n{results_df.to_string()}\n"
        
        if 'dataset_info' in context_data:
            context_str += f"Dataset Info: {context_data['dataset_info']}\n"
        
        full_prompt = f"{context_str}\nInstructions: {prompt}\n\nPlease provide a helpful, natural language response."
        return full_prompt

def smart_product_search(dataset: pd.DataFrame, requirements: Dict[str, Any], 
                        top_n: int = 5, natural_response: bool = True,
                        llm_config: LLMConfig = None) -> Union[pd.DataFrame, str]:
    """
    Enhanced product search with natural language response capability.
    
    Args:
        dataset: DataFrame containing product data
        requirements: Dictionary of search requirements
        top_n: Number of top results to return
        natural_response: Whether to return natural language response
        llm_config: LLM configuration
        
    Returns:
        DataFrame of results or natural language string response
    """
    # Perform the core pyprik search
    results = find_top_matching(dataset, requirements, top_n)
    
    if not natural_response:
        return results
    
    # Generate natural language response
    agent = PyPrikLLMAgent(llm_config)
    
    prompt = """
    You are a helpful product search assistant. Based on the search results provided:
    1. Summarize what the user was looking for
    2. Present the top matching products in a conversational way
    3. Highlight key features and why these products match
    4. If no perfect matches, explain what alternatives were found
    5. Keep the response friendly and informative
    """
    
    context_data = {
        'requirements': requirements,
        'results': results,
        'dataset_info': f"Searched through {len(dataset)} products"
    }
    
    return agent.generate_response(prompt, context_data)

def explain_search_results(dataset: pd.DataFrame, requirements: Dict[str, Any], 
                          results: pd.DataFrame, llm_config: LLMConfig = None) -> str:
    """
    Generate detailed explanation of search results.
    
    Args:
        dataset: Original dataset
        requirements: Search requirements
        results: Search results
        llm_config: LLM configuration
        
    Returns:
        Natural language explanation
    """
    agent = PyPrikLLMAgent(llm_config)
    
    prompt = """
    You are a data analysis expert. Explain the search results in detail:
    1. What criteria were used for matching
    2. How well each result matches the requirements
    3. What makes the top results stand out
    4. Any patterns or insights from the matching process
    5. Suggestions for refining the search if needed
    """
    
    context_data = {
        'requirements': requirements,
        'results': results,
        'dataset_info': f"Dataset contains {len(dataset)} items with columns: {list(dataset.columns)}"
    }
    
    return agent.generate_response(prompt, context_data)

def conversational_search(dataset: pd.DataFrame, user_query: str, 
                         llm_config: LLMConfig = None) -> str:
    """
    Perform conversational search where user provides natural language query.
    
    Args:
        dataset: DataFrame to search
        user_query: Natural language search query
        llm_config: LLM configuration
        
    Returns:
        Natural language response with search results
    """
    agent = PyPrikLLMAgent(llm_config)
    
    # First, extract requirements from natural language
    extraction_prompt = f"""
    Extract search requirements from this user query: "{user_query}"
    
    Based on the dataset columns: {list(dataset.columns)}
    
    Return a Python dictionary format like: {{"column_name": "value", "another_column": "value"}}
    Only include columns that exist in the dataset and values that make sense.
    If you can't extract clear requirements, return an empty dictionary.
    
    Just return the dictionary, nothing else.
    """
    
    context_data = {
        'user_query': user_query,
        'dataset_info': f"Dataset has {len(dataset)} rows and columns: {list(dataset.columns)}"
    }
    
    try:
        # Extract requirements
        requirements_str = agent.generate_response(extraction_prompt, context_data)
        
        # Try to parse the requirements (basic parsing)
        requirements = {}
        if '{' in requirements_str and '}' in requirements_str:
            # Extract dictionary-like content
            dict_part = requirements_str[requirements_str.find('{'):requirements_str.rfind('}')+1]
            try:
                requirements = eval(dict_part)  # Note: In production, use ast.literal_eval
            except:
                logger.warning("Could not parse extracted requirements")
        
        if not requirements:
            return f"I couldn't understand your search query: '{user_query}'. Please try being more specific about what you're looking for."
        
        # Perform search with extracted requirements
        return smart_product_search(dataset, requirements, top_n=3, 
                                  natural_response=True, llm_config=llm_config)
        
    except Exception as e:
        logger.error(f"Error in conversational search: {e}")
        return f"Sorry, I encountered an error processing your query: {str(e)}"

# Default configuration instance
_default_llm_config = None

def setup_default_llm(model: str = "openai", llm_name: str = "gpt-3.5-turbo", api_key: str = None):
    """
    Setup default LLM configuration for the module.
    
    Args:
        model: LLM provider ("openai" or "gemini")
        llm_name: Specific model name
        api_key: API key (optional, will use environment variables)
    """
    global _default_llm_config
    _default_llm_config = LLMConfig(model, llm_name, api_key)
    logger.info(f"Default LLM configured: {model} - {llm_name}")

def get_default_llm_config() -> LLMConfig:
    """Get the default LLM configuration."""
    global _default_llm_config
    if _default_llm_config is None:
        _default_llm_config = LLMConfig()
    return _default_llm_config