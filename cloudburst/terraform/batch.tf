# Download Compute Environment (Limited Concurrency)
resource "aws_batch_compute_environment" "download_compute" {
  compute_environment_name = "${var.deployment_name}_download_compute"
  state                    = "ENABLED"
  type                     = "MANAGED"

  compute_resources {
    type = "FARGATE"

  # allocation_strategy and bid_percentage are not valid for FARGATE

    max_vcpus = var.download_max_vcpus

    security_group_ids = [
      aws_security_group.aws_sec_grp.id
    ]

    subnets = [
      aws_subnet.subnet1.id,
      aws_subnet.subnet2.id
    ]

  # tags block is not supported for Fargate compute_resources
  }

  service_role = aws_iam_role.aws_batch_service_role.arn
  depends_on   = [aws_iam_role_policy_attachment.aws_batch_service_role]

  tags = {
    Name    = "${var.deployment_name}_download_compute_env"
    Purpose = "download"
  }
}

# Process Compute Environment (High Concurrency)
resource "aws_batch_compute_environment" "process_compute" {
  compute_environment_name = "${var.deployment_name}_process_compute"
  state                    = "ENABLED"
  type                     = "MANAGED"

  compute_resources {
    type = "FARGATE"

  # allocation_strategy and bid_percentage are not valid for FARGATE

    max_vcpus = var.max_vcpus

    security_group_ids = [
      aws_security_group.aws_sec_grp.id
    ]

    subnets = [
      aws_subnet.subnet1.id,
      aws_subnet.subnet2.id
    ]

  # tags block is not supported for Fargate compute_resources
  }

  service_role = aws_iam_role.aws_batch_service_role.arn
  depends_on   = [aws_iam_role_policy_attachment.aws_batch_service_role]

  tags = {
    Name    = "${var.deployment_name}_process_compute_env"
    Purpose = "process"
  }
}

# Download Job Queue (Limited Concurrency)
resource "aws_batch_job_queue" "download_queue" {
  name     = "${var.deployment_name}_download"
  state    = "ENABLED"
  priority = 1

  compute_environment_order {
    order               = 1
    compute_environment = aws_batch_compute_environment.download_compute.arn
  }

  tags = {
    Name    = "${var.deployment_name}_download_queue"
    Purpose = "download"
  }
}

# Process Job Queue (High Concurrency)
resource "aws_batch_job_queue" "process_queue" {
  name     = "${var.deployment_name}_process"
  state    = "ENABLED"
  priority = 1

  compute_environment_order {
    order               = 1
    compute_environment = aws_batch_compute_environment.process_compute.arn
  }

  tags = {
    Name    = "${var.deployment_name}_process_queue"
    Purpose = "process"
  }
}

# Download Job Definition
resource "aws_batch_job_definition" "download_jobdef" {
  name = "${var.deployment_name}_download_jobdef"
  type = "container"

  platform_capabilities = ["FARGATE"]

  retry_strategy {
    attempts = 3

    evaluate_on_exit {
      on_status_reason = "Essential container in task exited"
      action           = "EXIT"
    }

    evaluate_on_exit {
      on_status_reason = "*"
      action           = "RETRY"
    }
  }

  timeout {
    attempt_duration_seconds = 72000
  }

  depends_on = [
    aws_iam_role_policy_attachment.ecs_task_exec_role,
    aws_iam_role_policy.ecs_task_s3_policy,
    aws_iam_role_policy_attachment.ecs_task_exec_role_cw
  ]

  container_properties = jsonencode({
    command = []
    image   = "${local.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/${var.deployment_name}:latest"

    fargatePlatformConfiguration = {
      platformVersion = "LATEST"
    }

    resourceRequirements = [
      { type = "VCPU", value = "1" },
      { type = "MEMORY", value = "4096" }
    ]

    executionRoleArn = aws_iam_role.ecs_task_exec_role.arn
    jobRoleArn       = aws_iam_role.ecs_task_exec_role.arn

    environment = [
      { name = "AWS_REGION", value = var.aws_region },
      { name = "BUCKET_NAME", value = "" },
      { name = "MODE_STR", value = "download" },
      { name = "JOB_TYPE", value = "download" }
    ]

    networkConfiguration = {
      assignPublicIp = "ENABLED"
    }

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"  = "batch/${var.deployment_name}/download"
        "awslogs-region" = var.aws_region
      }
    }
  })

  tags = {
    Name    = "${var.deployment_name}_download_jobdef"
    Purpose = "download"
  }
}

# Process Job Definition
resource "aws_batch_job_definition" "process_jobdef" {
  name = "${var.deployment_name}_process_jobdef"
  type = "container"

  platform_capabilities = ["FARGATE"]

  retry_strategy {
    attempts = 3

    evaluate_on_exit {
      on_status_reason = "Essential container in task exited"
      action           = "EXIT"
    }

    evaluate_on_exit {
      on_status_reason = "*"
      action           = "RETRY"
    }
  }

  timeout {
    attempt_duration_seconds = 72000
  }

  depends_on = [
    aws_iam_role_policy_attachment.ecs_task_exec_role,
    aws_iam_role_policy.ecs_task_s3_policy,
    aws_iam_role_policy_attachment.ecs_task_exec_role_cw
  ]

  container_properties = jsonencode({
    command = []
    image   = "${local.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/${var.deployment_name}:latest"

    fargatePlatformConfiguration = {
      platformVersion = "LATEST"
    }

    resourceRequirements = [
      { type = "VCPU", value = "2" },
      { type = "MEMORY", value = "8192" }
    ]

    executionRoleArn = aws_iam_role.ecs_task_exec_role.arn
    jobRoleArn       = aws_iam_role.ecs_task_exec_role.arn

    environment = [
      { name = "AWS_REGION", value = var.aws_region },
      { name = "BUCKET_NAME", value = var.bucket_name },
      { name = "MODE_STR", value = "process" },
      { name = "JOB_TYPE", value = "process" }
    ]

    networkConfiguration = {
      assignPublicIp = "ENABLED"
    }

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"  = "batch/${var.deployment_name}/process"
        "awslogs-region" = var.aws_region
      }
    }
  })

  tags = {
    Name    = "${var.deployment_name}_process_jobdef"
    Purpose = "process"
  }
}
