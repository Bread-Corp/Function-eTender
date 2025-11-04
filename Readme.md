# 🌐 eTenders Processing Lambda Service

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

This section covers three deployment methods for the eTenders Processing Lambda Service. Choose the method that best fits your workflow and infrastructure preferences.

### 🛠️ Prerequisites

Before deploying, ensure you have:
- AWS CLI configured with appropriate credentials 🔑
- AWS SAM CLI installed (`pip install aws-sam-cli`)
- Python 3.13 runtime support in your target region
- Access to AWS Lambda, SQS, and CloudWatch Logs services ☁️
- Required Python dependency: `requests`

### 🎯 Method 1: AWS Toolkit Deployment

Deploy directly through your IDE using the AWS Toolkit extension.

#### Setup Steps:
1. **Install AWS Toolkit** in your IDE (VS Code, IntelliJ, etc.)
2. **Configure AWS Profile** with your credentials
3. **Open Project** containing `lambda_handler.py` and `models.py`

#### Deploy Process:
1. **Right-click** on `lambda_handler.py` in your IDE
2. **Select** "Deploy Lambda Function" from AWS Toolkit menu
3. **Configure Deployment**:
   - Function Name: `eTendersLambda`
   - Runtime: `python3.13`
   - Handler: `lambda_handler.lambda_handler`
   - Memory: `128 MB`
   - Timeout: `120 seconds`
4. **Add Layers** manually after deployment:
   - requests-library layer
5. **Set Environment Variables**:
   ```
   SQS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/211635102441/AIQueue.fifo
   API_TIMEOUT=30
   ```
6. **Configure IAM Permissions** for SQS and CloudWatch Logs

#### Post-Deployment:
- Test the function using the AWS Toolkit test feature
- Monitor logs through CloudWatch integration
- Update function code directly from IDE for quick iterations

### 🚀 Method 2: SAM Deployment

Use AWS SAM for infrastructure-as-code deployment with the provided template.

#### Initial Setup:
```bash
# Install AWS SAM CLI
pip install aws-sam-cli

# Verify installation
sam --version
```

#### Create Required Layer Directory:
Since the template references a layer not included in the repository, create it:

```bash
# Create layer directory
mkdir -p requests-library/python

# Install requests layer
pip install requests -t requests-library/python/
```

#### Build and Deploy:
```bash
# Build the SAM application
sam build

# Deploy with guided configuration (first time)
sam deploy --guided

# Follow the prompts:
# Stack Name: etenders-lambda-stack
# AWS Region: us-east-1 (or your preferred region)
# Parameter SQSQueueURL: https://sqs.us-east-1.amazonaws.com/211635102441/AIQueue.fifo
# Parameter APITimeout: 30
# Confirm changes before deploy: Y
# Allow SAM to create IAM roles: Y
# Save parameters to samconfig.toml: Y
```

#### Environment Variables Setup:
Add these parameters to your SAM template or set them after deployment:

```yaml
# Add to template.yml under eTendersLambda Properties
Environment:
  Variables:
    SQS_QUEUE_URL: https://sqs.us-east-1.amazonaws.com/211635102441/AIQueue.fifo
    API_TIMEOUT: "30"
```

#### Subsequent Deployments:
```bash
# Quick deployment after initial setup
sam build && sam deploy
```

#### Local Testing with SAM:
```bash
# Test function locally with environment variables
sam local invoke eTendersLambda --env-vars env.json

# Create env.json file:
echo '{
  "eTendersLambda": {
    "SQS_QUEUE_URL": "https://sqs.us-east-1.amazonaws.com/211635102441/AIQueue.fifo",
    "API_TIMEOUT": "30"
  }
}' > env.json
```

#### SAM Deployment Advantages:
- ✅ Complete infrastructure management
- ✅ Automatic layer creation and management
- ✅ IAM permissions defined in template
- ✅ Easy rollback capabilities
- ✅ CloudFormation integration

### 🔄 Method 3: Workflow Deployment (CI/CD)

Automated deployment using GitHub Actions workflow for production environments.

#### Setup Requirements:
1. **GitHub Repository Secrets**:
   ```
   AWS_ACCESS_KEY_ID: Your AWS access key
   AWS_SECRET_ACCESS_KEY: Your AWS secret key
   AWS_REGION: us-east-1 (or your target region)
   ```

2. **Pre-existing Lambda Function**: The workflow updates an existing function, so deploy initially using Method 1 or 2.

#### Deployment Process:
1. **Create Release Branch**:
   ```bash
   # Create and switch to release branch
   git checkout -b release
   
   # Make your changes to lambda_handler.py or models.py
   # Commit changes
   git add .
   git commit -m "feat: update eTenders processing logic"
   
   # Push to trigger deployment
   git push origin release
   ```

2. **Automatic Deployment**: The workflow will:
   - Checkout the code
   - Configure AWS credentials
   - Create deployment zip with `lambda_handler.py` and `models.py`
   - Update the existing Lambda function code
   - Maintain existing configuration (layers, environment variables, etc.)

#### Manual Trigger:
You can also trigger deployment manually:
1. Go to **Actions** tab in your GitHub repository
2. Select **"Deploy Python Scraper to AWS"** workflow
3. Click **"Run workflow"**
4. Choose the `release` branch
5. Click **"Run workflow"** button

#### Workflow Deployment Advantages:
- ✅ Automated CI/CD pipeline
- ✅ Consistent deployment process
- ✅ Audit trail of deployments
- ✅ Easy rollback to previous commits
- ✅ No local environment dependencies

### 🔧 Post-Deployment Configuration

Regardless of deployment method, configure the following:

#### Environment Variables:
Set these environment variables in your Lambda function:

```bash
SQS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/211635102441/AIQueue.fifo
API_TIMEOUT=30
USER_AGENT=Mozilla/5.0 (compatible; eTenders-Bot/1.0)
```

#### Via AWS CLI:
```bash
aws lambda update-function-configuration \
    --function-name eTendersLambda \
    --environment Variables='{
        "SQS_QUEUE_URL":"https://sqs.us-east-1.amazonaws.com/211635102441/AIQueue.fifo",
        "API_TIMEOUT":"30",
        "USER_AGENT":"Mozilla/5.0 (compatible; eTenders-Bot/1.0)"
    }'
```

#### CloudWatch Events (Optional):
Set up scheduled execution:
```bash
# Create CloudWatch Events rule for daily execution
aws events put-rule \
    --name "eTendersLambdaSchedule" \
    --schedule-expression "cron(0 9 * * ? *)" \
    --description "Daily eTenders scraping"

# Add Lambda as target
aws events put-targets \
    --rule "eTendersLambdaSchedule" \
    --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:211635102441:function:eTendersLambda"
```

### 🧪 Testing Your Deployment

After deployment, test the function:

```bash
# Test via AWS CLI
aws lambda invoke \
    --function-name eTendersLambda \
    --payload '{}' \
    response.json

# Check the response
cat response.json
```

#### Expected Success Indicators:
- ✅ Function executes without errors
- ✅ CloudWatch logs show successful API calls
- ✅ SQS queue receives tender messages
- ✅ No timeout or memory errors
- ✅ Valid JSON tender data in queue messages
- ✅ MessageGroupId set to "eTenderScrape"

### 🔍 Monitoring and Maintenance

#### CloudWatch Metrics to Monitor:
- **Duration**: Function execution time
- **Error Rate**: Failed invocations
- **Memory Utilization**: RAM usage patterns
- **Throttles**: Concurrent execution limits

#### Log Analysis:
```bash
# View recent logs
aws logs tail /aws/lambda/eTendersLambda --follow

# Search for errors
aws logs filter-log-events \
    --log-group-name /aws/lambda/eTendersLambda \
    --filter-pattern "ERROR"

# Search for successful batches
aws logs filter-log-events \
    --log-group-name /aws/lambda/eTendersLambda \
    --filter-pattern "Successfully sent batch"
```

### 🚨 Troubleshooting Deployments

<details>
<summary><strong>Layer Dependencies Missing</strong></summary>

**Issue**: `requests` import errors

**Solution**: Ensure the requests layer is properly created and attached:
```bash
# For SAM: Verify layer directory exists and contains packages
ls -la requests-library/python/

# For manual deployment: Create and upload layer separately
```
</details>

<details>
<summary><strong>Environment Variables Not Set</strong></summary>

**Issue**: Missing SQS_QUEUE_URL or API_TIMEOUT configuration

**Solution**: Set environment variables using AWS CLI or console:
```bash
aws lambda update-function-configuration \
    --function-name eTendersLambda \
    --environment Variables='{"SQS_QUEUE_URL":"your-queue-url","API_TIMEOUT":"30"}'
```
</details>

<details>
<summary><strong>IAM Permission Errors</strong></summary>

**Issue**: Access denied for SQS or CloudWatch operations

**Solution**: Verify the Lambda execution role has required permissions:
- `sqs:SendMessage`
- `sqs:GetQueueUrl` 
- `sqs:GetQueueAttributes`
- `logs:CreateLogGroup`
- `logs:CreateLogStream`
- `logs:PutLogEvents`
</details>

<details>
<summary><strong>Workflow Deployment Fails</strong></summary>

**Issue**: GitHub Actions workflow errors

**Solution**: Check repository secrets are correctly configured and the target Lambda function exists in AWS.
</details>

<details>
<summary><strong>API Connection Issues</strong></summary>

**Issue**: Cannot connect to eTenders API

**Solution**: Verify the API endpoint is accessible and consider increasing the API_TIMEOUT environment variable.
</details>

Choose the deployment method that best fits your development workflow and infrastructure requirements. SAM deployment is recommended for development environments, while workflow deployment excels for production CI/CD pipelines.

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
