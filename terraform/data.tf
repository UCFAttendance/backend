data "terraform_remote_state" "core-infra" {
  backend = "remote"

  config = {
    organization = "attendance"
    workspaces = {
      name = "354918382277-core-infra"
    }
  }
}

data "aws_ecs_cluster" "attendance_cluster" {
  cluster_name = data.terraform_remote_state.core-infra.outputs.ecs-cluster-name
}

data "aws_lb" "attendance_alb" {
  arn = data.terraform_remote_state.core-infra.outputs.alb-arn
}

data "aws_lb_listener" "attendance_alb_443" {
  load_balancer_arn = data.aws_lb.attendance_alb.arn
  port              = 443
}

data "aws_ecr_repository" "attendance_backend" {
  name = data.terraform_remote_state.core-infra.outputs.backend-repository-name
}

data "aws_db_instance" "attendance_db" {
  db_instance_identifier = data.terraform_remote_state.core-infra.outputs.rds-indentifier
}

data "aws_s3_bucket" "attendance_static_bucket" {
  bucket = replace(data.terraform_remote_state.core-infra.outputs.attendance-images-bucket, "arn:aws:s3:::", "")
}

data "aws_elasticache_replication_group" "attendance_redis_replication_group" {
  replication_group_id = data.terraform_remote_state.core-infra.outputs.redis-cluster-id
}

# TODO: Replace admin_url and secret_key with secrets manager
data "aws_ssm_parameter" "admin_url" {
  name = "/application/backend/admin-url"
}

data "aws_ssm_parameter" "secret_key" {
  name = "/application/backend/secret-key"
}

data "aws_ssm_parameter" "sentry_dns" {
  name = "/application/backend/sentry-dns"
}
