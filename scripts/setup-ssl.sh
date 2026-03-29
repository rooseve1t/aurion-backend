#!/bin/bash
# SSL Setup for Aurion (api.aurionai.ru)
# Run after backend is deployed and DNS is configured

set -e

echo "🔒 SSL Certificate Setup"
echo "========================"

# 1. Install certbot if needed
if ! command -v certbot &> /dev/null; then
    echo "📦 Installing certbot..."
    apt-get update
    apt-get install -y certbot python3-certbot-nginx
fi

# 2. Obtain certificates
echo "🔐 Obtaining certificates..."
certbot --nginx -d api.aurionai.ru --non-interactive --agree-tos --email admin@aurionai.ru

# 3. Auto-renewal
if ! grep -q "certbot renew" /etc/crontab; then
    echo "0 12 * * * root /usr/bin/certbot renew --quiet" >> /etc/crontab
    echo "✅ Auto-renewal configured"
fi

echo "✅ SSL setup complete!"
echo "Test: curl -v https://api.aurionai.ru/health"
