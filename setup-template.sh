#!/bin/bash

# === Configuration ===
REPO_NAME="python-uv-template"
DESCRIPTION="A Python starter template using uv, GitHub Actions, and Spaces CI"
PRIVATE=false           # set to true to create a private repo
TEMPLATE=true           # make it a template repo
LICENSE="MIT"
USERNAME=$(gh api user --jq .login)

# === Check requirements ===
command -v gh >/dev/null 2>&1 || { echo >&2 "GitHub CLI (gh) is required."; exit 1; }
command -v git >/dev/null 2>&1 || { echo >&2 "Git is required."; exit 1; }

# === Initialize local git repo ===
unzip -q myproject_template_with_license.zip -d "$REPO_NAME"
cd "$REPO_NAME" || exit
git init
git add .
git commit -m "Initial commit"

# === Create GitHub repo ===
gh repo create "$USERNAME/$REPO_NAME" \
  --description "$DESCRIPTION" \
  $( [ "$PRIVATE" = true ] && echo "--private" || echo "--public" ) \
  $( [ "$TEMPLATE" = true ] && echo "--template" ) \
  --source=. --remote=origin --push

# === Done ===
echo "✅ GitHub repository '$REPO_NAME' created and pushed successfully."
