resource "aws_cloudwatch_log_group" "batch_group" {
  name              = "batch/${var.deployment_name}"
  retention_in_days = 180
}
