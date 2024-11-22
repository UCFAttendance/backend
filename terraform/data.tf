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

# repository-arn
data "aws_ecr_repository" "attendance_backend" {
  name = data.terraform_remote_state.core-infra.outputs.backend-repository-name
}
