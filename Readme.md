# eTenders Processing Lambda Service
## 1. Overview
This service contains an AWS Lambda function responsible for scraping tender information from the National Treasury's eTenders portal API. Its function is analogous to the Eskom service: it fetches raw tender data, validates it against a specific data model, and sends it to an Amazon SQS queue for further processing.

This service allows the data pipeline to ingest tenders from multiple sources while maintaining a consistent workflow and data structure.

## 2. Lambda Function (`lambda_handler.py`)
The `lambda_handler` is the main entry point for this service. It performs the following steps:
1. **Fetch Data**: It sends an HTTP GET request to the eTenders paginated API endpoint to retrieve a list of open tenders.
2. **Error Handling**: It handles potential network errors and API response issues, ensuring the function fails gracefully.
3. **Data Extraction**: The eTenders API nests the actual list of tenders within a `data` key in the main JSON response. The function safely extracts this list.
4. **Data Parsing & Validation**: It iterates through each tender in the list. Each item is processed using the `eTender` model, which cleans and validates the data (e.g., parsing dates, constructing document URLs). Tenders that fail validation are skipped and logged.
5. **Batching**: Valid tenders are grouped into batches of up to 10 messages for efficient sending to SQS.
6. **Queueing**: Each batch is sent to the central `AIQueue.fifo` SQS queue. To distinguish these tenders from Eskom's, a unique `MessageGroupId` of `eTenderScrape` is assigned. This allows the FIFO queue to process groups of tenders from different sources independently while maintaining order within each group.

## 3. Data Model (`models.py`)
This service uses a data model consistent with the Eskom service, relying on the same abstract base class for structure.

`TenderBase` **(Abstract Class)**
This is the same foundational class used in the Eskom service, defining the core attributes common to all tenders:
- Core Attributes: `title`, `description`, `source`, `published_date`, `closing_date`, `supporting_docs`, `tags`.

`eTender` **(Concrete Class)**
This class inherits from `TenderBase` and adds fields specific to the data provided by the eTenders API.
- **Inherited Attributes**: All attributes from TenderBase.
- **eTender-Specific Attributes**:
    - `tender_number`: The unique tender number from the portal.
    - `category`: The category of the tender (e.g., "Civil Engineering").
    - `tender_type`: The type of procurement (e.g., "Request for Bid").
    - `department`: The government department issuing the tender.

## AI Tagging Initialization
As with the Eskom service, the `eTender` model explicitly handles the `tags` attribute. In the `from_api_response` method, the `tags` field is **always initialized to an empty list ([])**.

```
# From models.py
return cls(
    # ... other fields
    tags=[],  # Initialize tags as an empty list, ready for the AI service.
    # ... other fields
)
```

This design ensures that every tender object sent to the SQS queue has a `tags` field, even though the source API does not provide this information. This creates a uniform data contract for the downstream AI tagging service, which can then reliably access the `tags` list and populate it with relevant keywords.