variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name used to namespace all resources"
  type        = string
  default     = "your-project"
}

variable "state_bucket" {
  description = "S3 bucket name for Terraform remote state (must be globally unique)"
  type        = string
  default     = "terraform-state-your-project"
}

variable "lock_table" {
  description = "DynamoDB table name for Terraform state locking"
  type        = string
  default     = "terraform-state-lock-your-project"
}
