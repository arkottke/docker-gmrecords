# CloudWatch Log Group for Download Jobs
resource "aws_cloudwatch_log_group" "download_batch_group" {
  name              = "batch/${var.deployment_name}/download"
  retention_in_days = var.log_retention_days

  tags = {
    Name        = "${var.deployment_name}_download_batch_logs"
    Environment = var.deployment_name
    Purpose     = "download"
  }
}

# CloudWatch Log Group for Process Jobs
resource "aws_cloudwatch_log_group" "process_batch_group" {
  name              = "batch/${var.deployment_name}/process"
  retention_in_days = var.log_retention_days

  tags = {
    Name        = "${var.deployment_name}_process_batch_logs"
    Environment = var.deployment_name
    Purpose     = "process"
  }
}
