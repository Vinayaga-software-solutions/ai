# PDF to Markdown Converter Service

A Cloud Run service that listens to Google Pub/Sub messages for file uploads, downloads PDF files from Google Cloud Storage, converts them to Markdown format while preserving formatting, and uploads the converted files back to GCS.

## Architecture

```
Pub/Sub Topic (tensrgrid-data-file-uploaded)
    ↓
Cloud Run Service (PDF Converter)
    ↓
1. Receive message
2. Download PDF from GCS
3. Convert PDF → Markdown
4. Upload Markdown to GCS
```

## Features

- **Pub/Sub Integration**: Listens to `tensrgrid-data-file-uploaded` topic
- **PDF Processing**: Converts PDF files to Markdown using PyMuPDF
- **Format Preservation**: Maintains headers, bold, italic, lists, and document structure
- **Cloud Storage**: Downloads from and uploads to Google Cloud Storage
- **Scalable**: Runs as a Cloud Run service with automatic scaling
- **Error Handling**: Comprehensive logging and error recovery

## Message Format

The service expects Pub/Sub messages in the following format:

```json
{
  "event_type": "data_file_uploaded",
  "occurred_at": "2026-02-17T13:50:49+00:00",
  "data_file": {
    "id": 50,
    "data_id": 7,
    "original_name": "document.pdf",
    "storage_path": "tensrgrid/documents/2/xyz.pdf",
    "mime_type": "application/pdf",
    "size": 105,
    "created_at": "2026-02-17T13:50:49+00:00"
  },
  "data": {
    "id": 7,
    "name": "TensrGrid",
    "type": "document",
    "storage_path": "tensrgrid/documents/2",
    "data_collection_id": 2,
    "created_by": 1
  },
  "data_collection": {
    "id": 2,
    "name": "VAIDHYANATHAN",
    "project_id": 16
  },
  "project": {
    "id": 16,
    "name": "1"
  },
  "storage": {
    "disk": "gcs",
    "bucket": "tensrgrid-raw-data",
    "gcs_uri": "gs://tensrgrid-raw-data/tensrgrid/documents/2/xyz.pdf"
  }
}
```

## Local Development

### Prerequisites

- Python 3.11+
- Google Cloud SDK
- Service account with permissions:
  - Cloud Storage: Read/Write
  - Pub/Sub: Subscriber

### Setup

1. **Clone and navigate to the service directory**:
   ```bash
   cd control-plane/pdf-converter-service
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up Google Cloud credentials**:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
   ```

6. **Run the service locally**:
   ```bash
   python main.py
   ```

### Testing Locally

You can test the service by sending a POST request with a Pub/Sub message:

```bash
curl -X POST http://localhost:8080/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "data": "'$(echo '{
        "event_type": "data_file_uploaded",
        "data_file": {
          "id": 1,
          "mime_type": "application/pdf",
          "storage_path": "path/to/file.pdf",
          "original_name": "test.pdf"
        },
        "data_collection": {"id": 1},
        "storage": {"bucket": "your-bucket"}
      }' | base64)'"
    }
  }'
```

## Deployment to Cloud Run

### Prerequisites

- Google Cloud Project with billing enabled
- Cloud Run API enabled
- Cloud Build API enabled
- Artifact Registry API enabled

### Deployment Steps

1. **Set your project ID**:
   ```bash
   export PROJECT_ID=your-project-id
   export REGION=us-central1
   export SERVICE_NAME=pdf-converter-service
   ```

2. **Build and push the container image**:
   ```bash
   gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME
   ```

3. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy $SERVICE_NAME \
     --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
     --platform managed \
     --region $REGION \
     --allow-unauthenticated \
     --memory 2Gi \
     --cpu 2 \
     --timeout 300 \
     --set-env-vars GCP_PROJECT_ID=$PROJECT_ID,GCS_BUCKET=tensrgrid-raw-data,OUTPUT_FOLDER=tensrgrid/markdown-output
   ```

4. **Create Pub/Sub push subscription**:
   ```bash
   # Get the Cloud Run service URL
   export SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')
   
   # Create the subscription
   gcloud pubsub subscriptions create pdf-converter-subscription \
     --topic tensrgrid-data-file-uploaded \
     --push-endpoint=$SERVICE_URL \
     --push-auth-service-account=your-service-account@$PROJECT_ID.iam.gserviceaccount.com
   ```

### Alternative: Deploy with Service Account

For better security, deploy with a specific service account:

```bash
# Create service account
gcloud iam service-accounts create pdf-converter-sa \
  --display-name "PDF Converter Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:pdf-converter-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

# Deploy with service account
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --service-account pdf-converter-sa@$PROJECT_ID.iam.gserviceaccount.com \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --set-env-vars GCP_PROJECT_ID=$PROJECT_ID,GCS_BUCKET=tensrgrid-raw-data,OUTPUT_FOLDER=tensrgrid/markdown-output
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GCP_PROJECT_ID` | Google Cloud Project ID | - |
| `GCS_BUCKET` | GCS bucket name for storage | `tensrgrid-raw-data` |
| `OUTPUT_FOLDER` | Output folder path in GCS | `tensrgrid/markdown-output` |
| `PORT` | Service port | `8080` |

### Resource Configuration

- **Memory**: 2Gi (recommended for PDF processing)
- **CPU**: 2 (recommended for faster processing)
- **Timeout**: 300 seconds (5 minutes)
- **Concurrency**: 1 (one request at a time per instance)

## Monitoring

### View Logs

```bash
gcloud run services logs read $SERVICE_NAME --region $REGION --limit 50
```

### Monitor Service

```bash
gcloud run services describe $SERVICE_NAME --region $REGION
```

## Output Structure

Converted Markdown files are stored in GCS with the following structure:

```
gs://tensrgrid-raw-data/
  └── tensrgrid/
      └── markdown-output/
          └── {data_collection_id}/
              └── {filename}.md
```

## Error Handling

The service handles the following scenarios:

- **Non-PDF files**: Skipped with warning log
- **Download failures**: Error logged, returns error response
- **Conversion failures**: Error logged with stack trace
- **Upload failures**: Error logged, exception raised

## Scaling

Cloud Run automatically scales based on:
- Number of incoming requests
- CPU and memory utilization
- Configured concurrency limits

Configure scaling:

```bash
gcloud run services update $SERVICE_NAME \
  --region $REGION \
  --min-instances 0 \
  --max-instances 10 \
  --concurrency 1
```

## Cost Optimization

- **Min instances**: Set to 0 to avoid idle costs
- **Max instances**: Limit to control maximum spend
- **Timeout**: Set appropriately to avoid long-running requests
- **Memory**: Use 2Gi only if needed, reduce for smaller PDFs

## Troubleshooting

### Service not receiving messages

1. Check Pub/Sub subscription is active:
   ```bash
   gcloud pubsub subscriptions describe pdf-converter-subscription
   ```

2. Verify service URL is correct in subscription
3. Check service account has Pub/Sub permissions

### PDF conversion fails

1. Check logs for specific error
2. Verify PDF is not corrupted
3. Ensure sufficient memory allocation
4. Check PyMuPDF version compatibility

### Upload to GCS fails

1. Verify service account has Storage Object Admin role
2. Check bucket exists and is accessible
3. Verify output path is valid

## Development

### Project Structure

```
pdf-converter-service/
├── main.py              # Flask application and Pub/Sub handler
├── pdf_processor.py     # PDF to Markdown conversion logic
├── requirements.txt     # Python dependencies
├── Dockerfile          # Container definition
├── .env.example        # Environment template
├── .dockerignore       # Docker ignore rules
└── README.md           # This file
```

### Adding Features

To extend the converter:

1. Modify `pdf_processor.py` for conversion logic
2. Update `main.py` for message handling
3. Test locally before deploying
4. Update documentation

## License

Proprietary - Vinayaga Software Solutions
