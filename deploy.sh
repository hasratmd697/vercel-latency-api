#!/bin/bash

echo "🚀 Deploying eShop Telemetry API to Vercel..."

# Check if vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Deploy to Vercel
echo "📦 Deploying to production..."
vercel --prod

echo "✅ Deployment complete!"
echo ""
echo "Test your deployment with:"
echo "curl -X POST https://your-deployment-url.vercel.app/api/telemetry \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"regions\":[\"apac\",\"emea\"],\"threshold_ms\":150}'"
