resource "aws_ecs_service" "ecs_service" {
  name            = "${var.app_prefix}-service"
  cluster         = aws_ecs_cluster.ecs_cluster.id
  task_definition = aws_ecs_task_definition.task_definition.arn
  desired_count   = 1

  # Use Fargate Spot by specifying the capacity provider
  capacity_provider_strategy {
    capacity_provider = "FARGATE_SPOT"
    weight            = 1
  }

  network_configuration {
    subnets          = aws_subnet.private[*].id // Use private subnets for security
    security_groups  = [aws_security_group.lb_sg.id]
    assign_public_ip = true // Set to true if your tasks need public IPs
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app_target_group.arn
    container_name   = "${var.app_prefix}-container"
    container_port   = 80
  }

  depends_on = [
    aws_lb_target_group.app_target_group
  ]
}
