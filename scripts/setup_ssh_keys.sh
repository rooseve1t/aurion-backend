#!/usr/bin/env bash
# setup_ssh_keys.sh — генерирует SSH-ключевую пару и копирует на оба сервера.
# Использование: bash scripts/setup_ssh_keys.sh
set -euo pipefail

KEY_PATH="${HOME}/.ssh/aurion_deploy"
BACKEND_HOST="${BACKEND_HOST:-62.152.55.52}"
FRONTEND_HOST="${FRONTEND_HOST:-109.61.108.116}"
DEPLOY_USER="${DEPLOY_USER:-root}"

if [ ! -f "$KEY_PATH" ]; then
  echo "Generating SSH key pair at $KEY_PATH ..."
  ssh-keygen -t ed25519 -C "aurion-deploy" -f "$KEY_PATH" -N ""
else
  echo "Key already exists at $KEY_PATH, skipping generation."
fi

echo ""
echo "Copying public key to backend server ($BACKEND_HOST) ..."
ssh-copy-id -i "${KEY_PATH}.pub" "${DEPLOY_USER}@${BACKEND_HOST}"

echo "Copying public key to frontend server ($FRONTEND_HOST) ..."
ssh-copy-id -i "${KEY_PATH}.pub" "${DEPLOY_USER}@${FRONTEND_HOST}"

echo ""
echo "Disabling password auth on both servers ..."
for HOST in "$BACKEND_HOST" "$FRONTEND_HOST"; do
  ssh -i "$KEY_PATH" "${DEPLOY_USER}@${HOST}" \
    "sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config && systemctl reload sshd"
done

echo ""
echo "Done. Add the private key to GitHub Actions secret SSH_PRIVATE_KEY:"
echo ""
cat "$KEY_PATH"
