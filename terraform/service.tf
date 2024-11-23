locals {
  app_prefix = "attendance-backend"
}

resource "aws_security_group" "service_lb_sg" {
  name        = "${local.app_prefix}-service-lb-sg"
  description = "Allow HTTP inbound traffic"
  vpc_id      = data.terraform_remote_state.core-infra.outputs.vpc-id

  ingress {
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = data.aws_lb.attendance_alb.security_groups
  }
}

resource "aws_lb_target_group" "app_target_group" {
  name        = "${local.app_prefix}-target-group"
  port        = 80
  target_type = "ip"
  protocol    = "HTTP"
  vpc_id      = data.terraform_remote_state.core-infra.outputs.vpc-id
}

resource "aws_lb_listener_rule" "app_listener_rule" {
  listener_arn = data.aws_lb_listener.attendance_alb_443.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app_target_group.arn
  }

  condition {
    path_pattern {
      values = ["/api/*", "/api-auth/*"]
    }
  }
}

resource "aws_ecs_service" "attendance_backend" {
  name            = local.app_prefix
  cluster         = data.aws_ecs_cluster.attendance_cluster.id
  task_definition = aws_ecs_task_definition.attendance_backend.arn
  desired_count   = 1

  capacity_provider_strategy {
    capacity_provider = "FARGATE_SPOT"
    weight            = 1
  }

  network_configuration {
    subnets          = data.terraform_remote_state.core-infra.outputs.private-subnet-ids
    security_groups  = [aws_security_group.service_lb_sg.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app_target_group.arn
    container_name   = "${local.app_prefix}-container"
    container_port   = 80
  }
}
