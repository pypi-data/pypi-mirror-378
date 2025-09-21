"""Resource client classes for Zymmr API client.

This module implements hierarchical client classes for managing Zymmr resources,
following established patterns for API client development with proper session
management and resource representation.
"""

import json
from typing import Any, Dict, List, Optional

from .exceptions import ZymmrValidationError
from .http import HTTPClient
from .models import ResourceList


class BaseResourceClient:
    """Base class for all resource clients."""

    def __init__(self, http_client: HTTPClient, doctype: str):
        """Initialize base resource client.

        Args:
            http_client: HTTP client instance for making requests
            doctype: Frappe DocType name (e.g., 'Project')
        """
        self.http_client = http_client
        self.doctype = doctype

    def list(
        self,
        fields: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit_start: int = 0,
        limit_page_length: int = 20,
        **kwargs
    ) -> ResourceList:
        """Get a list of documents from Frappe.

        Args:
            fields: List of field names to fetch
            filters: Dictionary of filter conditions
            order_by: Field to order by with optional ASC/DESC
            limit_start: Starting offset for pagination
            limit_page_length: Number of records to fetch (max 200)
            **kwargs: Additional parameters

        Returns:
            ResourceList containing the documents
        """
        # Validate inputs
        if limit_page_length > 200:
            raise ZymmrValidationError("limit_page_length cannot exceed 200")
        if limit_start < 0:
            raise ZymmrValidationError("limit_start must be non-negative")

        # Build request parameters
        params: Dict[str, Any] = {
            'limit_start': limit_start,
            'limit_page_length': limit_page_length,
            **kwargs
        }

        # Add fields parameter
        if fields:
            params['fields'] = json.dumps(fields)

        # Add filters parameter
        if filters:
            params['filters'] = json.dumps(filters)

        # Add order_by parameter
        if order_by:
            params['order_by'] = order_by

        # Make API request
        url = f"/api/resource/{self.doctype}"
        response = self.http_client.get(url, params=params)

        # Extract data from response and return as ResourceList
        if isinstance(response, dict) and 'data' in response:
            data = response['data']
        elif isinstance(response, list):
            data = response
        else:
            data = []

        return ResourceList(data)

    def get(self, key: str, fields: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """Get a single document by key.

        Args:
            key: The key of the document
            fields: List of field names to fetch
            **kwargs: Additional parameters

        Returns:
            Dictionary containing the document data
        """
        if not key:
            raise ZymmrValidationError("Document key is required")

        params = {}
        if fields:
            params['fields'] = json.dumps(fields)

        params.update(kwargs)

        url = f"/api/resource/{self.doctype}/"
        params['filters'] = json.dumps({'key': key})
        response = self.http_client.get(url, params=params)

        # Frappe returns the document data directly or in 'data' field
        if isinstance(response, dict):
            return response.get('data', response)

        return response

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new document in Frappe.

        Args:
            data: Dictionary containing the document data

        Returns:
            Dictionary containing the created document data
        """
        if not data or not isinstance(data, dict):
            raise ZymmrValidationError("Data must be a non-empty dictionary")

        url = f"/api/resource/{self.doctype}"
        response = self.http_client.post(url, json=data)

        # Frappe returns the created document data
        if isinstance(response, dict):
            return response.get('data', response)

        return response

    def update(self, name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing document in Frappe.

        Args:
            name: The name/ID of the document to update
            data: Dictionary containing the fields to update

        Returns:
            Dictionary containing the updated document data
        """
        if not name:
            raise ZymmrValidationError("Document name is required")
        if not data or not isinstance(data, dict):
            raise ZymmrValidationError("Data must be a non-empty dictionary")

        url = f"/api/resource/{self.doctype}/{name}"
        response = self.http_client.put(url, json=data)

        # Frappe returns the updated document data
        if isinstance(response, dict):
            return response.get('data', response)

        return response

    def delete(self, name: str) -> bool:
        """Delete a document from Frappe.

        Args:
            name: The name/ID of the document to delete

        Returns:
            True if deletion was successful
        """
        if not name:
            raise ZymmrValidationError("Document name is required")

        url = f"/api/resource/{self.doctype}/{name}"
        self.http_client.delete(url)

        # If no exception was raised, deletion was successful
        return True


class ProjectsClient(BaseResourceClient):
    """Client for managing Project resources.

    This class provides methods for managing projects and follows the
    hierarchical client pattern for accessing nested resources.
    """

    def __init__(self, http_client: HTTPClient):
        """Initialize ProjectsClient.

        Args:
            http_client: HTTP client instance for making requests
        """
        super().__init__(http_client, "Project")

    def get_active(self, fields: Optional[List[str]] = None) -> ResourceList:
        """Get all active projects.

        Args:
            fields: List of field names to fetch

        Returns:
            ResourceList of active projects
        """
        return self.list(
            fields=fields,
            filters={"status": "Active"},
            order_by="title"
        )

    def get_by_user(
        self,
        user_id: str,
        fields: Optional[List[str]] = None
    ) -> ResourceList:
        """Get projects where the user is the lead.

        Args:
            user_id: User ID (as stored in the lead field, e.g., '866d6822-2afd-49fa-8998-b79510f5f802')
            fields: List of field names to fetch

        Returns:
            ResourceList of projects where the user is the lead
        """
        return self.list(
            fields=fields,
            filters={"lead": user_id},
            order_by="creation desc"
        )

    def get_analytics(
        self,
        project_id: str,
        period: str = "last_month"
    ) -> Dict[str, Any]:
        """Get analytics data for a project.

        Args:
            project_id: The project ID/key
            period: Time period for analytics (e.g., 'last_month', 'this_quarter')

        Returns:
            Dictionary containing project analytics
        """
        # This would integrate with analytics endpoints
        # For now, return basic project info
        project = self.get(project_id)
        return {
            "project": project,
            "period": period,
            "message": "Analytics feature to be implemented"
        }
