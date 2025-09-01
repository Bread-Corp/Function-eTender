# ==================================================================================================
#
# File: eTendersLambda/lambda_handler.py
#
# Description:
# This script contains an AWS Lambda function designed to fetch tender data from the National
# Treasury's eTenders portal API. It processes the raw data, transforms it into a structured
# format using the eTender model, and then sends it to an Amazon SQS (Simple Queue Service)
# queue for further processing.
#
# The function performs the following steps:
# 1. Fetches tender data from the eTenders API endpoint.
# 2. Handles potential network errors or invalid API responses.
# 3. Extracts the list of tenders from the nested 'data' key in the API response.
# 4. Iterates through each tender item.
# 5. Validates and parses each item into a structured eTender object.
# 6. Skips and logs any items that fail validation.
# 7. Converts the processed tender objects into dictionaries.
# 8. Batches the tender data into groups of 10.
# 9. Sends each batch to a specified SQS FIFO queue with a unique MessageGroupId.
# 10. Logs the outcome of the operation.
#
# ==================================================================================================

# --- Import necessary libraries ---
import json         # For serializing Python dictionaries to JSON strings.
import requests     # For making HTTP requests to the eTenders API.
import logging      # For logging information and errors.
import boto3        # The AWS SDK for Python, used to interact with SQS.
from models import eTender  # Import the data model for eTenders.

# --- Global Constants and Configuration ---
# The URL for the eTenders portal's paginated API.
# Parameters like 'length=100' request 100 tenders per page, and 'status=1' filters for open tenders.
ETENDERS_API_URL = "https://www.etenders.gov.za/Home/PaginatedTenderOpportunities?draw=1&length=100&status=1"

# HTTP headers to mimic a web browser.
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json',
}

# --- Logger Setup ---
# Get the default Lambda logger instance.
logger = logging.getLogger()
# Set the logging level to INFO.
logger.setLevel(logging.INFO)

# --- AWS Service Client Initialization ---
# Create a boto3 client to interact with the SQS service.
sqs_client = boto3.client('sqs')
# The URL of the target SQS FIFO queue. This is the same queue used by the Eskom lambda,
# allowing a single downstream service to process tenders from multiple sources.
SQS_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/211635102441/AIQueue.fifo'

# ==================================================================================================
# Lambda Function Handler
# This is the main entry point for the AWS Lambda execution.
# ==================================================================================================
def lambda_handler(event, context):
    """
    The main handler function for the AWS Lambda.

    Args:
        event (dict): The event data passed to the Lambda function.
        context (object): The runtime information of the Lambda function.

    Returns:
        dict: A dictionary containing the HTTP status code and a JSON-formatted body.
    """
    logger.info("Starting eTenders processing job.")

    # --- Step 1: Fetch Data from the eTenders API ---
    try:
        logger.info(f"Fetching data from {ETENDERS_API_URL}")
        # Make a GET request to the API with a 30-second timeout.
        response = requests.get(ETENDERS_API_URL, headers=HEADERS, timeout=30)
        # Check for HTTP errors.
        response.raise_for_status()
        # Parse the JSON response.
        api_response = response.json()
        # The actual tender data is nested within the 'data' key of the response object.
        # .get('data', []) provides a default empty list if the 'data' key is missing.
        api_data = api_response.get('data', [])
        logger.info(f"Successfully fetched {len(api_data)} tender items from the API.")
    except requests.exceptions.RequestException as e:
        # Handle network-related errors.
        logger.error(f"Failed to fetch data from API: {e}")
        return {'statusCode': 502, 'body': json.dumps({'error': 'Failed to fetch data from source API'})}
    except json.JSONDecodeError:
        # Handle cases where the response is not valid JSON.
        logger.error(f"Failed to decode JSON from API response. Response text: {response.text}")
        return {'statusCode': 502, 'body': json.dumps({'error': 'Invalid JSON response from source API'})}

    # --- Step 2: Process and Validate Each Tender Item ---
    processed_tenders = []  # A list to store successfully processed eTender objects.
    skipped_count = 0       # A counter for tenders that failed processing.

    # Loop through each item received from the API.
    for item in api_data:
        try:
            # Use the model's factory method to parse the raw dictionary.
            tender_object = eTender.from_api_response(item)
            # Add the structured object to our list.
            processed_tenders.append(tender_object)
        except (KeyError, ValueError, TypeError) as e:
            # Catch parsing or validation errors.
            skipped_count += 1
            tender_id = item.get('id', 'Unknown')
            logger.warning(f"Skipping tender {tender_id} due to a validation/parsing error: {e}")
            continue

    logger.info(f"Successfully processed {len(processed_tenders)} tenders.")
    if skipped_count > 0:
        logger.warning(f"Skipped a total of {skipped_count} tenders due to errors.")

    # --- Step 3: Prepare Data for SQS ---
    # Convert the list of eTender objects into a list of dictionaries.
    processed_tender_dicts = [tender.to_dict() for tender in processed_tenders]

    # --- Step 4: Batch and Send Messages to SQS ---
    batch_size = 10
    message_batches = [
        processed_tender_dicts[i:i + batch_size]
        for i in range(0, len(processed_tender_dicts), batch_size)
    ]

    sent_count = 0
    # Enumerate to get both the index and the batch, useful for creating unique message IDs.
    for batch_index, batch in enumerate(message_batches):
        entries = []
        for i, tender_dict in enumerate(batch):
            entries.append({
                # Create a more robust unique ID within the batch.
                'Id': f'tender_message_{batch_index}_{i}',
                'MessageBody': json.dumps(tender_dict),
                # Use a different MessageGroupId to distinguish these messages from Eskom tenders in the FIFO queue.
                'MessageGroupId': 'eTenderScrape'
            })

        # If a batch is somehow empty, skip to the next one.
        if not entries:
            continue

        # Send the batch to SQS.
        try:
            response = sqs_client.send_message_batch(
                QueueUrl=SQS_QUEUE_URL,
                Entries=entries
            )
            sent_count += len(response.get('Successful', []))
            logger.info(f"Successfully sent a batch of {len(entries)} messages to SQS.")
            # Check for and log any messages that failed to send within a successful batch call.
            if 'Failed' in response and response['Failed']:
                logger.error(f"Failed to send some messages in a batch: {response['Failed']}")
        except Exception as e:
            logger.error(f"Failed to send a message batch to SQS: {e}")

    logger.info(f"Processing complete. Sent a total of {sent_count} messages to SQS.")

    # --- Step 5: Return a Success Response ---
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Tender data processed and sent to SQS queue.'})
    }