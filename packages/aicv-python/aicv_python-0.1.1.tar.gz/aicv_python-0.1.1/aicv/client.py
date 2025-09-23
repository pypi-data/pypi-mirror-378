"""
AiCV Python SDK Client

Main client class for interacting with the AiCV API.
"""

import httpx
from typing import Optional, Dict, Any, Union
from .exceptions import AiCVError, AuthenticationError, APIError, ValidationError


class AiCVClient:
    """
    Main client for interacting with the AiCV API.
    
    This client provides methods to analyze CVs, generate content,
    and interact with various AI-powered features.
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.aicv.chat",
        timeout: float = 30.0,
        **kwargs
    ):
        """
        Initialize the AiCV client.
        
        Args:
            api_key: Your AiCV API key
            base_url: Base URL for the API (default: https://api.aicv.chat)
            timeout: Request timeout in seconds (default: 30.0)
            **kwargs: Additional arguments passed to httpx.Client
        """
        if not api_key:
            raise ValidationError("API key is required")
        
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        
        # Set up default headers
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"aicv-python/{__import__('aicv').__version__}"
        }
        
        # Create httpx client
        self.client = httpx.Client(
            base_url=self.base_url,
            headers=headers,
            timeout=timeout,
            **kwargs
        )
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def close(self):
        """Close the HTTP client."""
        if hasattr(self, 'client'):
            self.client.close()
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            **kwargs: Additional arguments for httpx
            
        Returns:
            Response data as dictionary
            
        Raises:
            AuthenticationError: If authentication fails
            APIError: If API returns an error
            AiCVError: For other client errors
        """
        try:
            response = self.client.request(
                method=method,
                url=endpoint,
                json=data,
                params=params,
                **kwargs
            )
            
            # Handle authentication errors
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key or authentication failed")
            
            # Handle other HTTP errors
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    error_message = error_data.get('message', f'HTTP {response.status_code} error')
                except:
                    error_message = f'HTTP {response.status_code} error'
                raise APIError(error_message, status_code=response.status_code)
            
            # Return JSON response
            return response.json()
            
        except httpx.RequestError as e:
            raise AiCVError(f"Request failed: {str(e)}")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid API key or authentication failed")
            raise APIError(f"HTTP {e.response.status_code} error: {e.response.text}")
    
    def analyze_cv(self, cv_text: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Analyze a CV and provide insights.
        
        Args:
            cv_text: The CV text to analyze
            analysis_type: Type of analysis ('comprehensive', 'skills', 'experience')
            
        Returns:
            Analysis results as dictionary
        """
        if not cv_text.strip():
            raise ValidationError("CV text cannot be empty")
        
        data = {
            "cv_text": cv_text,
            "analysis_type": analysis_type
        }
        
        return self._make_request("POST", "/api/v1/analyze", data=data)
    
    def generate_cv_section(
        self,
        section_type: str,
        context: str,
        requirements: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a specific CV section.
        
        Args:
            section_type: Type of section ('summary', 'experience', 'skills', 'education')
            context: Context information for generation
            requirements: Specific requirements for the section
            
        Returns:
            Generated content as dictionary
        """
        if not section_type or not context:
            raise ValidationError("Section type and context are required")
        
        data = {
            "section_type": section_type,
            "context": context,
            "requirements": requirements
        }
        
        return self._make_request("POST", "/api/v1/generate", data=data)
    
    def optimize_cv(self, cv_text: str, target_job: Optional[str] = None) -> Dict[str, Any]:
        """
        Optimize a CV for better ATS compatibility and impact.
        
        Args:
            cv_text: The CV text to optimize
            target_job: Target job description for optimization
            
        Returns:
            Optimization suggestions as dictionary
        """
        if not cv_text.strip():
            raise ValidationError("CV text cannot be empty")
        
        data = {
            "cv_text": cv_text,
            "target_job": target_job
        }
        
        return self._make_request("POST", "/api/v1/optimize", data=data)
    
    def get_account_info(self) -> Dict[str, Any]:
        """
        Get account information and usage statistics.
        
        Returns:
            Account information as dictionary
        """
        return self._make_request("GET", "/api/v1/account")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check API health status.
        
        Returns:
            Health status as dictionary
        """
        return self._make_request("GET", "/api/v1/health")
