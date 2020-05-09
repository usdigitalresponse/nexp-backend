# Terraform Provider

terraform {
  required_version = ">= 0.12.13"
  required_providers {
    aws = "2.44.0"
  }

  backend "s3" {
    bucket  = "usdr.terraform"
    key     = "nexp/main.json"
    region  = "us-east-1"
    encrypt = true
  }
}

provider "aws" {
  region = "us-east-1"
}
