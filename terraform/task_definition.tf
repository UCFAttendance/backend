locals {
  redis_address = data.aws_elasticache_cluster.attendance_redis_cluster.cache_nodes[0].address
  redis_port    = data.aws_elasticache_cluster.attendance_redis_cluster.cache_nodes[0].port
  environment_variables = {
    DJANGO_SETTINGS_MODULE            = "config.settings.production",
    DJANGO_ALLOWED_HOSTS              = "*",
    DJANGO_SECURE_SSL_REDIRECT        = "False",
    DJANGO_ACCOUNT_ALLOW_REGISTRATION = "True",
    WEB_CONCURRENCY                   = "4",
    DJANGO_AWS_STORAGE_BUCKET_NAME    = "${data.aws_s3_bucket.attendance_static_bucket.bucket}",
    DJANGO_MEDIA_BUCKET_NAME          = "${data.aws_s3_bucket.attendance_static_bucket.bucket}",
    DJANGO_ADMIN_URL                  = "${data.aws_ssm_parameter.admin_url.value}",
    DJANGO_SECRET_KEY                 = "${data.aws_ssm_parameter.secret_key.value}",
    SENTRY_DSN                        = "${data.aws_ssm_parameter.sentry_dns.value}",
    REDIS_URL                         = "redis://${local.redis_address}:${local.redis_port}",
    DB_SECRET_ARN                     = "${data.aws_db_instance.attendance_db.master_user_secret[0].secret_arn}",
    POSTGRES_HOST                     = "${data.aws_db_instance.attendance_db.address}",
    POSTGRES_PORT                     = "${data.aws_db_instance.attendance_db.port}",
    POSTGRES_DB                       = "${data.aws_db_instance.attendance_db.db_name}",
    POSTGRES_USER                     = "${data.aws_db_instance.attendance_db.master_username}",
  }
}

resource "aws_ecs_task_definition" "attendance_backend" {
  family                   = "${local.app_prefix}-task-definition"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = aws_iam_role.backend_execution_role.arn
  task_role_arn            = aws_iam_role.backend_task_role.arn
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"

  container_definitions = jsonencode([
    {
      name      = "${local.app_prefix}-container"
      image     = "${data.aws_ecr_repository.attendance_backend.repository_url}:${var.image_tag}"
      essential = true
      portMappings = [
        {
          containerPort = 5000
          hostPort      = 5000
        }
      ],
      logConfiguration = {
        logDriver = "awslogs",
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.attendance_backend.name,
          "awslogs-region"        = var.aws_region,
          "awslogs-stream-prefix" = "ecs"
        }
      },
      environment = [
        for key, value in local.environment_variables : {
          name  = tostring(key)
          value = tostring(value)
        }
      ]
    }
  ])
}
