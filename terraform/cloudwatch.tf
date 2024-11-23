resource "aws_cloudwatch_log_group" "attendance_backend" {
  name              = "/ecs/${local.app_prefix}"
  retention_in_days = 7
}
