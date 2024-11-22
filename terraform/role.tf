resource "aws_iam_role" "backend_execution_role" {
  name = "ecs-execution-role"

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

resource "aws_iam_policy" "ecr_pull_policy" {
  name        = "ECRPullPolicy"
  description = "Policy to allow ECS to pull from ECR"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability"
        ]
        Effect   = "Allow"
        Resource = data.terraform_remote_state.core-infra.outputs.repository-arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecr_pull_policy_attachment" {
  role       = aws_iam_role.backend_execution_role.name
  policy_arn = aws_iam_policy.ecr_pull_policy.arn
}
