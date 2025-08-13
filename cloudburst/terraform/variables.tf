variable "deployment_name" {
  description = "Deployment Name"
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.deployment_name))
    error_message = "Deployment name must contain only lowercase letters, numbers, and hyphens."
  }
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"

  validation {
    condition = contains([
      "us-east-1", "us-east-2", "us-west-1", "us-west-2",
      "eu-west-1", "eu-west-2", "eu-central-1",
      "ap-southeast-1", "ap-southeast-2", "ap-northeast-1"
    ], var.aws_region)
    error_message = "AWS region must be a valid region."
  }
}

variable "bucket_name" {
  description = "S3 bucket name"
  type        = string
}

variable "vpc_cidr_block" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"

  validation {
    condition     = can(cidrhost(var.vpc_cidr_block, 0))
    error_message = "VPC CIDR block must be a valid IPv4 CIDR."
  }
}

variable "max_vcpus" {
  description = "Maximum number of vCPUs for the compute environment"
  type        = number
  default     = 10000

  validation {
    condition     = var.max_vcpus > 0 && var.max_vcpus <= 50000
    error_message = "max_vcpus must be between 1 and 50000."
  }
}

variable "log_retention_days" {
  description = "Number of days to retain CloudWatch logs"
  type        = number
  default     = 180

  validation {
    condition = contains([
      1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1096, 1827, 2192, 2557, 2922, 3288, 3653
    ], var.log_retention_days)
    error_message = "log_retention_days must be a valid CloudWatch Logs retention period."
  }
}

variable "download_max_vcpus" {
  description = "Maximum number of vCPUs for the download queue compute environment"
  type        = number
  default     = 10

  validation {
    condition     = var.download_max_vcpus > 0 && var.download_max_vcpus <= 1000
    error_message = "download_max_vcpus must be between 1 and 1000."
  }
}
