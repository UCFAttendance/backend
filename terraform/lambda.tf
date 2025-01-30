resource "aws_lambda_function" "attendance_migration" {
  function_name = "attendance_migration"
  role          = aws_iam_role.lambda_migration_role.arn
  package_type  = "Image"
  image_uri     = "${data.aws_ecr_repository.attendance_backend.repository_url}:${var.image_tag}"
  memory_size   = 256
  timeout       = 300
  vpc_config {
    subnet_ids         = data.terraform_remote_state.core-infra.outputs.public-subnet-ids
    security_group_ids = [aws_security_group.service_lb_sg.id]
  }
  image_config {
    command           = ["migrate.handler"]
    working_directory = "/app"
  }
  environment {
    variables = local.environment_variables
  }
}
