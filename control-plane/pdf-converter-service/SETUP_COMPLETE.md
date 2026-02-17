# PDF to Markdown Converter Service - Complete Setup

## ✅ What Has Been Created

A complete, production-ready Cloud Run service has been created in:
```
control-plane/pdf-converter-service/
```

### 📁 Files Created (15 files)

#### Core Application (4 files)
1. **main.py** - Flask app, Pub/Sub handler, GCS integration
2. **pdf_processor.py** - PDF to Markdown conversion engine
3. **config.py** - Configuration settings
4. **dev.py** - Local development server

#### Deployment (4 files)
5. **Dockerfile** - Container definition for Cloud Run
6. **deploy.sh** - Bash deployment script (Linux/Mac)
7. **deploy.ps1** - PowerShell deployment script (Windows)
8. **cloudbuild.yaml** - CI/CD configuration

#### Configuration (3 files)
9. **requirements.txt** - Python dependencies
10. **.env.example** - Environment template
11. **.gitignore** - Git ignore rules
12. **.dockerignore** - Docker ignore rules

#### Documentation & Testing (3 files)
13. **README.md** - Complete documentation (9KB)
14. **QUICKSTART.md** - 5-minute deployment guide
15. **PROJECT_SUMMARY.md** - Architecture & overview
16. **test_service.py** - Testing utilities

## 🚀 Quick Start (Choose One)

### Option A: Deploy to Cloud Run (Recommended)

**Windows:**
```powershell
# Set your project ID
$env:GCP_PROJECT_ID = "your-project-id"

# Navigate to service directory
cd control-plane\pdf-converter-service

# Deploy (one command!)
.\deploy.ps1
```

**Linux/Mac:**
```bash
# Set your project ID
export GCP_PROJECT_ID=your-project-id

# Navigate to service directory
cd control-plane/pdf-converter-service

# Make script executable
chmod +x deploy.sh

# Deploy (one command!)
./deploy.sh
```

### Option B: Test Locally First

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Set credentials
set GOOGLE_APPLICATION_CREDENTIALS=path\to\key.json  # Windows
# export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json  # Linux/Mac

# Set project ID
set GCP_PROJECT_ID=your-project-id  # Windows
# export GCP_PROJECT_ID=your-project-id  # Linux/Mac

# Run development server
python dev.py

# In another terminal, test it
python test_service.py --health-only
```

## 🔄 How It Works

```
1. User uploads PDF in Laravel app
   ↓
2. Laravel publishes to Pub/Sub topic: tensrgrid-data-file-uploaded
   ↓
3. Cloud Run service receives push notification
   ↓
4. Service downloads PDF from GCS
   ↓
5. PDF converted to Markdown (preserving formatting)
   ↓
6. Markdown uploaded to GCS: tensrgrid/markdown-output/{collection_id}/
   ↓
7. Service returns success response
```

## 📊 Message Format Expected

Your Laravel app already publishes the correct format:

```json
{
  "event_type": "data_file_uploaded",
  "data_file": {
    "id": 50,
    "mime_type": "application/pdf",
    "storage_path": "tensrgrid/documents/2/file.pdf",
    "original_name": "document.pdf"
  },
  "data_collection": {
    "id": 2
  },
  "storage": {
    "bucket": "tensrgrid-raw-data"
  }
}
```

## 📂 Output Location

Converted files will be stored at:
```
gs://tensrgrid-raw-data/tensrgrid/markdown-output/{collection_id}/{filename}.md
```

## 🔧 Configuration

### Default Settings
- **Memory**: 2Gi (handles large PDFs)
- **CPU**: 2 cores (fast processing)
- **Timeout**: 5 minutes
- **Scaling**: 0-10 instances
- **Region**: us-central1

### Environment Variables
- `GCP_PROJECT_ID` - Your GCP project
- `GCS_BUCKET` - Storage bucket (default: tensrgrid-raw-data)
- `OUTPUT_FOLDER` - Output path (default: tensrgrid/markdown-output)

## 📋 What the Service Does

### ✅ Supported Features
- ✅ Downloads PDFs from GCS
- ✅ Converts to Markdown with formatting:
  - Headers (H1-H4)
  - Bold and italic text
  - Lists (bulleted and numbered)
  - Code blocks
  - Document metadata
- ✅ Uploads to GCS
- ✅ Handles errors gracefully
- ✅ Logs everything
- ✅ Auto-scales
- ✅ Only processes PDFs (skips other files)

### 🔍 Conversion Quality
The converter preserves:
- Document structure
- Font-based formatting
- Lists and bullets
- Page numbers
- Metadata (title, author, subject)

## 🧪 Testing

### Test Health Endpoint
```bash
curl https://your-service-url/health
```

Expected response:
```json
{"status": "healthy", "service": "pdf-converter"}
```

### Test PDF Conversion
```bash
python test_service.py --url https://your-service-url
```

## 📊 Monitoring

### View Logs
```bash
gcloud run services logs read pdf-converter-service --region us-central1 --limit 50
```

### View Service Status
```bash
gcloud run services describe pdf-converter-service --region us-central1
```

### GCP Console
Visit: https://console.cloud.google.com/run

## 💰 Estimated Costs

- **Per conversion**: ~$0.0001 - $0.001
- **100 PDFs/day**: ~$3-5/month
- **1000 PDFs/day**: ~$30-50/month
- **Idle cost**: $0 (scales to zero)

## 🔐 Security Notes

### Current Setup
- ✅ Runs on Cloud Run (managed security)
- ✅ Uses service account for GCS access
- ✅ HTTPS by default
- ⚠️ Unauthenticated endpoint (required for Pub/Sub push)

### Recommended Next Steps
1. Create dedicated service account
2. Grant minimal permissions
3. Enable VPC connector for private GCS
4. Add request validation

## 🐛 Troubleshooting

### Service not receiving messages
```bash
# Check subscription
gcloud pubsub subscriptions describe pdf-converter-subscription

# Check service logs
gcloud run services logs read pdf-converter-service --limit 20
```

### PDF conversion fails
- Check PDF is not corrupted
- Verify memory allocation (2Gi)
- Review logs for specific error

### Permission errors
```bash
# Grant storage permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:YOUR-SA@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"
```

## 📚 Documentation

- **README.md** - Complete documentation
- **QUICKSTART.md** - 5-minute guide
- **PROJECT_SUMMARY.md** - Architecture overview
- **This file** - Setup checklist

## ✅ Deployment Checklist

- [ ] Set GCP_PROJECT_ID environment variable
- [ ] Run deployment script (deploy.ps1 or deploy.sh)
- [ ] Verify service is deployed
- [ ] Test health endpoint
- [ ] Verify Pub/Sub subscription created
- [ ] Upload a test PDF via Laravel app
- [ ] Check logs for processing
- [ ] Verify Markdown file in output folder

## 🎯 Next Steps

### Immediate (Required)
1. **Deploy**: Run `deploy.ps1` or `deploy.sh`
2. **Test**: Upload a PDF via your Laravel app
3. **Verify**: Check output folder for .md file

### Short Term (Recommended)
1. Set up monitoring alerts
2. Create dedicated service account
3. Test with various PDF types
4. Monitor costs

### Long Term (Optional)
1. Add OCR for scanned PDFs
2. Support other formats (DOCX, etc.)
3. Implement caching
4. Add webhook notifications

## 🆘 Need Help?

### Check Logs
```bash
gcloud run services logs read pdf-converter-service --region us-central1
```

### Common Commands
```bash
# Redeploy
./deploy.ps1  # or ./deploy.sh

# View service details
gcloud run services describe pdf-converter-service --region us-central1

# Delete service
gcloud run services delete pdf-converter-service --region us-central1

# Delete subscription
gcloud pubsub subscriptions delete pdf-converter-subscription
```

## 📝 Summary

You now have a **complete, production-ready PDF to Markdown converter service** that:

1. ✅ Listens to your existing Pub/Sub topic
2. ✅ Downloads PDFs from GCS
3. ✅ Converts to Markdown with formatting
4. ✅ Uploads to GCS output folder
5. ✅ Scales automatically
6. ✅ Handles errors gracefully
7. ✅ Costs ~$0 when idle

**Just run the deployment script and you're done!**

---

**Created**: 2026-02-17  
**Location**: `control-plane/pdf-converter-service/`  
**Status**: ✅ Ready to Deploy
