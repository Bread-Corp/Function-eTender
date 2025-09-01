# ==================================================================================================
#
# File: eTendersLambda/models.py
#
# Description:
# This module defines the data structures (models) for representing tender information
# sourced specifically from the National Treasury's eTenders portal. It provides a
# structured way to handle, validate, and serialize this specific type of tender data.
#
# Note: This file shares a similar structure with the EskomLambda/models.py, using the
# same base classes (SupportingDoc, TenderBase) to maintain consistency. The key difference
# is the implementation of the `eTender` class, which is tailored to the eTenders API.
#
# The classes defined here are:
#   - SupportingDoc: A simple class to represent a downloadable document linked to a tender.
#   - TenderBase: An abstract base class defining the common interface and core attributes
#     for any tender. This promotes consistency across different tender types.
#   - eTender: A concrete class that inherits from TenderBase and adds fields
#     specific to the data provided by the eTenders API. It includes logic for parsing
#     the raw API response into a clean, usable object.
#
# ==================================================================================================

# Import necessary built-in modules.
# abc (Abstract Base Classes) is used to define the basic structure of a tender.
# datetime is used for handling and formatting date/time information.
# logging is used to record warnings or errors during data parsing.
from abc import ABC, abstractmethod
from datetime import datetime
import logging

# ==================================================================================================
# Class: SupportingDoc
# Purpose: Represents a single supporting document associated with a tender.
# ==================================================================================================
class SupportingDoc:
    """
    A simple data class to hold information about a supporting document.
    This typically includes tender specifications, forms, or other relevant files.
    """
    def __init__(self, name: str, url: str):
        """
        Initializes a new instance of the SupportingDoc class.

        Args:
            name (str): The human-readable name of the document (e.g., "Tender Specifications.pdf").
            url (str): The direct URL where the document can be downloaded.
        """
        # --- Instance Attributes ---
        self.name = name  # The title or filename of the document.
        self.url = url    # The hyperlink to the document.

    def to_dict(self):
        """
        Serializes the SupportingDoc instance into a dictionary format.
        This is useful for converting the object into a JSON string for APIs or storage.

        Returns:
            dict: A dictionary containing the document's name and URL.
        """
        return {"name": self.name, "url": self.url}

# ==================================================================================================
# Class: TenderBase (Abstract Base Class)
# Purpose: Defines the fundamental structure and contract for all tender types.
# ==================================================================================================
class TenderBase(ABC):
    """
    An abstract base class that serves as a template for all specific tender models.
    It defines the common attributes and methods that every tender object must have,
    ensuring a consistent data structure regardless of the data source.
    This class cannot be instantiated directly.
    """
    def __init__(self, title: str, description: str, source: str, published_date: datetime, closing_date: datetime, supporting_docs: list = None, tags: list = None):
        """
        Initializes the base attributes of a tender.

        Args:
            title (str): The official title or headline of the tender.
            description (str): A detailed description of the tender's scope and requirements.
            source (str): The name of the platform where the tender was found (e.g., "eTenders").
            published_date (datetime): The date and time when the tender was officially published.
            closing_date (datetime): The date and time when submissions for the tender are due.
            supporting_docs (list, optional): A list of SupportingDoc objects. Defaults to an empty list.
            tags (list, optional): A list of keywords or categories for the tender. Defaults to an empty list.
                                   This is intentionally left empty to be populated by a downstream AI service.
        """
        # --- Instance Attributes ---
        self.title = title
        self.description = description
        self.source = source
        self.published_date = published_date
        self.closing_date = closing_date
        # If supporting_docs is not provided, initialize as an empty list to prevent errors.
        self.supporting_docs = supporting_docs if supporting_docs is not None else []
        # If tags is not provided, initialize as an empty list. This is the standard behavior
        # as the tags are expected to be added by a separate AI tagging process later.
        self.tags = tags if tags is not None else []

    @classmethod
    @abstractmethod
    def from_api_response(cls, response_item: dict):
        """
        An abstract factory method that must be implemented by all subclasses.
        Its purpose is to create a tender object from a single item (dictionary)
        from a raw API response.

        Args:
            response_item (dict): A dictionary representing one tender from the source API.

        Raises:
            NotImplementedError: If a subclass does not implement this method.
        """
        pass

    def to_dict(self):
        """
        Serializes the common tender attributes into a dictionary.
        This method is intended to be called by subclasses, which will then add their
        own specific fields to the dictionary.

        Returns:
            dict: A dictionary containing the core attributes of the tender.
        """
        return {
            "title": self.title,
            "description": self.description,
            "source": self.source,
            # Convert datetime objects to ISO 8601 format string, handling None values gracefully.
            "publishedDate": self.published_date.isoformat() if self.published_date else None,
            "closingDate": self.closing_date.isoformat() if self.closing_date else None,
            # Serialize each SupportingDoc object in the list.
            "supporting_docs": [doc.to_dict() for doc in self.supporting_docs],
            # Serialize each tag object in the list (if any).
            "tags": [tag.to_dict() for tag in self.tags]
        }


# ==================================================================================================
# Class: eTender
# Purpose: A concrete implementation of TenderBase for eTenders portal tenders.
# ==================================================================================================
class eTender(TenderBase):
    """
    Represents a tender sourced from the eTenders portal. It inherits all the base attributes
    from TenderBase and adds additional fields that are unique to the eTenders API data structure.
    """
    def __init__(
        self,
        # --- Base fields required by TenderBase ---
        title: str, description: str, source: str, published_date: datetime, closing_date: datetime, supporting_docs: list, tags: list,
        # --- Child fields specific to eTender ---
        tender_number: str,
        category: str,
        tender_type: str,
        department: str,
    ):
        """
        Initializes a new eTender instance.

        Args:
            (Inherited): title, description, source, published_date, closing_date, supporting_docs, tags.
            tender_number (str): The unique identifier for the tender from the portal.
            category (str): The category the tender belongs to (e.g., "Construction").
            tender_type (str): The type of tender (e.g., "Request for Proposal").
            department (str): The government department that issued the tender.
        """
        # Call the parent class's __init__ method to set up the common fields.
        super().__init__(title, description, source, published_date, closing_date, supporting_docs, tags)
        # --- eTender-specific Instance Attributes ---
        self.tender_number = tender_number
        self.category = category
        self.tender_type = tender_type
        self.department = department

    @classmethod
    def from_api_response(cls, response_item: dict):
        """
        Factory method to create an eTender object from a raw eTenders API response item.
        This method handles data extraction, cleaning, and validation.

        Args:
            response_item (dict): A dictionary containing a single tender's data from the eTenders API.

        Returns:
            eTender: An instance of the eTender class populated with the API data.
        """
        # --- Date Parsing with Error Handling ---
        pub_date, close_date = None, None
        tender_id = response_item.get('id', 'Unknown')
        try:
            # The eTenders API might use different date field names. Adjust as needed.
            # Example assumes 'datePublished' and 'closingDate' keys.
            pub_date_str = response_item.get('datePublished') # Replace with actual key
            if pub_date_str:
                pub_date = datetime.fromisoformat(pub_date_str)
        except (TypeError, ValueError):
            logging.warning(f"Tender {tender_id} has invalid published date: {response_item.get('datePublished')}")

        try:
            close_date_str = response_item.get('closingDate') # Replace with actual key
            if close_date_str:
                close_date = datetime.fromisoformat(close_date_str)
        except (TypeError, ValueError):
            logging.warning(f"Tender {tender_id} has invalid closing date: {response_item.get('closingDate')}")

        # The eTenders API nests documents. We assume a structure here for demonstration.
        # This logic should be adapted to the actual API response structure.
        doc_list = []
        raw_docs = response_item.get('supportingDocuments', [])
        if isinstance(raw_docs, list):
            for doc in raw_docs:
                if isinstance(doc, dict) and 'name' in doc and 'url' in doc:
                    doc_list.append(SupportingDoc(name=doc['name'], url=doc['url']))

        # Create and return an instance of the eTender class.
        return cls(
            # The description field from the API seems to be used as the title.
            title=response_item.get('description', 'No Title Provided').strip(),
            # A more detailed description might be in another field, or we can reuse the title.
            description=response_item.get('description', 'No Description Provided').strip(),
            source="eTenders",  # Hardcoded source for this class.
            published_date=pub_date,
            closing_date=close_date,
            supporting_docs=doc_list,
            tags=[],  # Initialize tags as an empty list, ready for the AI service.
            tender_number=response_item.get('tenderNo', '').strip(),
            category=response_item.get('categoryName', '').strip(),
            tender_type=response_item.get('tenderType', '').strip(),
            department=response_item.get('departmentName', '').strip()
        )

    def to_dict(self):
        """
        Serializes the eTender object to a dictionary, including both
        base and eTender-specific fields.

        Returns:
            dict: A complete dictionary representation of the eTender.
        """
        # Get the dictionary of base fields from the parent class.
        data = super().to_dict()
        # Add the eTender-specific fields to the dictionary.
        data.update({
            "tenderNumber": self.tender_number,
            "category": self.category,
            "tenderType": self.tender_type,
            "department": self.department
        })
        # Return the final, combined dictionary.
        return data