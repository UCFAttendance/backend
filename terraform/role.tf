resource "aws_iam_role" "backend_execution_role" {
  name = "backend-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "backend_execution_policy" {
  name        = "BackendExecutionPolicy"
  description = "Policy to allow ECS task execution for backend service"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        "Action" : [
          "ecr:GetAuthorizationToken",
        ]
        "Effect" : "Allow"
        "Resource" : "*"
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
        ],
        "Resource" : data.aws_ecr_repository.attendance_backend.arn
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        "Resource" : "arn:aws:logs:*:*:log-group:/ecs/${local.app_prefix}:*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_policy_attachment" {
  role       = aws_iam_role.backend_execution_role.name
  policy_arn = aws_iam_policy.backend_execution_policy.arn
}

resource "aws_iam_role" "backend_task_role" {
  name = "backend-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = [
            "ecs-tasks.amazonaws.com",
          ]
        }
      }
    ]
  })
}

resource "aws_iam_policy" "backend_task_policy" {
  name        = "BackendECSTaskPolicy"
  description = "Policy to allow access to RDS and S3 for backend service"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        "Effect" : "Allow",
        "Action" : [
          "secretsmanager:GetSecretValue",
          "secretsmanager:PutResourcePolicy",
          "secretsmanager:DescribeSecret",
          "secretsmanager:TagResource"
        ],
        "Resource" : data.aws_db_instance.attendance_db.master_user_secret[0].secret_arn
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "kms:Decrypt"
        ],
        "Resource" : "arn:aws:kms:${var.aws_region}:${data.aws_db_instance.attendance_db.master_user_secret[0].kms_key_id}"
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "s3:*"
        ],
        "Resource" : [
          data.aws_s3_bucket.attendance_static_bucket.arn,
          "${data.aws_s3_bucket.attendance_static_bucket.arn}/*"
        ]
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:BatchGetItem",
          "dynamodb:BatchWriteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ],
        "Resource" : data.aws_dynamodb_table.attendance.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "backend_task_policy_attachment" {
  role       = aws_iam_role.backend_task_role.name
  policy_arn = aws_iam_policy.backend_task_policy.arn
}
