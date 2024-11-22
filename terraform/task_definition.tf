resource "aws_ecs_task_definition" "attendance_backend" {
  family                   = "attendance-backend-definition"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = aws_iam_role.backend_execution_role.arn
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"

  container_definitions = jsonencode([
    {
      name      = local.app_prefix
      image     = "nginx:latest"
      essential = true
      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
        }
      ]
    }
  ])
}
