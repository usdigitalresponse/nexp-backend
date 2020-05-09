# Variables --------------------------------------------------------------------
variable service { default = "nexp-backend" }
variable deploy_bucket { default = "usdr.deploy-artifacts" }
variable ssm_prefix { default = "nexp" }
variable deploy_policy_name { default = "NEXP-DeployPolicy" }
variable deploy_username { default = "nexp-deploy-user" }
variable tags { default = {
  Environment = "Production",
  ManagedBy   = "terraform"
  Project     = "NEXP / Health Work Connect"
} }

# Preconfigured ----------------------------------------------------------------
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
