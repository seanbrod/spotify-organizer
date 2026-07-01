terraform {
  required_version = ">= 1.12.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # bucket, region, and dynamodb_table are passed at runtime via -backend-config flags.
  # In CI/CD these come from GitHub Secrets. Locally, create a backend.hcl from
  # terraform.tfvars.example and run: terraform init -backend-config=backend.hcl
  backend "s3" {
    key     = "dev/terraform.tfstate"
    encrypt = true
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "Terraform"
    }
  }
}

# Example resource — remove or replace with your actual infrastructure
resource "aws_s3_bucket" "example" {
  bucket = "${var.project_name}-${var.environment}-example"

  tags = {
    Name        = "Example bucket"
    Description = "Placeholder — replace with your actual resources"
  }
}
