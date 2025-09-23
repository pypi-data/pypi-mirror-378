"""Model configuration for NCP SDK agents."""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from ..types import ModelProvider


class ModelConfig(BaseModel):
    """Configuration for LLM models used by agents.
    
    This class provides type-safe configuration for different LLM providers
    and models that can be used by NCP agents.
    
    Example:
        # OpenAI configuration
        config = ModelConfig(
            model="gpt-4-turbo",
            api_key="sk-...",
            temperature=0.7
        )
        
        # Custom/Local model configuration
        config = ModelConfig(
            model="llama-3.3-70b-inst-gptq-4bit",
            api_key="dummy-key",
            base_url="http://localhost:8000/v1/",
            temperature=0.7
        )
    """
    
    model: str = Field(..., description="Model identifier (e.g., 'gpt-4', 'claude-3-opus')")
    api_key: str = Field(..., description="API key for authentication")
    base_url: Optional[str] = Field(None, description="Custom base URL for API endpoints")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int = Field(2048, gt=0, le=100000, description="Maximum tokens to generate")
    top_p: float = Field(1.0, ge=0.0, le=1.0, description="Nucleus sampling parameter")
    
    # Additional provider-specific parameters
    extra_params: Dict[str, Any] = Field(default_factory=dict, description="Provider-specific parameters")
    
    model_config = {"extra": "forbid", "validate_assignment": True}
    
    @validator('model')
    def validate_model(cls, v: str) -> str:
        """Validate model name against known providers."""
        if not v:
            raise ValueError("Model name cannot be empty")
        return v
    
    @validator('api_key') 
    def validate_api_key(cls, v: str) -> str:
        """Validate API key format."""
        if not v:
            raise ValueError("API key cannot be empty")
        return v
    
    @property
    def provider(self) -> Optional[ModelProvider]:
        """Infer provider from model name."""
        model_lower = self.model.lower()
        
        if any(model in model_lower for model in ["gpt", "openai"]):
            return ModelProvider.OPENAI
        elif any(model in model_lower for model in ["claude", "anthropic"]):
            return ModelProvider.ANTHROPIC
        elif any(model in model_lower for model in ["gemini", "bard"]):
            return ModelProvider.GOOGLE
        elif any(model in model_lower for model in ["llama", "llama2", "llama3"]):
            return ModelProvider.LLAMA
        else:
            return ModelProvider.CUSTOM
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = {
            "model": self.model,
            "api_key": self.api_key,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
        }
        
        if self.base_url:
            data["base_url"] = self.base_url
            
        if self.extra_params:
            data.update(self.extra_params)
            
        return data
    
    def to_openai_kwargs(self) -> Dict[str, Any]:
        """Convert to OpenAI client initialization kwargs."""
        kwargs = {"api_key": self.api_key}
        
        if self.base_url:
            kwargs["base_url"] = self.base_url
            
        return kwargs
    
    def to_chat_completion_kwargs(self) -> Dict[str, Any]:
        """Convert to chat completion API kwargs."""
        kwargs = {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
        }
        
        # Add provider-specific parameters
        kwargs.update(self.extra_params)
        
        return kwargs


# Pre-defined configurations for common models
class ModelConfigs:
    """Pre-configured model settings for common use cases."""
    
    @staticmethod
    def openai_gpt4(api_key: str, **kwargs) -> ModelConfig:
        """GPT-4 configuration."""
        return ModelConfig(
            model="gpt-4-turbo",
            api_key=api_key,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 4096),
        )
    
    @staticmethod
    def openai_gpt35(api_key: str, **kwargs) -> ModelConfig:
        """GPT-3.5 Turbo configuration."""
        return ModelConfig(
            model="gpt-3.5-turbo",
            api_key=api_key,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 4096),
        )
    
    @staticmethod
    def claude3_opus(api_key: str, **kwargs) -> ModelConfig:
        """Claude 3 Opus configuration."""
        return ModelConfig(
            model="claude-3-opus-20240229",
            api_key=api_key,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 4096),
        )
    
    @staticmethod
    def local_llama(base_url: str, model: str = "llama-3.3-70b-inst-gptq-4bit", **kwargs) -> ModelConfig:
        """Local Llama model configuration."""
        return ModelConfig(
            model=model,
            api_key="dummy-key",  # Local models don't need real API keys
            base_url=base_url,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2048),
        )