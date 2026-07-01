output "environment" {
  description = "Environment name"
  value = var.environment
}

output "aws_region" {
  description = "AWS region"
  value = var.aws_region
}

output "project_name" {
  description = "Project name"
  value = var.project_name
}

#example bucket
output "example_bucket_name" {
  description = "Name of example s3 bucket"
  value = aws_s3_bucket.example.id
}