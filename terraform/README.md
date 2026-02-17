# TensrGrid Infrastructure Management

This directory contains Terraform modules to manage the TensrGrid infrastructure on Google Cloud Platform.

## 🚀 Getting Started

### 1. Prerequisites
- **Terraform CLI**: Installed on your machine.
- **GCP Project**: `project-edc85560-4f90-48de-813`
- **Application Default Credentials**: Run `gcloud auth application-default login`.

### 2. Setup Configuration
Copy the example variables file and add your project details:
```bash
cp terraform.tfvars.example terraform.tfvars
```

### 3. Initialize Terraform
This downloads the required plugins:
```bash
terraform init
```

### 4. Plan and Apply
Preview changes:
```bash
terraform plan
```
Apply the changes to create the resources:
```bash
terraform apply
```

## 🛠 Managed Resources

### GCS Bucket
- **Name**: `tensrgrid-raw-data`
- **Utility**: Primary storage for raw uploaded files.
- **Settings**: Uniform access enabled, Versioning enabled.

### MySQL Instance
- **Resource**: Compute Engine (VM)
- **Machine Type**: `e2-micro`
- **Database**: MariaDB/MySQL
- **Network**: Port 3306 open to `0.0.0.0/0` (Public Traffic).

## ⚠️ Security Note
The MySQL instance is currently open to all traffic on port 3306 as requested. For a production environment, it is highly recommended to:
1. Limit `source_ranges` to specific IPs.
2. Use Cloud SQL instead of a VM for managed security.
3. Use Identity-Aware Proxy (IAP) for access.

## 🔄 Resource Management Commands
- **Check Status**: `terraform show`
- **Destroy Infrastructure**: `terraform destroy`
- **Refresh State**: `terraform refresh`
