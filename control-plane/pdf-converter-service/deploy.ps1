# PDF Converter Service Deployment Script (PowerShell)
# This script builds and deploys the PDF converter service to Cloud Run

param(
    [string]$ProjectId = $env:GCP_PROJECT_ID,
    [string]$Region = "us-central1",
    [string]$ServiceName = "pdf-converter-service",
    [string]$GcsBucket = "tensrgrid-raw-data",
    [string]$OutputFolder = "tensrgrid/markdown-output",
    [string]$PubSubTopic = "tensrgrid-data-file-uploaded"
)

# Function to print colored output
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check if PROJECT_ID is set
if ([string]::IsNullOrEmpty($ProjectId)) {
    Write-Error "GCP_PROJECT_ID is not set"
    Write-Host "Usage: `$env:GCP_PROJECT_ID='your-project-id'; .\deploy.ps1"
    exit 1
}

Write-Info "Starting deployment of $ServiceName to Cloud Run"
Write-Info "Project: $ProjectId"
Write-Info "Region: $Region"

# Set the project
Write-Info "Setting GCP project..."
gcloud config set project $ProjectId

# Enable required APIs
Write-Info "Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com run.googleapis.com pubsub.googleapis.com storage.googleapis.com

# Build the container image
Write-Info "Building container image..."
gcloud builds submit --tag "gcr.io/$ProjectId/$ServiceName"

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to build container image"
    exit 1
}

# Deploy to Cloud Run
Write-Info "Deploying to Cloud Run..."
gcloud run deploy $ServiceName `
    --image "gcr.io/$ProjectId/$ServiceName" `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --memory 2Gi `
    --cpu 2 `
    --timeout 300 `
    --max-instances 10 `
    --min-instances 0 `
    --concurrency 1 `
    --set-env-vars "GCP_PROJECT_ID=$ProjectId,GCS_BUCKET=$GcsBucket,OUTPUT_FOLDER=$OutputFolder"

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to deploy to Cloud Run"
    exit 1
}

# Get the service URL
$ServiceUrl = gcloud run services describe $ServiceName --region $Region --format 'value(status.url)'
Write-Info "Service deployed at: $ServiceUrl"

# Check if Pub/Sub topic exists
Write-Info "Checking Pub/Sub topic..."
$topicExists = gcloud pubsub topics describe $PubSubTopic 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Info "Pub/Sub topic '$PubSubTopic' exists"
} else {
    Write-Warning "Pub/Sub topic '$PubSubTopic' does not exist"
    $create = Read-Host "Do you want to create it? (y/n)"
    if ($create -eq 'y' -or $create -eq 'Y') {
        gcloud pubsub topics create $PubSubTopic
        Write-Info "Created Pub/Sub topic '$PubSubTopic'"
    }
}

# Create or update Pub/Sub subscription
$SubscriptionName = "pdf-converter-subscription"
Write-Info "Setting up Pub/Sub subscription..."

$subExists = gcloud pubsub subscriptions describe $SubscriptionName 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Warning "Subscription '$SubscriptionName' already exists"
    $update = Read-Host "Do you want to update it? (y/n)"
    if ($update -eq 'y' -or $update -eq 'Y') {
        gcloud pubsub subscriptions delete $SubscriptionName --quiet
        gcloud pubsub subscriptions create $SubscriptionName `
            --topic $PubSubTopic `
            --push-endpoint=$ServiceUrl `
            --ack-deadline=300
        Write-Info "Updated subscription '$SubscriptionName'"
    }
} else {
    gcloud pubsub subscriptions create $SubscriptionName `
        --topic $PubSubTopic `
        --push-endpoint=$ServiceUrl `
        --ack-deadline=300
    Write-Info "Created subscription '$SubscriptionName'"
}

# Summary
Write-Info "Deployment complete!"
Write-Host ""
Write-Host "Service URL: $ServiceUrl"
Write-Host "Pub/Sub Topic: $PubSubTopic"
Write-Host "Subscription: $SubscriptionName"
Write-Host ""
Write-Info "To view logs, run:"
Write-Host "  gcloud run services logs read $ServiceName --region $Region --limit 50"
Write-Host ""
Write-Info "To test the service, publish a message to the topic:"
Write-Host "  gcloud pubsub topics publish $PubSubTopic --message '{`"event_type`":`"data_file_uploaded`",`"data_file`":{`"mime_type`":`"application/pdf`"}}'"
