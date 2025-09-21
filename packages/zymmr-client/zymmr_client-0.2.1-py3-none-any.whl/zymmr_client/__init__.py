"""Zymmr Client - Python library for Zymmr Project Management API.

A modern, robust Python client for interacting with Zymmr's REST API,
built on top of Frappe Framework v14.

The client supports two complementary API patterns:

1. **Generic DocType API** (Original) - Direct Frappe DocType access
2. **Resource-Based API** (New) - Hierarchical resource management

Currently implementing Projects resource with more resources to be added.

Example usage - Generic API (still supported):
    ```python
    from zymmr_client import ZymmrClient

    # Initialize client
    client = ZymmrClient(
        base_url="https://zymmr.yourdomain.com",
        username="your-username",
        password="your-password"
    )

    # Get list of projects (generic way)
    projects = client.get_list("Project", fields=["name", "status"])

    # Get specific document
    project = client.get_doc("Project", "PROJ-001")
    ```

Example usage - Resource-Based API (New) - Projects:
    ```python
    from zymmr_client import ZymmrClient

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

__version__ = "0.2.1"
__author__ = "Kiran Harbak"
__email__ = "kiran.harbak@amruts.com"

# Main exports
from .client import ZymmrClient
from .exceptions import (
    ZymmrAPIError,
    ZymmrAuthenticationError,
    ZymmrPermissionError,
    ZymmrNotFoundError,
    ZymmrValidationError,
    ZymmrServerError,
    ZymmrConnectionError,
    ZymmrTimeoutError
)
from .models import (
    Project,
    ResourceList
)
from .resources import (
    ProjectsClient
)

__all__ = [
    # Main client
    "ZymmrClient",

    # Exceptions
    "ZymmrAPIError",
    "ZymmrAuthenticationError",
    "ZymmrPermissionError",
    "ZymmrNotFoundError",
    "ZymmrValidationError",
    "ZymmrServerError",
    "ZymmrConnectionError",
    "ZymmrTimeoutError",

    # Models
    "Project",
    "ResourceList",

    # Resource clients
    "ProjectsClient",
]


def main() -> None:
    """CLI entry point."""
    print(f"Zymmr Client v{__version__}")
    print("Python client library for Zymmr Project Management API")
    print("\nFor usage examples, visit: https://github.com/kiran-harbak/zymmr-client")
