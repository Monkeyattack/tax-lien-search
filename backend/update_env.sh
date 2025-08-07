#!/bin/bash
# Script to update environment variables on VPS

# Add Google Maps API key if not already present
if ! grep -q "GOOGLE_MAPS_API_KEY" /var/www/tax-lien-search/backend/.env; then
    echo "" >> /var/www/tax-lien-search/backend/.env
    echo "# Google Maps API" >> /var/www/tax-lien-search/backend/.env
    echo "GOOGLE_MAPS_API_KEY=AIzaSyClDyNdQritdtXYGDbCi_sFJFpQrhx5TRw" >> /var/www/tax-lien-search/backend/.env
    echo "Google Maps API key added to .env"
else
    # Update existing key
    sed -i 's/^GOOGLE_MAPS_API_KEY=.*/GOOGLE_MAPS_API_KEY=AIzaSyClDyNdQritdtXYGDbCi_sFJFpQrhx5TRw/' /var/www/tax-lien-search/backend/.env
    echo "Google Maps API key updated in .env"
fi