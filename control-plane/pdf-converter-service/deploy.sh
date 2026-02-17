#!/bin/bash

# PDF Converter Service Deployment Script
# This script builds and deploys the PDF converter service to Cloud Run

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-}"
REGION="${REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-pdf-converter-service}"
GCS_BUCKET="${GCS_BUCKET:-tensrgrid-raw-data}"
OUTPUT_FOLDER="${OUTPUT_FOLDER:-tensrgrid/markdown-output}"
PUBSUB_TOPIC="${PUBSUB_TOPIC:-tensrgrid-data-file-uploaded}"

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if PROJECT_ID is set
if [ -z "$PROJECT_ID" ]; then
    print_error "GCP_PROJECT_ID environment variable is not set"
    echo "Usage: export GCP_PROJECT_ID=your-project-id && ./deploy.sh"
    exit 1
fi

print_info "Starting deployment of $SERVICE_NAME to Cloud Run"
print_info "Project: $PROJECT_ID"
print_info "Region: $REGION"

# Set the project
print_info "Setting GCP project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
print_info "Enabling required APIs..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    pubsub.googleapis.com \
    storage.googleapis.com

# Build the container image
print_info "Building container image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy to Cloud Run
print_info "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 0 \
    --concurrency 1 \
    --set-env-vars GCP_PROJECT_ID=$PROJECT_ID,GCS_BUCKET=$GCS_BUCKET,OUTPUT_FOLDER=$OUTPUT_FOLDER

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')
print_info "Service deployed at: $SERVICE_URL"

# Check if Pub/Sub topic exists
print_info "Checking Pub/Sub topic..."
if gcloud pubsub topics describe $PUBSUB_TOPIC &>/dev/null; then
    print_info "Pub/Sub topic '$PUBSUB_TOPIC' exists"
else
    print_warning "Pub/Sub topic '$PUBSUB_TOPIC' does not exist"
    read -p "Do you want to create it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gcloud pubsub topics create $PUBSUB_TOPIC
        print_info "Created Pub/Sub topic '$PUBSUB_TOPIC'"
    fi
fi

# Create or update Pub/Sub subscription
SUBSCRIPTION_NAME="pdf-converter-subscription"
print_info "Setting up Pub/Sub subscription..."

if gcloud pubsub subscriptions describe $SUBSCRIPTION_NAME &>/dev/null; then
    print_warning "Subscription '$SUBSCRIPTION_NAME' already exists"
    read -p "Do you want to update it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gcloud pubsub subscriptions delete $SUBSCRIPTION_NAME
        gcloud pubsub subscriptions create $SUBSCRIPTION_NAME \
            --topic $PUBSUB_TOPIC \
            --push-endpoint=$SERVICE_URL \
            --ack-deadline=300
        print_info "Updated subscription '$SUBSCRIPTION_NAME'"
    fi
else
    gcloud pubsub subscriptions create $SUBSCRIPTION_NAME \
        --topic $PUBSUB_TOPIC \
        --push-endpoint=$SERVICE_URL \
        --ack-deadline=300
    print_info "Created subscription '$SUBSCRIPTION_NAME'"
fi

# Summary
print_info "Deployment complete!"
echo ""
echo "Service URL: $SERVICE_URL"
echo "Pub/Sub Topic: $PUBSUB_TOPIC"
echo "Subscription: $SUBSCRIPTION_NAME"
echo ""
print_info "To view logs, run:"
echo "  gcloud run services logs read $SERVICE_NAME --region $REGION --limit 50"
echo ""
print_info "To test the service, publish a message to the topic:"
echo "  gcloud pubsub topics publish $PUBSUB_TOPIC --message '{\"event_type\":\"data_file_uploaded\",\"data_file\":{\"mime_type\":\"application/pdf\"}}'"
