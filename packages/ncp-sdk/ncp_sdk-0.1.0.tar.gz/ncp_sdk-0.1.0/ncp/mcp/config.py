"""Configuration for MCP servers."""

from typing import Dict, Optional
from pydantic import BaseModel, Field


class MCPServerConfig(BaseModel):
    """Configuration for connecting to an MCP server.

    Supports remote MCP servers with authentication and custom settings.

    Example:
        # Simple URL configuration
        config = MCPServerConfig(url="http://localhost:3000")

        # Advanced configuration with authentication
        config = MCPServerConfig(
            url="https://secure-mcp.example.com",
            auth_token="your-auth-token",
            timeout=30,
            retry_attempts=3,
            headers={
                "X-API-Version": "v1",
                "Authorization": "Bearer custom-token"
            }
        )
    """

    url: str = Field(..., description="MCP server URL (e.g., 'http://localhost:3000')")
    auth_token: Optional[str] = Field(None, description="Optional authentication token")
    timeout: int = Field(30, description="Request timeout in seconds", ge=1, le=300)
    retry_attempts: int = Field(3, description="Number of retry attempts for failed requests", ge=1, le=10)
    headers: Dict[str, str] = Field(default_factory=dict, description="Additional headers to send with requests")

    model_config = {"extra": "forbid"}

    def to_headers(self) -> Dict[str, str]:
        """Convert configuration to HTTP headers."""
        result_headers = self.headers.copy()

        if self.auth_token:
            # If auth_token is provided but no Authorization header exists, add Bearer token
            if "Authorization" not in result_headers and "authorization" not in result_headers:
                result_headers["Authorization"] = f"Bearer {self.auth_token}"

        return result_headers

    def __str__(self) -> str:
        """String representation."""
        return f"MCPServerConfig(url='{self.url}')"

    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"MCPServerConfig(url='{self.url}', timeout={self.timeout}, "
            f"retry_attempts={self.retry_attempts}, has_auth={bool(self.auth_token)})"
        )