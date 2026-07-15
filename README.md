# GCP API to BigQuery Incremental Pipeline

A production-style data engineering project that extracts customer-review data from an external REST API, loads it into Google BigQuery, and creates an analytics-ready curated table.

## Overview

Many businesses use external platforms to collect customer reviews, feedback and ratings. Although this information is valuable, analysts cannot always access it easily or combine it with internal business data.

This project demonstrates how to build an automated data pipeline that retrieves review data from a REST API and loads it into Google BigQuery.

The pipeline supports:

* Historical backfills
* Daily incremental ingestion
* Cursor-based API pagination
* API retry and rate-limit handling
* Raw and curated BigQuery data layers
* Duplicate prevention using an idempotent MERGE
* Secure handling of API credentials
* Automated execution using Cloud Scheduler and Cloud Run

The final curated table is designed to be consumed by analysts, reporting tools and downstream machine-learning or natural-language-processing workflows.

## Business Problem

A customer-experience team collects product and service reviews through an external review platform.

The reviews contain useful information such as:

* Review text
* Customer rating
* Review date
* Customer reference
* Order reference

However, the data remains inside the external platform and is not readily available to analysts.

The business requires an automated solution that:

1. Retrieves historical review data.
2. Collects new reviews every morning.
3. Avoids inserting duplicate records.
4. Stores an unchanged copy of the source data.
5. Creates a clean analytics-ready table.
6. Handles temporary API failures and rate limits.
7. Makes the data available in BigQuery for reporting and analysis.

## Architecture

The production-style architecture is:

```text
Cloud Scheduler
       │
       ▼
Cloud Run
       │
       ▼
Python ETL application
       │
       ▼
External reviews API
       │
       ▼
BigQuery raw table
       │
       ▼
BigQuery MERGE operation
       │
       ▼
BigQuery curated table
       │
       ▼
BI dashboards, analytics and NLP workloads
```

Cloud Scheduler starts the pipeline each morning.

Cloud Run executes the containerised Python application.

The Python application requests review data from the external API, normalises the response and loads it into BigQuery.

The raw table stores the ingested records, while the curated table contains the latest deduplicated version of each review.

## Features

### Historical backfill

The pipeline can retrieve all available historical reviews from the API.

This mode is normally used when the pipeline is deployed for the first time.

### Incremental ingestion

The pipeline reads the most recent review timestamp already stored in the curated table.

It then requests only reviews posted after that timestamp.

This reduces unnecessary API requests and avoids reprocessing the entire review history every morning.

### Cursor-based pagination

The external API may return only a limited number of records in each response.

The pipeline follows the API's cursor until all available pages have been retrieved.

### Retry handling

Temporary failures can happen when calling an external API.

The pipeline retries requests when it receives:

* HTTP 429 rate-limit responses
* HTTP 5xx server errors
* Temporary network failures

Exponential backoff is used to avoid repeatedly sending requests too quickly.

### Raw and curated tables

The project uses two BigQuery tables.

The raw table stores the records received during ingestion.

The curated table stores the latest deduplicated version of every review.

### Idempotent loading

The pipeline uses a BigQuery `MERGE` operation.

This means rerunning the same batch will not create duplicate records in the curated table.

### Secure configuration

API credentials are read from environment variables and are never hardcoded in the source code.

In a deployed GCP environment, the credentials can be stored in Secret Manager.

## How the Pipeline Works

The pipeline follows these steps:

1. Read the application configuration.
2. Determine whether the run is a historical backfill or an incremental load.
3. Read the latest review timestamp from the curated BigQuery table.
4. Request review data from the external API.
5. Follow the API cursor until all pages have been retrieved.
6. Convert the API response into a consistent internal schema.
7. Append the ingested records to the raw BigQuery table.
8. Deduplicate the records using their review and order references.
9. Merge the latest record versions into the curated table.
10. Write operational information to the application logs.

## Backfill Mode

Backfill mode retrieves all historical reviews available from the API.

The process is:

```text
Start without a watermark
        │
        ▼
Request the first API page
        │
        ▼
Follow the cursor through all remaining pages
        │
        ▼
Load the records into the raw table
        │
        ▼
Merge the records into the curated table
```

Backfill mode is intended for the initial project deployment or controlled historical reloads.

Example command:

```bash
python src/pipeline.py \
  --api-base "https://api.example.com" \
  --bq-table "your-project.customer_feedback.reviews" \
  --full-backfill
```

## Incremental Mode

Incremental mode retrieves only new or recently updated reviews.

The process is:

```text
Read the latest review timestamp from BigQuery
        │
        ▼
Use the timestamp as the API watermark
        │
        ▼
Request reviews posted after the watermark
        │
        ▼
Append the new records to the raw table
        │
        ▼
Merge the records into the curated table
```

In production, Cloud Scheduler can invoke the Cloud Run workload every morning at 08:00.

Example command:

```bash
python src/pipeline.py \
  --api-base "https://api.example.com" \
  --bq-table "your-project.customer_feedback.reviews"
```

## Raw and Curated Data Layers

### Raw table

The raw table is an append-only ingestion layer.

Its purpose is to preserve the data received from the source system.

Example name:

```text
your-project.customer_feedback.reviews_raw
```

The raw table can contain:

* Review ID
* Review timestamp
* Customer reference
* Order reference
* Review text
* Rating
* Original source payload
* Ingestion timestamp

The raw table is partitioned using the ingestion timestamp.

### Curated table

The curated table is the analytics-ready layer.

Example name:

```text
your-project.customer_feedback.reviews
```

It contains the latest version of each review and removes duplicate records using a BigQuery `MERGE`.

The curated table is partitioned using the review date and can be clustered using the order reference.

Analysts should normally query the curated table rather than the raw table.

## Project Structure

The initial project structure is:

```text
gcp-api-to-bigquery-pipeline/
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
├── src/
│   └── pipeline.py
├── examples/
│   └── reviews.json
└── docs/
```

As the project develops, the application will be separated into smaller modules for configuration, API access, data models, BigQuery operations and orchestration.

## Local Setup

### Prerequisites

To run the project locally, you will eventually need:

* Python 3.11 or later
* Git
* A Google Cloud project
* Google Cloud authentication
* Access to a compatible reviews API

The project will also provide a mock-data mode so that it can be tested without real API or Google Cloud credentials.

### Create a Python virtual environment

Create the virtual environment:

```bash
python -m venv .venv
```

Activate it on macOS, Linux or Git Bash:

```bash
source .venv/bin/activate
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Activate it on Windows Command Prompt:

```cmd
.venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

## Running the Pipeline

The project will support three execution modes.

### Mock mode

Mock mode reads synthetic reviews from a local JSON file.

It does not require an API token or a BigQuery connection.

```bash
python src/pipeline.py \
  --source-file examples/reviews.json \
  --dry-run
```

### Historical backfill

```bash
python src/pipeline.py \
  --api-base "https://api.example.com" \
  --bq-table "your-project.customer_feedback.reviews" \
  --full-backfill
```

### Incremental load

```bash
python src/pipeline.py \
  --api-base "https://api.example.com" \
  --bq-table "your-project.customer_feedback.reviews"
```

## Testing

The project will use `pytest` for automated tests.

The tests will cover:

* Review normalisation
* Timestamp conversion
* Missing or invalid values
* Cursor pagination
* Retry behaviour
* Watermark handling
* Duplicate prevention

Tests will be run with:

```bash
pytest
```

Automated tests will later run through GitHub Actions whenever code is pushed to the repository.

## Deployment

The production-style deployment will use:

* Cloud Run to execute the application
* Cloud Scheduler to start the application every morning
* BigQuery to store raw and curated data
* Secret Manager to store the API token
* Cloud Logging to capture application logs

The infrastructure will initially be created manually so that each GCP resource can be understood.

Terraform will be introduced later to automate the infrastructure after the manual deployment process is understood.

## Security

The project follows these security principles:

* API credentials are not stored in the source code.
* Secrets are read from environment variables.
* Local `.env` files are excluded from Git.
* Production secrets can be stored in Google Secret Manager.
* The Cloud Run service account should receive only the permissions it needs.
* Real customer data is not included in the repository.
* All example reviews are synthetic.
* Company-specific project IDs, URLs and table names are removed.

## Limitations

The first version of the project has several deliberate limitations:

* It is designed as a reference implementation rather than a vendor-specific API client.
* Schema evolution is not initially automated.
* Very large backfills may require batch-by-batch loading rather than storing all records in memory.
* The first version uses a timestamp watermark and may later include an overlap window for late-arriving records.
* Infrastructure automation will not be included until the manual deployment is working.
* Monitoring and alerting will be introduced in a later version.

These limitations are documented so that future improvements can be implemented transparently.

## Future Improvements

Planned improvements include:

* Separating the Python application into smaller modules
* Adding synthetic mock API responses
* Adding unit and integration tests
* Adding Docker support
* Deploying the application to Cloud Run
* Scheduling daily runs through Cloud Scheduler
* Storing credentials in Secret Manager
* Adding structured Cloud Logging
* Adding GitHub Actions for continuous integration
* Adding Terraform for infrastructure as code
* Supporting configurable schemas and source systems
* Processing large backfills page by page
* Adding monitoring and failure alerts

## Background

This repository is an independently recreated and sanitised reference implementation inspired by a production data pipeline I previously delivered while working as a Data Engineer.

It does not contain company source code, credentials, customer data, internal URLs or confidential configuration.

The purpose of this project is to demonstrate the engineering patterns used to build reliable cloud data pipelines, including incremental ingestion, pagination, retry handling, raw and curated data layers, idempotent loading and cloud-native deployment.
