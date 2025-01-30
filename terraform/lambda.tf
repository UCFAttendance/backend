resource "aws_lambda_function" "attendance_migration" {
  function_name = "attendance_migration"
  role          = aws_iam_role.backend_task_role.arn
  image_uri     = "${data.aws_ecr_repository.attendance_backend.repository_url}:${var.image_tag}"
  memory_size   = 256
  timeout       = 300
  image_config {
    command = ["python", "/app/manage.py", "migrate"]
  }
}
