#!/usr/bin/env bash
# bootstrap-state.sh — one-time setup of Terraform remote state infrastructure
#
# Usage:
#   ./scripts/bootstrap-state.sh            # loads .env (default)
#   ./scripts/bootstrap-state.sh .env.prod  # loads a custom env file

set -euo pipefail

ENV_FILE="${1:-.env}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Error: env file not found: ${ENV_FILE}"
  echo "Copy .env.example to .env and fill in your values."
  exit 1
fi

echo "==> Loading config from ${ENV_FILE}"
# shellcheck source=/dev/null
source "$ENV_FILE"

: "${PROJECT_NAME:?PROJECT_NAME is not set in ${ENV_FILE}}"
: "${AWS_REGION:?AWS_REGION is not set in ${ENV_FILE}}"

STATE_BUCKET="terraform-state-${PROJECT_NAME}"
LOCK_TABLE="terraform-state-lock-${PROJECT_NAME}"

echo "==> Verifying AWS credentials..."
aws sts get-caller-identity --query '[Account, Arn]' --output text

echo ""
echo "==> Creating S3 state bucket: ${STATE_BUCKET}"

aws s3api create-bucket \
  --bucket "$STATE_BUCKET" \
  --region "$AWS_REGION" \

aws s3api put-bucket-versioning \
  --bucket "$STATE_BUCKET" \
  --versioning-configuration Status=Enabled

aws s3api put-bucket-encryption \
  --bucket "$STATE_BUCKET" \
  --server-side-encryption-configuration \
    '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'

aws s3api put-public-access-block \
  --bucket "$STATE_BUCKET" \
  --public-access-block-configuration \
    BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

echo "==> Creating DynamoDB lock table: ${LOCK_TABLE}"

aws dynamodb create-table \
  --table-name "$LOCK_TABLE" \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region "$AWS_REGION"

echo ""
echo "Done. Add these values as GitHub Secrets:"
echo "  TF_STATE_BUCKET = ${STATE_BUCKET}"
echo "  TF_LOCK_TABLE   = ${LOCK_TABLE}"
echo "  AWS_REGION      = ${AWS_REGION}"
