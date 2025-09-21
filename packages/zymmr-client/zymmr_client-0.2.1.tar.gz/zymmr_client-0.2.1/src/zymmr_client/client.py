"""Main Zymmr API client implementation.

Provides the primary ZymmrClient class for interacting with Zymmr's Frappe-based
REST API endpoints.
"""

import json
from typing import Any, Dict, List, Optional

from .auth import FrappeAuth
from .exceptions import ZymmrValidationError
from .http import HTTPClient
from .resources import ProjectsClient


class ZymmrClient:
    """Main client for interacting with Zymmr API.

    This client provides both the original generic DocType API and the new
    resource-based API for maximum flexibility. The resource-based API follows
    modern API client patterns and provides better developer experience.

    The client supports two complementary patterns:

    1. **Generic DocType API** (Original) - Direct Frappe DocType access
    2. **Resource-Based API** (New) - Hierarchical resource management

    Currently implementing Projects resource with more resources to be added.

    Example - Generic API (still supported):
        ```python
        # Initialize client
        client = ZymmrClient(
            base_url="https://zymmr.yourdomain.com",
            username="your-username",
            password="your-password"
        )

        # Get list of projects (generic way)
        projects = client.get_list("Project",
                                  fields=["name", "status", "project_name"],
                                  limit_page_length=10)
        ```

    Example - Resource-Based API (New) - Projects:
        ```python
        # List all projects
        projects = client.projects.list(
            fields=["title", "key", "status"],
            filters={"status": "Active"}
        )

        # Get active projects only
        active_projects = client.projects.get_active()

        # Get projects by user
        my_projects = client.projects.get_by_user("user@example.com")

        # Get specific project
        project = client.projects.get("PROJ-001")

        # Create new project
        new_project = client.projects.create({
            "title": "My New Project",
            "key": "MNP",
            "description": "Project description",
            "lead": "pm@example.com"
        })
        ```
    """

    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        timeout: int = 30,
        max_retries: int = 3,
        debug: bool = False
    ):
        """Initialize Zymmr client.

        Args:
            base_url: Base URL of your Zymmr instance (e.g., 'https://zymmr.yourdomain.com')
            username: Username for authentication
            password: Password for authentication
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum retries for failed requests (default: 3)
            debug: Enable debug logging (default: False)

        Raises:
            ZymmrAuthenticationError: If authentication fails
            ZymmrConnectionError: If unable to connect to server
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.debug = debug

        # Initialize authentication
        self._auth = FrappeAuth(base_url, username, password)

        # Authenticate immediately
        self._auth.authenticate()

        # Initialize HTTP client
        self._http = HTTPClient(
            auth=self._auth,
            timeout=timeout,
            max_retries=max_retries,
            debug=debug
        )

    @property
    def is_authenticated(self) -> bool:
        """Check if client is authenticated."""
        return self._auth.is_authenticated

    @property
    def projects(self) -> ProjectsClient:
        """Get the Projects resource client.

        Returns:
            ProjectsClient instance for managing projects
        """
        if not hasattr(self, '_projects_client'):
            self._projects_client = ProjectsClient(self._http)
        return self._projects_client

    def get_list(
        self,
        doctype: str,
        fields: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit_start: int = 0,
        limit_page_length: int = 20,
        group_by: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get a list of documents from Frappe.

        This method corresponds to Frappe's GET /api/resource/{doctype} endpoint.

        Args:
            doctype: The DocType to fetch (e.g., 'Project', 'Task', 'User')
            fields: List of field names to fetch. If None, fetches all allowed fields
            filters: Dictionary of filter conditions (e.g., {'status': 'Open'})
            order_by: Field to order by with optional ASC/DESC (e.g., 'creation desc')
            limit_start: Starting offset for pagination (default: 0)
            limit_page_length: Number of records to fetch (default: 20, max: 200)
            group_by: Field to group results by

        Returns:
            List of dictionaries containing the document data

        Raises:
            ZymmrValidationError: If parameters are invalid
            ZymmrNotFoundError: If DocType doesn't exist
            ZymmrPermissionError: If user lacks read permissions
            ZymmrAPIError: For other API errors

        Example:
            ```python
            # Basic usage
            projects = client.get_list("Project")

            # With specific fields
            projects = client.get_list("Project", 
                                      fields=["name", "project_name", "status"])

            # With filters
            open_tasks = client.get_list("Task", 
                                        filters={"status": "Open"},
                                        order_by="priority desc",
                                        limit_page_length=50)

            # Complex filters
            filtered_projects = client.get_list("Project", 
                                               filters={
                                                   "status": ["in", ["Active", "On Hold"]],
                                                   "creation": [">", "2023-01-01"]
                                               })
            ```
        """
        # Validate inputs
        if not doctype:
            raise ZymmrValidationError("DocType cannot be empty")

        if limit_page_length > 200:
            raise ZymmrValidationError("limit_page_length cannot exceed 200")

        if limit_start < 0:
            raise ZymmrValidationError("limit_start must be non-negative")

        # Build request parameters
        params: Dict[str, Any] = {
            'limit_start': limit_start,
            'limit_page_length': limit_page_length
        }

        # Add fields parameter
        if fields:
            # Frappe expects fields as JSON string
            params['fields'] = json.dumps(fields)

        # Add filters parameter
        if filters:
            # Frappe expects filters as JSON string
            params['filters'] = json.dumps(filters)

        # Add order_by parameter
        if order_by:
            params['order_by'] = order_by

        # Add group_by parameter
        if group_by:
            params['group_by'] = group_by

        # Make API request
        url = f"/api/resource/{doctype}"

        if self.debug:
            print(f"[DEBUG] Fetching {doctype} with params: {params}")

        response = self._http.get(url, params=params)

        # Extract data from response
        # Frappe typically returns data in the 'data' field
        if isinstance(response, dict) and 'data' in response:
            return response['data']
        elif isinstance(response, list):
            return response
        else:
            # Fallback - return empty list if structure is unexpected
            return []

    def get_doc(self, doctype: str, name: str, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get a single document by name.

        This method corresponds to Frappe's GET /api/resource/{doctype}/{name} endpoint.

        Args:
            doctype: The DocType (e.g., 'Project', 'Task')
            name: The name/ID of the document
            fields: List of field names to fetch. If None, fetches all allowed fields

        Returns:
            Dictionary containing the document data

        Raises:
            ZymmrNotFoundError: If document doesn't exist
            ZymmrPermissionError: If user lacks read permissions
            ZymmrAPIError: For other API errors
        """
        if not doctype or not name:
            raise ZymmrValidationError("Both doctype and name are required")

        params = {}
        if fields:
            params['fields'] = json.dumps(fields)

        url = f"/api/resource/{doctype}/{name}"
        response = self._http.get(url, params=params)

        # Frappe returns the document data directly or in 'data' field
        if isinstance(response, dict):
            return response.get('data', response)

        return response

    def insert(self, doctype: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new document in Frappe.

        This method corresponds to Frappe's POST /api/resource/{doctype} endpoint.

        Args:
            doctype: The DocType to create (e.g., 'Work Item', 'Project')
            data: Dictionary containing the document data

        Returns:
            Dictionary containing the created document data

        Raises:
            ZymmrValidationError: If data is invalid or required fields missing
            ZymmrPermissionError: If user lacks create permissions
            ZymmrAPIError: For other API errors

        Example:
            ```python
            # Create a new work item
            work_item = client.insert("Work Item", {
                "title": "Fix login bug",
                "project": "PROJ-001", 
                "type": "Bug",
                "priority": "High",
                "description": "Users can't login with special characters"
            })

            # Create a new project
            project = client.insert("Project", {
                "title": "New Website",
                "key": "NW",
                "description": "Company website redesign",
                "lead": "john@company.com"
            })
            ```
        """
        if not doctype:
            raise ZymmrValidationError("DocType cannot be empty")

        if not data or not isinstance(data, dict):
            raise ZymmrValidationError("Data must be a non-empty dictionary")

        url = f"/api/resource/{doctype}"

        if self.debug:
            print(f"[DEBUG] Creating {doctype} with data: {data}")

        response = self._http.post(url, json=data)

        # Frappe returns the created document data
        if isinstance(response, dict):
            return response.get('data', response)

        return response

    def update(self, doctype: str, name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing document in Frappe.

        This method corresponds to Frappe's PUT /api/resource/{doctype}/{name} endpoint.

        Args:
            doctype: The DocType (e.g., 'Work Item', 'Project')
            name: The name/ID of the document to update
            data: Dictionary containing the fields to update

        Returns:
            Dictionary containing the updated document data

        Raises:
            ZymmrNotFoundError: If document doesn't exist
            ZymmrValidationError: If data is invalid
            ZymmrPermissionError: If user lacks write permissions
            ZymmrAPIError: For other API errors

        Example:
            ```python
            # Update work item status
            updated_item = client.update("Work Item", "WI-123", {
                "status": "In Progress",
                "assignee": "jane@company.com"
            })

            # Update project end date
            updated_project = client.update("Project", "PROJ-001", {
                "end_date": "2024-12-31",
                "status": "Active"
            })
            ```
        """
        if not doctype or not name:
            raise ZymmrValidationError("Both doctype and name are required")

        if not data or not isinstance(data, dict):
            raise ZymmrValidationError("Data must be a non-empty dictionary")

        url = f"/api/resource/{doctype}/{name}"

        if self.debug:
            print(f"[DEBUG] Updating {doctype} {name} with data: {data}")

        response = self._http.put(url, json=data)

        # Frappe returns the updated document data
        if isinstance(response, dict):
            return response.get('data', response)

        return response

    def delete(self, doctype: str, name: str) -> bool:
        """Delete a document from Frappe.

        This method corresponds to Frappe's DELETE /api/resource/{doctype}/{name} endpoint.

        Args:
            doctype: The DocType (e.g., 'Work Item', 'Project')
            name: The name/ID of the document to delete

        Returns:
            True if deletion was successful

        Raises:
            ZymmrNotFoundError: If document doesn't exist
            ZymmrPermissionError: If user lacks delete permissions
            ZymmrAPIError: For other API errors

        Example:
            ```python
            # Delete a work item
            success = client.delete("Work Item", "WI-123")
            if success:
                print("Work item deleted successfully")

            # Delete a time log
            client.delete("Time Log", "TL-456")
            ```
        """
        if not doctype or not name:
            raise ZymmrValidationError("Both doctype and name are required")

        url = f"/api/resource/{doctype}/{name}"

        if self.debug:
            print(f"[DEBUG] Deleting {doctype} {name}")

        response = self._http.delete(url)

        # Frappe typically returns success message or empty response for deletes
        return True  # If no exception was raised, deletion was successful

    def ping(self) -> bool:
        """Test connection to server.

        Returns:
            True if server is reachable and client is authenticated
        """
        try:
            url = "/api/method/ping"
            response = self._http.get(url)
            return response.get('message') == 'pong'
        except:
            return False

    def get_user_info(self) -> Dict[str, Any]:
        """Get information about the currently logged-in user.

        Returns:
            Dictionary containing user information
        """
        url = "/api/method/frappe.auth.get_logged_user"
        response = self._http.get(url)

        return {
            'username': response.get('message'),
            'full_name': response.get('full_name', ''),
            'email': response.get('email', ''),
            'user_type': response.get('user_type', ''),
            'roles': response.get('roles', [])
        }

    def close(self) -> None:
        """Close the client and logout.

        This method logs out from the server and cleans up resources.
        It's recommended to call this when you're done with the client.
        """
        if hasattr(self, '_auth'):
            self._auth.logout()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - automatically logout."""
        self.close()

    def __repr__(self) -> str:
        """String representation of the client."""
        status = "authenticated" if self.is_authenticated else "not authenticated"
        return f"ZymmrClient(base_url='{self.base_url}', user='{self.username}', {status})"
