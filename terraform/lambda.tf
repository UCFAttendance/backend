resource "aws_lambda_function" "attendance_migration" {
  function_name = "attendance_migration"
  role          = aws_iam_role.backend_task_role.arn
  image_uri     = "${data.aws_ecr_repository.attendance_backend.repository_url}:${var.image_tag}"
  memory_size   = 256
  timeout       = 300
  package_type  = "Image"
  vpc_config {
    subnet_ids         = data.terraform_remote_state.core-infra.outputs.public-subnet-ids
    security_group_ids = [aws_security_group.service_lb_sg.id]
  }
  image_config {
    command = ["python", "/app/manage.py", "migrate"]
  }
}
