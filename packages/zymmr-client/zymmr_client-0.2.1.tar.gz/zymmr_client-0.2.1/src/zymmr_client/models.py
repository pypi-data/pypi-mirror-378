"""Resource model classes for Zymmr API client.

This module defines model classes that represent resources transferred to and from
the Zymmr API, following established patterns for API client development.
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional


class BaseModel:
    """Base model class for all Zymmr resources."""

    def __init__(self, data: Dict[str, Any]):
        """Initialize model from API response data."""
        self._data = data
        self._parse_data(data)

    def _parse_data(self, data: Dict[str, Any]):
        """Parse API response data into model attributes."""
        for key, value in data.items():
            setattr(self, key, value)

    def to_dict(self) -> Dict[str, Any]:
        """Convert model back to dictionary."""
        return self._data.copy()

    def __repr__(self) -> str:
        """String representation of the model."""
        return f"{self.__class__.__name__}(id={getattr(self, 'name', 'N/A')})"


class Project(BaseModel):
    """Model representing a Zymmr Project.

    This class represents a project entity with all its associated fields
    as defined in the Frappe DocType schema.
    """

    def __init__(self, data: Dict[str, Any]):
        """Initialize Project model from API response."""
        super().__init__(data)

    @property
    def project_id(self) -> str:
        """Get the project ID/key."""
        return getattr(self, 'key', '')

    @property
    def title(self) -> str:
        """Get the project title."""
        return getattr(self, 'title', '')

    @property
    def status(self) -> str:
        """Get the project status."""
        return getattr(self, 'status', '')

    @property
    def lead(self) -> str:
        """Get the project lead."""
        return getattr(self, 'lead', '')

    @property
    def description(self) -> str:
        """Get the project description."""
        return getattr(self, 'description', '')

    @property
    def start_date(self) -> Optional[date]:
        """Get the project start date."""
        date_str = getattr(self, 'start_date', None)
        if date_str:
            return datetime.fromisoformat(date_str).date()
        return None

    @property
    def end_date(self) -> Optional[date]:
        """Get the project end date."""
        date_str = getattr(self, 'end_date', None)
        if date_str:
            return datetime.fromisoformat(date_str).date()
        return None

    @property
    def is_active(self) -> bool:
        """Check if project is active."""
        return self.status.lower() == 'active'


class ResourceList(list):
    """A list of resources with additional metadata."""

    def __init__(self, data: List[Dict[str, Any]], model_class=None):
        """Initialize resource list from API response."""
        super().__init__()
        self.model_class = model_class
        if model_class:
            for item in data:
                self.append(model_class(item))
        else:
            self.extend(data)

    def first(self):
        """Get the first item in the list."""
        return self[0] if self else None

    def last(self):
        """Get the last item in the list."""
        return self[-1] if self else None

    def filter(self, **conditions):
        """Filter the list by conditions."""
        result = []
        for item in self:
            match = True
            for key, value in conditions.items():
                if getattr(item, key, None) != value:
                    match = False
                    break
            if match:
                result.append(item)
        return ResourceList(result, self.model_class)
