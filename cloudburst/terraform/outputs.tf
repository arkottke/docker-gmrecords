output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = aws_ecr_repository.ecr_repo.repository_url
}

# Download Queue Outputs
output "download_job_queue_arn" {
  description = "ARN of the download AWS Batch job queue"
  value       = aws_batch_job_queue.download_queue.arn
}

output "download_job_queue_name" {
  description = "Name of the download AWS Batch job queue"
  value       = aws_batch_job_queue.download_queue.name
}

output "download_job_definition_arn" {
  description = "ARN of the download AWS Batch job definition"
  value       = aws_batch_job_definition.download_jobdef.arn
}

# Process Queue Outputs
output "process_job_queue_arn" {
  description = "ARN of the process AWS Batch job queue"
  value       = aws_batch_job_queue.process_queue.arn
}

output "process_job_queue_name" {
  description = "Name of the process AWS Batch job queue"
  value       = aws_batch_job_queue.process_queue.name
}

output "process_job_definition_arn" {
  description = "ARN of the process AWS Batch job definition"
  value       = aws_batch_job_definition.process_jobdef.arn
}

output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.vpc.id
}

output "subnet_ids" {
  description = "IDs of the subnets"
  value       = [aws_subnet.subnet1.id, aws_subnet.subnet2.id]
}

output "security_group_id" {
  description = "ID of the security group"
  value       = aws_security_group.aws_sec_grp.id
}

# CloudWatch Log Groups
output "download_log_group_name" {
  description = "Name of the download CloudWatch log group"
  value       = aws_cloudwatch_log_group.download_batch_group.name
}

output "process_log_group_name" {
  description = "Name of the process CloudWatch log group"
  value       = aws_cloudwatch_log_group.process_batch_group.name
}

output "iam_execution_role_arn" {
  description = "ARN of the ECS task execution role"
  value       = aws_iam_role.ecs_task_exec_role.arn
}

output "availability_zones" {
  description = "Availability zones used for the deployment"
  value       = local.azs
}
