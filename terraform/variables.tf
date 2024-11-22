variable "aws_region" {
  default     = "us-east-1"
  description = "The AWS region to deploy to"
}

variable "image_tag" {
  type        = string
  description = "The tag of the Docker image to deploy"
}
