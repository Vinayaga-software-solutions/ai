# 1. Rebuild the image
cd c:\Users\vaidh\Documents\ai\control-plane
gcloud builds submit --tag us-central1-docker.pkg.dev/project-edc85560-4f90-48de-813/app-repo/laravel-app:latest .

# 2. Update Cloud Run (only if you change .env or infra)
cd c:\Users\vaidh\Documents\ai\terraform
terraform apply -auto-approve