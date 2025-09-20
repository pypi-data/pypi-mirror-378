"""
Backboard API Python client
"""

import json
import uuid
from typing import Optional, List, Dict, Any, Union, Iterator
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .models import (
    Assistant, Thread, Document, Message, MessageResponse, 
    ToolOutputsResponse, ToolDefinition, ToolOutput
)
from .exceptions import (
    BackboardAPIError, BackboardValidationError, BackboardNotFoundError,
    BackboardRateLimitError, BackboardServerError
)


class BackboardClient:
    """
    Backboard API client for building conversational AI applications
    with persistent memory and intelligent document processing.
    """
    
    def __init__(
        self, 
        api_key: str,
        base_url: str = "https://backboard.io/api",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize the Backboard client
        
        Args:
            api_key: Your Backboard API key
            base_url: API base URL (default: https://backboard.io/api)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retries for failed requests (default: 3)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        
        # Create session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": "backboard-python-sdk/1.0.0"
        })

    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        json_data: Optional[Dict] = None,
        data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        params: Optional[Dict] = None,
        stream: bool = False
    ) -> requests.Response:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # Prepare headers for this request
        headers = {"X-API-Key": self.api_key}
        
        # For form data without files, we need to ensure proper Content-Type
        # When files are present, let requests handle the Content-Type automatically
        if data and not files:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=json_data,
                data=data,
                files=files,
                params=params,
                headers=headers,
                timeout=self.timeout,
                stream=stream
            )
            
            # Handle different error status codes
            if response.status_code >= 400:
                self._handle_error_response(response)
                
            return response
            
        except requests.exceptions.Timeout:
            raise BackboardAPIError("Request timed out")
        except requests.exceptions.ConnectionError:
            raise BackboardAPIError("Connection error")
        except requests.exceptions.RequestException as e:
            raise BackboardAPIError(f"Request failed: {str(e)}")

    def _handle_error_response(self, response: requests.Response):
        """Handle error responses from the API"""
        try:
            error_data = response.json()
            error_message = error_data.get('detail', f"HTTP {response.status_code}")
        except (ValueError, KeyError):
            error_message = f"HTTP {response.status_code}: {response.text}"

        if response.status_code == 400:
            raise BackboardValidationError(error_message, response.status_code, response)
        elif response.status_code == 404:
            raise BackboardNotFoundError(error_message, response.status_code, response)
        elif response.status_code == 429:
            raise BackboardRateLimitError(error_message, response.status_code, response)
        elif response.status_code >= 500:
            raise BackboardServerError(error_message, response.status_code, response)
        else:
            raise BackboardAPIError(error_message, response.status_code, response)

    # Assistant methods
    def create_assistant(
        self, 
        name: str, 
        description: Optional[str] = None,
        tools: Optional[List[Union[ToolDefinition, Dict[str, Any]]]] = None
    ) -> Assistant:
        """
        Create a new assistant
        
        Args:
            name: Name of the assistant
            description: Optional description
            tools: Optional list of tool definitions (can be ToolDefinition objects or dict)
            
        Returns:
            Created Assistant object
        """
        data = {"name": name}
        if description:
            data["description"] = description
        if tools:
            data["tools"] = [self._tool_to_dict(tool) for tool in tools]
            
        response = self._make_request("POST", "/assistants", json_data=data)
        return Assistant.from_dict(response.json())

    def list_assistants(self, skip: int = 0, limit: int = 100) -> List[Assistant]:
        """
        List all assistants
        
        Args:
            skip: Number of assistants to skip
            limit: Maximum number of assistants to return
            
        Returns:
            List of Assistant objects
        """
        params = {"skip": skip, "limit": limit}
        response = self._make_request("GET", "/assistants", params=params)
        return [Assistant.from_dict(data) for data in response.json()]

    def get_assistant(self, assistant_id: Union[str, uuid.UUID]) -> Assistant:
        """
        Get a specific assistant
        
        Args:
            assistant_id: Assistant ID
            
        Returns:
            Assistant object
        """
        response = self._make_request("GET", f"/assistants/{assistant_id}")
        return Assistant.from_dict(response.json())

    def update_assistant(
        self,
        assistant_id: Union[str, uuid.UUID],
        name: Optional[str] = None,
        description: Optional[str] = None,
        tools: Optional[List[Union[ToolDefinition, Dict[str, Any]]]] = None
    ) -> Assistant:
        """
        Update an assistant
        
        Args:
            assistant_id: Assistant ID
            name: New name (optional)
            description: New description (optional)  
            tools: New list of tools (optional, replaces existing)
            
        Returns:
            Updated Assistant object
        """
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if tools is not None:
            data["tools"] = [self._tool_to_dict(tool) for tool in tools]
            
        response = self._make_request("PUT", f"/assistants/{assistant_id}", json_data=data)
        return Assistant.from_dict(response.json())

    def delete_assistant(self, assistant_id: Union[str, uuid.UUID]) -> Dict[str, Any]:
        """
        Delete an assistant
        
        Args:
            assistant_id: Assistant ID
            
        Returns:
            Deletion confirmation
        """
        response = self._make_request("DELETE", f"/assistants/{assistant_id}")
        return response.json()

    # Thread methods
    def create_thread(self, assistant_id: Union[str, uuid.UUID]) -> Thread:
        """
        Create a new thread for an assistant
        
        Args:
            assistant_id: Assistant ID
            
        Returns:
            Created Thread object
        """
        response = self._make_request("POST", f"/assistants/{assistant_id}/threads", json_data={})
        return Thread.from_dict(response.json())

    def list_threads(self, skip: int = 0, limit: int = 100) -> List[Thread]:
        """
        List all threads
        
        Args:
            skip: Number of threads to skip
            limit: Maximum number of threads to return
            
        Returns:
            List of Thread objects
        """
        params = {"skip": skip, "limit": limit}
        response = self._make_request("GET", "/threads", params=params)
        return [Thread.from_dict(data) for data in response.json()]

    def get_thread(self, thread_id: Union[str, uuid.UUID]) -> Thread:
        """
        Get a specific thread with all its messages
        
        Args:
            thread_id: Thread ID
            
        Returns:
            Thread object with messages
        """
        response = self._make_request("GET", f"/threads/{thread_id}")
        return Thread.from_dict(response.json())

    def delete_thread(self, thread_id: Union[str, uuid.UUID]) -> Dict[str, Any]:
        """
        Delete a thread
        
        Args:
            thread_id: Thread ID
            
        Returns:
            Deletion confirmation
        """
        response = self._make_request("DELETE", f"/threads/{thread_id}")
        return response.json()

    def add_message(
        self,
        thread_id: Union[str, uuid.UUID],
        content: Optional[str] = None,
        files: Optional[List[Union[str, Path]]] = None,
        llm_provider: Optional[str] = None,
        model_name: Optional[str] = None,
        stream: bool = False,
        hide_tool_events: bool = True
    ) -> Union[MessageResponse, Iterator[Dict[str, Any]]]:
        """
        Add a message to a thread with optional file attachments
        
        Args:
            thread_id: Thread ID
            content: Message content (optional if files provided)
            files: List of file paths to attach (optional)
            llm_provider: LLM provider (default: openai)
            model_name: Model name (default: gpt-4o)
            stream: Whether to stream the response
            hide_tool_events: Whether to hide tool events in streaming
            
        Returns:
            MessageResponse object or streaming iterator
        """
        # Prepare form data
        form_data = {
            "stream": "true" if stream else "false",
            "hide_tool_events": "true" if hide_tool_events else "false"
        }
        
        if content:
            form_data["content"] = content
        if llm_provider:
            form_data["llm_provider"] = llm_provider
        if model_name:
            form_data["model_name"] = model_name

        # Handle file attachments with direct requests to avoid session issues
        if files:
            import requests
            
            # Prepare files for multipart upload
            files_data = []
            file_handles = []
            try:
                for file_path in files:
                    path = Path(file_path)
                    if not path.exists():
                        raise FileNotFoundError(f"File not found: {file_path}")
                    file_handle = open(path, "rb")
                    file_handles.append(file_handle)
                    files_data.append(("files", (path.name, file_handle, "text/plain")))
                
                # Use direct requests for file uploads
                headers = {"X-API-Key": self.api_key}
                url = f"{self.base_url}/threads/{thread_id}/messages"
                
                if stream:
                    # For streaming with files, we need to handle differently
                    response = requests.post(
                        url,
                        data=form_data,
                        files=files_data,
                        headers=headers,
                        timeout=self.timeout,
                        stream=True
                    )
                    
                    if response.status_code >= 400:
                        self._handle_error_response(response)
                    
                    return self._parse_streaming_response(response)
                else:
                    response = requests.post(
                        url,
                        data=form_data,
                        files=files_data,
                        headers=headers,
                        timeout=self.timeout
                    )
                    
                    if response.status_code >= 400:
                        self._handle_error_response(response)
                    
                    return MessageResponse.from_dict(response.json())
                    
            finally:
                # Always close file handles
                for file_handle in file_handles:
                    file_handle.close()
        else:
            # No files, use regular session request
            response = self._make_request(
                "POST", 
                f"/threads/{thread_id}/messages",
                data=form_data,
                files=None,
                stream=stream
            )
            
            if stream:
                return self._parse_streaming_response(response)
            else:
                return MessageResponse.from_dict(response.json())

    def submit_tool_outputs(
        self,
        thread_id: Union[str, uuid.UUID],
        run_id: str,
        tool_outputs: List[Union[ToolOutput, Dict[str, str]]],
        stream: bool = False
    ) -> Union[ToolOutputsResponse, Iterator[Dict[str, Any]]]:
        """
        Submit tool outputs for a run
        
        Args:
            thread_id: Thread ID
            run_id: Run ID
            tool_outputs: List of tool outputs (can be ToolOutput objects or dicts with 'tool_call_id' and 'output')
            stream: Whether to stream the response
            
        Returns:
            ToolOutputsResponse object or streaming iterator
        """
        # Convert tool outputs to the format expected by the API
        formatted_outputs = []
        for output in tool_outputs:
            if isinstance(output, dict):
                # Already a dict, use as-is
                formatted_outputs.append(output)
            else:
                # ToolOutput object, convert to dict
                formatted_outputs.append({
                    "tool_call_id": output.tool_call_id, 
                    "output": output.output
                })
        
        data = {"tool_outputs": formatted_outputs}
        
        params = {"stream": "true" if stream else "false"}
        
        response = self._make_request(
            "POST",
            f"/threads/{thread_id}/runs/{run_id}/submit-tool-outputs",
            json_data=data,
            params=params,
            stream=stream
        )
        
        if stream:
            return self._parse_streaming_response(response)
        else:
            return ToolOutputsResponse.from_dict(response.json())

    # Document methods
    def upload_document_to_assistant(
        self, 
        assistant_id: Union[str, uuid.UUID],
        file_path: Union[str, Path]
    ) -> Document:
        """
        Upload a document to an assistant
        
        Args:
            assistant_id: Assistant ID
            file_path: Path to the file to upload
            
        Returns:
            Document object
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Use direct requests for file uploads to avoid session issues
        import requests
        with open(path, "rb") as file_handle:
            files = {"file": (path.name, file_handle, "text/plain")}
            headers = {"X-API-Key": self.api_key}
            url = f"{self.base_url}/assistants/{assistant_id}/documents"
            
            response = requests.post(
                url,
                files=files,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code >= 400:
                self._handle_error_response(response)
            
        return Document.from_dict(response.json())

    def upload_document_to_thread(
        self,
        thread_id: Union[str, uuid.UUID], 
        file_path: Union[str, Path]
    ) -> Document:
        """
        Upload a document to a thread
        
        Args:
            thread_id: Thread ID
            file_path: Path to the file to upload
            
        Returns:
            Document object
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Use direct requests for file uploads to avoid session issues
        import requests
        with open(path, "rb") as file_handle:
            files = {"file": (path.name, file_handle, "text/plain")}
            headers = {"X-API-Key": self.api_key}
            url = f"{self.base_url}/threads/{thread_id}/documents"
            
            response = requests.post(
                url,
                files=files,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code >= 400:
                self._handle_error_response(response)
            
        return Document.from_dict(response.json())

    def list_assistant_documents(self, assistant_id: Union[str, uuid.UUID]) -> List[Document]:
        """
        List documents associated with an assistant
        
        Args:
            assistant_id: Assistant ID
            
        Returns:
            List of Document objects
        """
        response = self._make_request("GET", f"/assistants/{assistant_id}/documents")
        return [Document.from_dict(data) for data in response.json()]

    def list_thread_documents(self, thread_id: Union[str, uuid.UUID]) -> List[Document]:
        """
        List documents associated with a thread
        
        Args:
            thread_id: Thread ID
            
        Returns:
            List of Document objects
        """
        response = self._make_request("GET", f"/threads/{thread_id}/documents")
        return [Document.from_dict(data) for data in response.json()]

    def get_document_status(self, document_id: Union[str, uuid.UUID]) -> Document:
        """
        Get document processing status
        
        Args:
            document_id: Document ID
            
        Returns:
            Document object with status information
        """
        response = self._make_request("GET", f"/documents/{document_id}/status")
        return Document.from_dict(response.json())

    def delete_document(self, document_id: Union[str, uuid.UUID]) -> Dict[str, Any]:
        """
        Delete a document
        
        Args:
            document_id: Document ID
            
        Returns:
            Deletion confirmation
        """
        response = self._make_request("DELETE", f"/documents/{document_id}")
        return response.json()

    # Helper methods
    def _tool_to_dict(self, tool: Union[ToolDefinition, Dict[str, Any]]) -> Dict[str, Any]:
        """Convert ToolDefinition object or dict to dictionary for API requests"""
        # If it's already a dict, return as-is (assuming it's properly formatted)
        if isinstance(tool, dict):
            return tool
            
        # Convert ToolDefinition object to dict
        return {
            "type": tool.type,
            "function": {
                "name": tool.function.name,
                "description": tool.function.description,
                "parameters": {
                    "type": tool.function.parameters.type,
                    "properties": {
                        k: {
                            "type": v.type,
                            "description": v.description,
                            "enum": v.enum,
                            "properties": v.properties,
                            "items": v.items
                        }
                        for k, v in (tool.function.parameters.properties or {}).items()
                    },
                    "required": tool.function.parameters.required
                }
            }
        }

    def _parse_streaming_response(self, response: requests.Response) -> Iterator[Dict[str, Any]]:
        """Parse Server-Sent Events streaming response"""
        for line in response.iter_lines(decode_unicode=True):
            if line.startswith("data: "):
                try:
                    data = json.loads(line[6:])  # Remove "data: " prefix
                    yield data
                except json.JSONDecodeError:
                    continue
