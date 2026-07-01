#!/usr/bin/env bash
# setup-oidc-role.sh — one-time setup of the GitHub Actions OIDC IAM role
#
# Usage:
#   ./scripts/setup-oidc-role.sh            # loads .env (default)
#   ./scripts/setup-oidc-role.sh .env.prod  # loads a custom env file

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

: "${AWS_REGION:?AWS_REGION is not set in ${ENV_FILE}}"
: "${GITHUB_USERNAME:?GITHUB_USERNAME is not set in ${ENV_FILE}}"
: "${GITHUB_REPO:?GITHUB_REPO is not set in ${ENV_FILE}}"
: "${IAM_ROLE_NAME:?IAM_ROLE_NAME is not set in ${ENV_FILE}}"

echo "==> Verifying AWS credentials..."
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "    Account: ${AWS_ACCOUNT_ID}"

OIDC_PROVIDER_URL="token.actions.githubusercontent.com"
OIDC_PROVIDER_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:oidc-provider/${OIDC_PROVIDER_URL}"

# Step 3a — Create OIDC Identity Provider (once per AWS account)
echo ""
echo "==> Creating OIDC Identity Provider..."
CREATE_OUTPUT=$(aws iam create-open-id-connect-provider \
  --url "https://${OIDC_PROVIDER_URL}" \
  --client-id-list "sts.amazonaws.com" \
  --thumbprint-list "6938fd4d98bab03faadb97b34396831e3780aea1" 2>&1) && {
  echo "    Created: ${OIDC_PROVIDER_ARN}"
} || {
  if echo "$CREATE_OUTPUT" | grep -q "EntityAlreadyExists"; then
    echo "    Already exists — skipping."
  else
    echo "Error: ${CREATE_OUTPUT}"
    exit 1
  fi
}

# Step 3b — Write trust policy to temp file
echo ""
echo "==> Writing trust policy..."
TRUST_POLICY_FILE=$(mktemp /tmp/trust-policy.XXXXXX)
trap 'rm -f "$TRUST_POLICY_FILE"' EXIT

cat > "$TRUST_POLICY_FILE" <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "${OIDC_PROVIDER_ARN}"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "${OIDC_PROVIDER_URL}:aud": "sts.amazonaws.com",
          "${OIDC_PROVIDER_URL}:sub": "repo:${GITHUB_USERNAME}/${GITHUB_REPO}:ref:refs/heads/main"
        }
      }
    }
  ]
}
EOF
echo "    Scoped to: ${GITHUB_USERNAME}/${GITHUB_REPO} (main branch only)"

# Step 3c — Create the IAM role
echo ""
echo "==> Creating IAM role: ${IAM_ROLE_NAME}"
aws iam create-role \
  --role-name "$IAM_ROLE_NAME" \
  --assume-role-policy-document "file://${TRUST_POLICY_FILE}"

# Step 3d — Attach state management policies
echo ""
echo "==> Attaching state management policies..."
aws iam attach-role-policy \
  --role-name "$IAM_ROLE_NAME" \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
echo "    Attached: AmazonS3FullAccess"

aws iam attach-role-policy \
  --role-name "$IAM_ROLE_NAME" \
  --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
echo "    Attached: AmazonDynamoDBFullAccess"

# Step 3e — Print the role ARN
echo ""
ROLE_ARN=$(aws iam get-role \
  --role-name "$IAM_ROLE_NAME" \
  --query 'Role.Arn' \
  --output text)

echo "Done. Add this value as a GitHub Secret:"
echo "  AWS_ROLE_ARN = ${ROLE_ARN}"
