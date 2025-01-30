resource "aws_cloudwatch_log_group" "attendance_backend" {
  name              = "/ecs/${local.app_prefix}"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_group" "attendance_migration_lambda" {
  name              = "/aws/lambda/${aws_lambda_function.attendance_migration.function_name}"
  retention_in_days = 7
}
