# GMRecords Terraform Configuration

This Terraform configuration sets up AWS infrastructure for running GMRecords jobs using AWS Batch with Fargate, featuring two separate job queues for different workload types.

## Architecture

The infrastructure includes:
- **VPC** with 2 subnets across 2 availability zones
- **Two AWS Batch Compute Environments**:
  - **Download Queue**: Limited to 10 concurrent vCPUs for data download tasks
  - **Process Queue**: High concurrency (up to 10,000 vCPUs) for data processing tasks
- **ECR Repository** for container images with lifecycle policies
- **IAM Roles** with least-privilege permissions
- **CloudWatch Logs** for centralized logging (separate log groups per queue)
- **Security Group** with minimal required access

## Queue Configuration

### Download Queue (`gmrecords_download`)
- **Purpose**: Data download and lightweight tasks
- **Concurrency**: Limited to 10 concurrent vCPUs (configurable via `download_max_vcpus`)
- **Resources**: 1 vCPU, 4GB RAM per job
- **Log Group**: `batch/gmrecords/download`

### Process Queue (`gmrecords_process`)
- **Purpose**: Data processing and compute-intensive tasks
- **Concurrency**: High concurrency up to 10,000 vCPUs (configurable via `max_vcpus`)
- **Resources**: 2 vCPUs, 8GB RAM per job
- **Log Group**: `batch/gmrecords/process`

## Prerequisites

- AWS CLI configured with appropriate credentials
- Terraform >= 1.0
- Docker (for building and pushing images to ECR)

## Configuration

### Required Variables

Set these variables in `terraform.tfvars`:

```hcl
deployment_name = "gmrecords"
aws_region      = "us-west-2"
```

### Optional Variables

You can customize these in `terraform.tfvars`:

```hcl
vpc_cidr_block       = "10.0.0.0/16"    # VPC CIDR block
max_vcpus           = 10000             # Maximum vCPUs for Process queue
download_max_vcpus  = 10                # Maximum vCPUs for Download queue
log_retention_days  = 180               # CloudWatch log retention
```

## Deployment

1. **Initialize Terraform:**
   ```bash
   terraform init
   ```

2. **Plan the deployment:**
   ```bash
   terraform plan
   ```

3. **Apply the configuration:**
   ```bash
   terraform apply
   ```

## Post-Deployment

After successful deployment:

1. **Build and push your Docker image:**
   ```bash
   # Get ECR login command
   aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-west-2.amazonaws.com

   # Build and push image
   docker build -t gmrecords .
   docker tag gmrecords:latest <account-id>.dkr.ecr.us-west-2.amazonaws.com/gmrecords:latest
   docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/gmrecords:latest
   ```

2. **Submit jobs to the appropriate Batch queue:**

   **For Download Jobs:**
   ```bash
   aws batch submit-job \
     --job-name "download-job-$(date +%s)" \
     --job-queue "gmrecords_download" \
     --job-definition "gmrecords_download_jobdef"
   ```

   **For Process Jobs:**
   ```bash
   aws batch submit-job \
     --job-name "process-job-$(date +%s)" \
     --job-queue "gmrecords_process" \
     --job-definition "gmrecords_process_jobdef"
   ```

## Security Features

- **Least-privilege IAM policies** instead of broad permissions
- **KMS encryption** for ECR repositories
- **VPC isolation** with private subnets
- **Spot pricing** for cost optimization
- **Image scanning** enabled on ECR

## Monitoring

- CloudWatch logs are configured for all Batch jobs
- ECR lifecycle policies automatically clean up old images
- Default tags applied to all resources for cost tracking

## Cleanup

To destroy the infrastructure:

```bash
terraform destroy
```

**Note:** Make sure to delete any ECR images first, as Terraform cannot destroy non-empty repositories.

## Changes from Previous Version

- Updated AWS provider from 3.x to 5.x
- Updated Terraform version requirement to >= 1.0
- Replaced hardcoded availability zones with dynamic lookup
- Improved IAM security with specific S3 permissions
- Added resource tagging strategy
- Converted JSON configuration to jsonencode() for better maintainability
- Added ECR lifecycle policies
- Added input validation for variables
- Added comprehensive outputs
- **NEW**: Split into two separate queues:
  - Download queue with limited concurrency (10 vCPUs)
  - Process queue with high concurrency (up to 10,000 vCPUs)
- **NEW**: Separate job definitions optimized for each queue type
- **NEW**: Separate CloudWatch log groups for better monitoring
- Improved documentation
