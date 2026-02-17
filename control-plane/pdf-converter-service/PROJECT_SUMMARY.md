# PDF to Markdown Converter Service - Project Summary

## Overview

A production-ready Cloud Run service that automatically converts PDF files to Markdown format when they are uploaded to Google Cloud Storage. The service integrates with Google Pub/Sub to receive notifications and processes files asynchronously.

## Architecture

```
┌─────────────────┐
│  Laravel App    │
│  (Control Plane)│
└────────┬────────┘
         │ Uploads PDF
         ▼
┌─────────────────┐
│  Google Cloud   │
│    Storage      │
└────────┬────────┘
         │ Triggers
         ▼
┌─────────────────┐
│   Pub/Sub       │
│   Topic         │
└────────┬────────┘
         │ Push
         ▼
┌─────────────────┐
│  Cloud Run      │
│  PDF Converter  │
└────────┬────────┘
         │ Downloads PDF
         │ Converts to MD
         │ Uploads MD
         ▼
┌─────────────────┐
│  Google Cloud   │
│    Storage      │
│  (Output Folder)│
└─────────────────┘
```

## Project Structure

```
pdf-converter-service/
├── main.py                 # Flask app & Pub/Sub handler
├── pdf_processor.py        # PDF to Markdown conversion logic
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container definition
├── cloudbuild.yaml       # CI/CD configuration
├── deploy.sh             # Bash deployment script
├── deploy.ps1            # PowerShell deployment script
├── test_service.py       # Testing utilities
├── .env.example          # Environment template
├── .dockerignore         # Docker ignore rules
├── .gitignore           # Git ignore rules
├── README.md            # Full documentation
└── QUICKSTART.md        # Quick start guide
```

## Key Features

### 1. **Pub/Sub Integration**
- Listens to `tensrgrid-data-file-uploaded` topic
- Processes messages in real-time
- Automatic retry on failure

### 2. **PDF Processing**
- Uses PyMuPDF (fitz) for robust PDF parsing
- Preserves formatting:
  - Headers (H1-H4)
  - Bold and italic text
  - Lists (bulleted and numbered)
  - Code blocks
  - Document metadata

### 3. **Cloud Storage Integration**
- Downloads PDFs from GCS
- Uploads converted Markdown to configurable output folder
- Maintains folder structure based on collection ID

### 4. **Production Ready**
- Comprehensive error handling
- Structured logging
- Health check endpoint
- Configurable resource limits
- Automatic scaling

### 5. **Easy Deployment**
- One-command deployment scripts
- CI/CD ready with Cloud Build
- Environment-based configuration
- Local testing support

## File Descriptions

### Core Application Files

**main.py**
- Flask application entry point
- Pub/Sub message handler
- GCS download/upload logic
- Health check endpoint
- Error handling and logging

**pdf_processor.py**
- PDF to Markdown conversion engine
- Font-based formatting detection
- List and table detection
- Markdown cleanup and formatting
- Advanced converter with enhanced features

**config.py**
- Centralized configuration
- Heading size thresholds
- Conversion options
- Processing limits

### Deployment Files

**Dockerfile**
- Multi-stage build for optimization
- Python 3.11 slim base
- PyMuPDF dependencies
- Gunicorn configuration

**deploy.sh / deploy.ps1**
- Automated deployment scripts
- API enablement
- Container building
- Service deployment
- Pub/Sub subscription setup

**cloudbuild.yaml**
- CI/CD pipeline configuration
- Automated builds on commit
- Container registry management
- Cloud Run deployment

### Configuration Files

**requirements.txt**
- Flask 3.0.0
- gunicorn 21.2.0
- google-cloud-storage 2.14.0
- google-cloud-pubsub 2.19.0
- PyMuPDF 1.23.26

**.env.example**
- Environment variable template
- GCP project configuration
- Storage settings

### Testing & Documentation

**test_service.py**
- Local and remote testing
- Health check testing
- PDF conversion testing
- Mock Pub/Sub messages

**README.md**
- Complete documentation
- Architecture overview
- Deployment instructions
- Configuration guide
- Troubleshooting

**QUICKSTART.md**
- 5-minute deployment guide
- Essential commands
- Common issues

## Deployment Options

### Option 1: Quick Deploy (Recommended)

**Windows:**
```powershell
$env:GCP_PROJECT_ID = "your-project-id"
cd control-plane/pdf-converter-service
.\deploy.ps1
```

**Linux/Mac:**
```bash
export GCP_PROJECT_ID=your-project-id
cd control-plane/pdf-converter-service
./deploy.sh
```

### Option 2: Manual Deploy

```bash
# Build
gcloud builds submit --tag gcr.io/$PROJECT_ID/pdf-converter-service

# Deploy
gcloud run deploy pdf-converter-service \
  --image gcr.io/$PROJECT_ID/pdf-converter-service \
  --region us-central1 \
  --memory 2Gi \
  --cpu 2
```

### Option 3: CI/CD with Cloud Build

```bash
# Set up trigger
gcloud builds triggers create github \
  --repo-name=your-repo \
  --branch-pattern="^main$" \
  --build-config=pdf-converter-service/cloudbuild.yaml
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GCP_PROJECT_ID` | GCP Project ID | Required |
| `GCS_BUCKET` | Storage bucket | `tensrgrid-raw-data` |
| `OUTPUT_FOLDER` | Output path | `tensrgrid/markdown-output` |
| `PORT` | Service port | `8080` |

### Resource Configuration

- **Memory**: 2Gi (handles large PDFs)
- **CPU**: 2 (faster processing)
- **Timeout**: 300s (5 minutes)
- **Concurrency**: 1 (one PDF at a time)
- **Max Instances**: 10 (cost control)
- **Min Instances**: 0 (no idle costs)

## Message Flow

1. **Upload**: User uploads PDF via Laravel app
2. **Publish**: Laravel publishes message to Pub/Sub
3. **Receive**: Cloud Run receives push notification
4. **Validate**: Service validates message format
5. **Download**: PDF downloaded from GCS
6. **Convert**: PDF converted to Markdown
7. **Upload**: Markdown uploaded to GCS
8. **Respond**: Success/error response returned
9. **Acknowledge**: Pub/Sub message acknowledged

## Output Structure

```
gs://tensrgrid-raw-data/
├── tensrgrid/
│   ├── documents/
│   │   └── {collection_id}/
│   │       └── {file}.pdf          # Input
│   └── markdown-output/
│       └── {collection_id}/
│           └── {file}.md           # Output
```

## Error Handling

### Handled Scenarios

1. **Non-PDF files**: Skipped with warning
2. **Download failures**: Logged and returned as error
3. **Conversion failures**: Logged with stack trace
4. **Upload failures**: Exception raised for retry
5. **Invalid messages**: Logged and ignored

### Retry Logic

- Pub/Sub automatically retries failed messages
- Exponential backoff
- Dead letter queue after max retries

## Monitoring

### Logs
```bash
gcloud run services logs read pdf-converter-service --limit 50
```

### Metrics
- Request count
- Request latency
- Error rate
- Instance count
- CPU/Memory usage

### Alerts (Recommended)
- Error rate > 5%
- Latency > 60s
- Instance count > 8

## Cost Optimization

### Current Configuration
- **Min instances**: 0 (no idle costs)
- **Max instances**: 10 (controlled scaling)
- **Memory**: 2Gi (right-sized for PDFs)
- **CPU**: 2 (balanced performance)

### Estimated Costs
- **Per conversion**: ~$0.0001 - $0.001
- **100 conversions/day**: ~$3-5/month
- **1000 conversions/day**: ~$30-50/month

### Cost Reduction Tips
1. Reduce memory if PDFs are small
2. Lower max instances
3. Increase concurrency if PDFs are small
4. Use preemptible instances (not available for Cloud Run)

## Security

### Current Setup
- Service runs with default compute service account
- Unauthenticated endpoint (Pub/Sub push)
- GCS access via service account

### Recommended Improvements
1. Create dedicated service account
2. Grant minimal permissions (Storage Object Admin)
3. Use Pub/Sub authentication
4. Enable VPC connector for private GCS access
5. Implement request validation

## Testing

### Local Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Set credentials
export GOOGLE_APPLICATION_CREDENTIALS=key.json

# Run service
python main.py

# Test
python test_service.py --url http://localhost:8080
```

### Remote Testing
```bash
# Test health
curl https://your-service-url/health

# Test with script
python test_service.py --url https://your-service-url
```

## Troubleshooting

### Common Issues

**Service not receiving messages**
- Check Pub/Sub subscription exists
- Verify service URL in subscription
- Check service account permissions

**PDF conversion fails**
- Verify PDF is not corrupted
- Check memory allocation (2Gi recommended)
- Review logs for specific error

**Upload to GCS fails**
- Verify service account has Storage Object Admin
- Check bucket exists
- Verify output path is valid

## Next Steps

### Immediate
1. Deploy to Cloud Run
2. Test with sample PDF
3. Monitor logs and metrics

### Short Term
1. Set up monitoring alerts
2. Create dedicated service account
3. Implement request validation
4. Add support for other formats (DOCX, etc.)

### Long Term
1. Implement caching for repeated conversions
2. Add OCR for scanned PDFs
3. Support batch processing
4. Add webhook notifications on completion

## Support & Maintenance

### Regular Tasks
- Monitor error rates
- Review and optimize costs
- Update dependencies
- Review and improve conversion quality

### Updating the Service
```bash
# Make changes to code
# Test locally
python test_service.py

# Deploy
./deploy.ps1  # or ./deploy.sh
```

## License

Proprietary - Vinayaga Software Solutions

---

**Created**: 2026-02-17  
**Version**: 1.0.0  
**Status**: Production Ready
