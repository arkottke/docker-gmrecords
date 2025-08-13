resource "aws_iam_role" "ecs_task_exec_role" {
  name               = "${var.deployment_name}_task_exec_role"
  assume_role_policy = data.aws_iam_policy_document.assume_role_policy_ecs.json
}

data "aws_iam_policy_document" "assume_role_policy_ecs" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "ecs_task_exec_role" {
  role       = aws_iam_role.ecs_task_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy_attachment" "ecs_task_exec_role_cw" {
  role       = aws_iam_role.ecs_task_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}

# Create a more restrictive S3 policy instead of full access
resource "aws_iam_role_policy" "ecs_task_s3_policy" {
  name = "${var.deployment_name}_ecs_task_s3_policy"
  role = aws_iam_role.ecs_task_exec_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::*"
        ]
      }
    ]
  })
}

# Remove the overly broad S3 full access policy
# resource "aws_iam_role_policy_attachment" "ecs_task_exec_role_s3" {
#   role       = aws_iam_role.ecs_task_exec_role.name
#   policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
# }

resource "aws_iam_role" "aws_batch_service_role" {
  name               = "${var.deployment_name}_batch_service_role"
  assume_role_policy = data.aws_iam_policy_document.assume_role_policy_batch.json
}

data "aws_iam_policy_document" "assume_role_policy_batch" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["batch.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "aws_batch_service_role" {
  role       = aws_iam_role.aws_batch_service_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBatchServiceRole"
}
