#!/bin/bash
set -e

echo "----------------------------------------"
echo " Shift Left Security Check"
echo " Terraform + OPA/Rego Policy Evaluation"
echo "----------------------------------------"

echo ""
echo "[1/3] Initializing Terraform..."
terraform init -input=false -no-color

echo ""
echo "[2/3] Generating Terraform plan..."
terraform plan -out=tfplan -no-color
terraform show -json tfplan > tfplan.json

echo ""
echo "[3/3] Evaluating plan against OPA policies..."
conftest test tfplan.json --policy policies/

echo ""
echo "All policies passed. Safe to deploy."
