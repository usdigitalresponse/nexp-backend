# Resources to construct on AWS

# Permissions
data "aws_iam_policy_document" "deploy-user" {
  statement {
    effect = "Allow"
    actions = [
      "iam:PassRole",
      "iam:GetRole*",
      "iam:CreateRole",
      "iam:PutRolePolicy",
      "iam:DeleteRolePolicy",
      "iam:DeleteRole",
      "iam:AttachRolePolicy"
    ]
    resources = ["*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "cloudformation:CreateStack",
      "cloudformation:DescribeStacks",
      "cloudformation:DescribeStackEvents",
      "cloudformation:DescribeStackResource",
      "cloudformation:DescribeStackResources",
      "cloudformation:DeleteStack",
      "cloudformation:UpdateStack",
      "cloudformation:ListStackResources"
    ]
    resources = [
      "arn:aws:cloudformation:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:stack/${var.service}*"
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "cloudformation:ValidateTemplate"
    ]
    resources = ["*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "s3:*"
    ]
    resources = [
      "arn:aws:s3:::${var.deploy_bucket}",
      "arn:aws:s3:::${var.deploy_bucket}/*"
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "s3:ListAllMyBuckets",
      "s3:CreateBucket"
    ]
    resources = ["*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "lambda:GetFunction",
      "lambda:CreateFunction",
      "lambda:DeleteFunction",
      "lambda:UpdateFunctionConfiguration",
      "lambda:UpdateFunctionCode",
      "lambda:ListVersionsByFunction",
      "lambda:PublishVersion",
      "lambda:CreateAlias",
      "lambda:DeleteAlias",
      "lambda:UpdateAlias",
      "lambda:GetFunctionConfiguration",
      "lambda:AddPermission",
      "lambda:RemovePermission",
      "lambda:InvokeFunction",
      "lambda:PublishLayerVersion",
      "lambda:GetLayerVersion",
      "lambda:DeleteLayerVersion",
      "lambda:ListAliases"
    ]
    resources = [
      "arn:aws:lambda:*:${data.aws_caller_identity.current.account_id}:function:nexp*",
      "arn:aws:lambda:*:${data.aws_caller_identity.current.account_id}:layer:*"
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "logs:DescribeLogGroups"
    ]
    resources = [
      "arn:aws:events:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group::log-stream:*",
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "logs:*"
    ]
    resources = [
      "arn:aws:events:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/nexp*:log-stream:*",
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "events:*"
    ]
    resources = [
      "arn:aws:events:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:rule/${var.service}*"
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "ssm:GetParameter*"
    ]
    resources = [
      "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter/${var.ssm_prefix}/*"
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "kms:Decrypt"
    ]
    resources = ["*"]
  }
}

# Policy
resource "aws_iam_policy" "deploy-user" {
  name   = var.deploy_policy_name
  policy = data.aws_iam_policy_document.deploy-user.json
}

# User
resource "aws_iam_user" "deploy-user" {
  name = var.deploy_username
  path = "/system/"
  tags = var.tags
}

# Policy Attachment
resource "aws_iam_user_policy_attachment" "deploy-user" {
  user       = aws_iam_user.deploy-user.name
  policy_arn = aws_iam_policy.deploy-user.arn
}
