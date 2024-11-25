locals {
  app_prefix = "attendance-backend"
}

resource "aws_security_group" "service_lb_sg" {
  name        = "${local.app_prefix}-service-lb-sg"
  description = "Allow HTTP inbound traffic"
  vpc_id      = data.terraform_remote_state.core-infra.outputs.vpc-id

  ingress {
    from_port       = 5000
    to_port         = 5000
    protocol        = "tcp"
    security_groups = data.aws_lb.attendance_alb.security_groups
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group_rule" "db_ingress_from_ecs" {
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  security_group_id        = data.aws_db_instance.attendance_db.vpc_security_groups[0]
  source_security_group_id = aws_security_group.service_lb_sg.id
}

resource "aws_security_group_rule" "redis_ingress_from_ecs" {
  type                     = "ingress"
  from_port                = 6379
  to_port                  = 6379
  protocol                 = "tcp"
  security_group_id        = data.aws_elasticache_cluster.attendance_redis.security_group_ids[0]
  source_security_group_id = aws_security_group.service_lb_sg.id

}

resource "aws_lb_target_group" "app_target_group" {
  name        = "${local.app_prefix}-tg"
  port        = 5000
  target_type = "ip"
  protocol    = "HTTP"
  vpc_id      = data.terraform_remote_state.core-infra.outputs.vpc-id

  health_check {
    path                = "/health/"
    protocol            = "HTTP"
    port                = "traffic-port"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
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
      values = ["/api/*", "/api-auth/*", "/${data.aws_ssm_parameter.admin_url.value}/*"]
    }
  }
}

resource "aws_ecs_service" "attendance_backend" {
  name            = local.app_prefix
  cluster         = data.aws_ecs_cluster.attendance_cluster.id
  task_definition = aws_ecs_task_definition.attendance_backend.arn
  desired_count   = 1

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  capacity_provider_strategy {
    capacity_provider = "FARGATE_SPOT"
    weight            = 1
  }

  network_configuration {
    subnets          = data.terraform_remote_state.core-infra.outputs.public-subnet-ids
    security_groups  = [aws_security_group.service_lb_sg.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app_target_group.arn
    container_name   = "${local.app_prefix}-container"
    container_port   = 5000
  }

  lifecycle {
    ignore_changes = [desired_count]
  }
}
