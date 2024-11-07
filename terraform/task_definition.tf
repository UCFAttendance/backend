resource "aws_ecs_task_definition" "task_definition" {
  family                   = "${var.app_prefix}-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc" // required for Fargate
  cpu                      = "256"    // Choose Fargate-compatible values
  memory                   = "512"

  container_definitions = jsonencode([
    {
      name  = "${var.app_prefix}-container"
      image = "nginx:latest"
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
