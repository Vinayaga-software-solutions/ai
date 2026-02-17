# Simple manual deployment script for PDF Converter Service
# This avoids the permission issues with automated deployment

param(
    [string]$ProjectId = $env:GCP_PROJECT_ID,
    [string]$Region = "us-central1"
)

if ([string]::IsNullOrEmpty($ProjectId)) {
    Write-Host "[ERROR] GCP_PROJECT_ID is not set" -ForegroundColor Red
    Write-Host "Usage: `$env:GCP_PROJECT_ID='your-project-id'; .\manual-deploy.ps1"
    exit 1
}

Write-Host "[INFO] Manual deployment of pdf-converter-service" -ForegroundColor Green
Write-Host "[INFO] Project: $ProjectId" -ForegroundColor Green
Write-Host "[INFO] Region: $Region" -ForegroundColor Green
Write-Host ""

# Set project
Write-Host "[INFO] Setting project..." -ForegroundColor Green
gcloud config set project $ProjectId

# Build locally and deploy directly
Write-Host "[INFO] Building and deploying to Cloud Run..." -ForegroundColor Green
Write-Host "[INFO] This will build the image and deploy in one step" -ForegroundColor Green
Write-Host ""

gcloud run deploy pdf-converter-service `
    --source . `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --memory 2Gi `
    --cpu 2 `
    --timeout 300 `
    --max-instances 10 `
    --min-instances 0 `
    --concurrency 1 `
    --set-env-vars "GCP_PROJECT_ID=$ProjectId,GCS_BUCKET=tensrgrid-raw-data,OUTPUT_FOLDER=tensrgrid/markdown-output"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] Deployment complete!" -ForegroundColor Green
    
    # Get service URL
    $ServiceUrl = gcloud run services describe pdf-converter-service --region $Region --format 'value(status.url)'
    Write-Host "Service URL: $ServiceUrl" -ForegroundColor Cyan
    
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Test health: curl $ServiceUrl/health"
    Write-Host "2. Set up Pub/Sub subscription (see README.md)"
} else {
    Write-Host ""
    Write-Host "[ERROR] Deployment failed" -ForegroundColor Red
    exit 1
}
