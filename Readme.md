# 🌐 eTenders Processing Lambda Service — National Treasury Scraper

[![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-orange.svg)](https://aws.amazon.com/lambda/)
[![Python 3.9](https://img.shields.io/badge/Python-3.9-blue.svg)](https://www.python.org/)
[![Amazon SQS](https://img.shields.io/badge/AWS-SQS-yellow.svg)](https://aws.amazon.com/sqs/)
[![eTenders API](https://img.shields.io/badge/API-eTenders-green.svg)](https://www.etenders.gov.za/)
[![Pydantic](https://img.shields.io/badge/Validation-Pydantic-red.svg)](https://pydantic.dev/)

**Your gateway to South African government tenders!** 🏛️ This AWS Lambda service is one of the five powerful web scrapers in our comprehensive tender data pipeline. It connects directly to the National Treasury's eTenders portal API, extracting valuable procurement opportunities and feeding them into our intelligent processing system.

## 📚 Table of Contents

- [🎯 Overview](#-overview)
- [⚡ Lambda Function (lambda_handler.py)](#-lambda-function-lambda_handlerpy)
- [📊 Data Model (models.py)](#-data-model-modelspy)
- [🏷️ AI Tagging Initialization](#️-ai-tagging-initialization)
- [📋 Example Tender Data](#-example-tender-data)
- [🚀 Getting Started](#-getting-started)
- [📦 Deployment](#-deployment)
- [🧰 Troubleshooting](#-troubleshooting)

## 🎯 Overview

This service is a crucial component of our multi-source tender aggregation pipeline! 🚀 It specializes in harvesting tender opportunities from the National Treasury's eTenders portal API, ensuring our system captures every government procurement opportunity available to businesses across South Africa.

**What makes it special?** ✨
- 🔄 **Consistent Workflow**: Maintains the same data structure and processing patterns as our other scrapers (Eskom, SANRAL, etc.)
- 🛡️ **Robust Validation**: Uses Pydantic models to ensure data quality and consistency
- 📦 **Intelligent Batching**: Groups tenders efficiently for optimal SQS processing
- 🏷️ **AI-Ready**: Pre-configures every tender for downstream AI tagging and enrichment

## ⚡ Lambda Function (`lambda_handler.py`)

The heart of our scraping operation! 💓 The `lambda_handler` orchestrates the entire data extraction process with military precision:

### 🔄 The Scraping Journey:

1. **🌐 Fetch Data**: Fires off an HTTP GET request to the eTenders paginated API endpoint to retrieve the latest batch of open tenders.

2. **🛡️ Error Handling**: Built like a tank! Handles network hiccups, API timeouts, and response issues with grace, ensuring the function never crashes and burns.

3. **🔍 Data Extraction**: The eTenders API loves to nest things - it wraps the actual tender list within a `data` key. Our function expertly unwraps this gift! 🎁

4. **✅ Data Parsing & Validation**: Each tender runs through our rigorous `eTender` model validation gauntlet. We clean dates, construct proper document URLs, and validate every field. Bad data? It gets logged and left behind! 🗑️

5. **📦 Smart Batching**: Valid tenders are grouped into efficient batches of up to 10 messages - because bulk operations are always better! 

6. **🚀 Queue Dispatch**: Each batch rockets off to the central `AIQueue.fifo` SQS queue with a unique `MessageGroupId` of `eTenderScrape`. This keeps our government tenders organized and separate from other sources while maintaining perfect processing order.

## 📊 Data Model (`models.py`)

Our data architecture is built for consistency and extensibility! 🏗️

### `TenderBase` **(Abstract Foundation)** 🏛️
The bedrock of our tender universe! This abstract class defines the core DNA shared by all tenders:

**🧬 Core Attributes:**
- `title`: The tender's headline - what's it all about?
- `description`: The juicy details and requirements
- `source`: Always "eTenders" for this scraper
- `published_date`: When this opportunity first saw the light of day
- `closing_date`: The deadline - tick tock! ⏰
- `supporting_docs`: Treasure trove of PDF documents and specifications
- `tags`: Keywords for AI magic (starts empty, gets filled by our AI service)

### `eTender` **(Government Specialist)** 🏛️
This powerhouse inherits all the goodness from `TenderBase` and adds government-specific superpowers:

**🎯 eTender-Specific Attributes:**
- `tender_number`: The official government reference (e.g., "SANPC/2025/003")
- `audience`: Which government department is shopping? (e.g., "Strategic Fuel Fund")
- `office_location`: Where the briefing happens (e.g., "Microsoft Teams")
- `email`: Direct line to the procurement team
- `address`: Full physical address constructed from multiple API fields
- `province`: Which province holds the opportunity

## 🏷️ AI Tagging Initialization

We're all about that AI-ready data! 🤖 Every tender that leaves our scraper is perfectly prepped for the downstream AI tagging service:

```python
# From models.py - Setting the stage for AI magic! ✨
return cls(
    # ... other fields
    tags=[],  # Initialize tags as an empty list, ready for the AI service.
    # ... other fields
)
```

This ensures **100% compatibility** with our AI pipeline - every tender object arrives with a clean, empty `tags` field just waiting to be filled with intelligent categorizations! 🧠

## 📋 Example Tender Data

Here's what a real government tender looks like after our scraper works its magic! 🎩✨

```json
{
  "title": "Architectural And Engineering Activities; Technical Testing And Analysis",
  "description": "Rfp To Appoint A Service Provider To Remove The Old Electrical Actuators And Design, Manufacture Deliver, Install And Commission Flameproof Electrical Actuators At The Saldanha Terminal And Oil Jetty (4 Ep/Eb Or Higher)",
  "source": "eTenders",
  "publishedDate": "2025-10-16T00:00:00",
  "closingDate": "2025-11-13T11:00:00",
  "supportingDocs": [
    {
      "name": "Tender Document CIDB-SANPC-2025 -003 Actuators.pdf",
      "url": "https://www.etenders.gov.za/home/Download/?blobName=1e4a2580-804b-45ee-bb0c-038142f1f153.pdf&downloadedFileName=Tender%20Document%20CIDB-SANPC-2025%20-003%20Actuators.pdf"
    }
  ],
  "tags": [],
  "tenderNumber": "SANPC/2025/003",
  "audience": "Strategic Fuel Fund",
  "officeLocation": "Microsoft Teams",
  "email": "sanpcprocurement@sa-npc.co.za",
  "address": "151 Frans Conradie Drive, Parow (Petrosa Building), Parow, Cape Town, 7500",
  "province": "Western Cape"
}
```

**🎯 What this shows:**
- 💰 **High-Value Opportunity**: Engineering services for critical fuel infrastructure
- 🏭 **Industrial Scope**: Electrical actuator replacement at Saldanha Terminal
- 📋 **Complete Documentation**: PDF tender documents readily available
- 🌍 **Location Clarity**: Western Cape, with virtual briefing sessions
- ⏰ **Clear Timeline**: Published Oct 16, closing Nov 13

## 🚀 Getting Started

Ready to dive into government tender scraping? Let's get you set up! 🎉

### 📋 Prerequisites
- AWS CLI configured with appropriate credentials 🔑
- Python 3.9+ with pip 🐍
- Access to AWS Lambda and SQS services ☁️

### 🔧 Local Development
1. **📁 Clone the repository**
2. **📦 Install dependencies**: `pip install -r requirements.txt`
3. **🧪 Run tests**: `python -m pytest`
4. **🔍 Test locally**: Use AWS SAM or similar tools

## 📦 Deployment

### 🚀 Quick Deploy
1. **📁 Package**: Zip your code and dependencies
2. **⬆️ Upload**: Deploy to AWS Lambda
3. **⚙️ Configure**: Set up CloudWatch Events for scheduling
4. **🎯 Test**: Trigger manually to verify operation

### 🔧 Environment Variables
- `SQS_QUEUE_URL`: Target queue for processed tenders
- `API_TIMEOUT`: Request timeout for eTenders API calls

## 🧰 Troubleshooting

### 🚨 Common Issues

<details>
<summary><strong>API Rate Limiting</strong></summary>

**Issue**: Getting HTTP 429 responses from eTenders API.

**Solution**: Implement exponential backoff and respect rate limits. The government APIs are usually generous but not infinite! 🏛️

</details>

<details>
<summary><strong>Data Validation Failures</strong></summary>

**Issue**: Tenders failing Pydantic validation.

**Solution**: Check the API response format - government APIs sometimes change structure. Update the model accordingly! 🔧

</details>

<details>
<summary><strong>SQS Send Failures</strong></summary>

**Issue**: Batches failing to send to SQS.

**Solution**: Check IAM permissions and queue configuration. FIFO queues are picky about message attributes! 📬

</details>

> Built with love, bread, and code by **Bread Corporation** 🦆❤️💻
