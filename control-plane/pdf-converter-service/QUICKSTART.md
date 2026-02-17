# Quick Start Guide

## Prerequisites

1. **Google Cloud Project** with billing enabled
2. **gcloud CLI** installed and authenticated
3. **Python 3.11+** (for local testing)
4. **Docker** (optional, for local container testing)

## Quick Deployment (5 minutes)

### 1. Set Environment Variables

```bash
# Windows PowerShell
$env:GCP_PROJECT_ID = "your-project-id"

# Linux/Mac
export GCP_PROJECT_ID=your-project-id
```

### 2. Deploy to Cloud Run

**Windows:**
```powershell
cd control-plane/pdf-converter-service
.\deploy.ps1
```

**Linux/Mac:**
```bash
cd control-plane/pdf-converter-service
chmod +x deploy.sh
./deploy.sh
```

### 3. Verify Deployment

The script will output the service URL. Test it:

```bash
curl https://your-service-url/health
```

Expected response:
```json
{"status": "healthy", "service": "pdf-converter"}
```

## Local Testing (Optional)

### 1. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set Up Credentials

```bash
# Download service account key from GCP Console
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 4. Run Locally

```bash
python main.py
```

### 5. Test Locally

```bash
python test_service.py --url http://localhost:8080 --health-only
```

## How It Works

1. **File Upload**: When a PDF is uploaded to your Laravel app, it publishes a message to Pub/Sub
2. **Message Received**: Cloud Run service receives the push notification
3. **Download**: Service downloads the PDF from GCS
4. **Convert**: PDF is converted to Markdown using PyMuPDF
5. **Upload**: Markdown file is uploaded back to GCS in the output folder
6. **Complete**: Service returns success response

## File Locations

- **Input**: `gs://tensrgrid-raw-data/tensrgrid/documents/{collection_id}/{filename}.pdf`
- **Output**: `gs://tensrgrid-raw-data/tensrgrid/markdown-output/{collection_id}/{filename}.md`

## Monitoring

### View Logs
```bash
gcloud run services logs read pdf-converter-service --region us-central1 --limit 50
```

### View Service Details
```bash
gcloud run services describe pdf-converter-service --region us-central1
```

### Monitor in Console
Visit: https://console.cloud.google.com/run

## Troubleshooting

### Service not receiving messages
- Check Pub/Sub subscription exists and is active
- Verify service URL in subscription matches deployed URL
- Check service logs for errors

### PDF conversion fails
- Verify PDF is not corrupted
- Check service has enough memory (2Gi recommended)
- Review logs for specific error

### Permission errors
- Ensure service account has Storage Object Admin role
- Verify Pub/Sub permissions are correct

## Next Steps

1. **Monitor**: Set up Cloud Monitoring alerts
2. **Scale**: Adjust min/max instances based on load
3. **Optimize**: Fine-tune memory and CPU based on PDF sizes
4. **Enhance**: Add support for other file formats

## Support

For issues or questions, check:
- Service logs: `gcloud run services logs read pdf-converter-service`
- README.md for detailed documentation
- GCP Console for service status
