# GitHub Actions Secrets Setup Guide

This guide explains how to configure the required GitHub Actions secrets for the BDC CI/CD pipeline.

## Required Secrets

Navigate to your GitHub repository → Settings → Secrets and variables → Actions, then add the following secrets:

### Development Environment Secrets

- **DEV_SSH_KEY**: SSH private key for accessing the development server
  - Generate with: `ssh-keygen -t ed25519 -C "bdc-dev-deploy"`
  - Add public key to `~/.ssh/authorized_keys` on dev server

- **DEV_HOST**: Development server hostname or IP address
  - Example: `dev.bdc.com` or `10.0.1.10`

- **DEV_USER**: Username for SSH access to development server
  - Example: `deploy`

- **DEV_DIR**: Directory path for application on development server
  - Default: `/opt/bdc-dev`

### Staging Environment Secrets

- **STAGING_SSH_KEY**: SSH private key for accessing the staging server
  - Generate with: `ssh-keygen -t ed25519 -C "bdc-staging-deploy"`
  - Add public key to `~/.ssh/authorized_keys` on staging server

- **STAGING_HOST**: Staging server hostname or IP address
  - Example: `staging.bdc.com` or `10.0.1.20`

- **STAGING_USER**: Username for SSH access to staging server
  - Example: `deploy`

- **STAGING_DIR**: Directory path for application on staging server
  - Default: `/opt/bdc-staging`

### Production Environment Secrets

- **PROD_SSH_KEY**: SSH private key for accessing the production server
  - Generate with: `ssh-keygen -t ed25519 -C "bdc-prod-deploy"`
  - Add public key to `~/.ssh/authorized_keys` on production server

- **PROD_HOST**: Production server hostname or IP address
  - Example: `app.bdc.com` or `10.0.2.10`

- **PROD_USER**: Username for SSH access to production server
  - Example: `deploy`

- **PROD_DIR**: Directory path for application on production server
  - Default: `/opt/bdc`

- **PROD_URL**: Production application URL for health checks
  - Example: `https://app.bdc.com`

### Container Registry Secrets

These are automatically available if using GitHub Container Registry:
- **GITHUB_TOKEN**: Automatically provided by GitHub Actions
- **github.repository**: Automatically available as context variable

### Optional Monitoring Secrets

- **SLACK_WEBHOOK_URL**: Slack webhook for deployment notifications
- **DISCORD_WEBHOOK_URL**: Discord webhook for deployment notifications

## Setting Up SSH Keys

1. Generate SSH key pair:
   ```bash
   ssh-keygen -t ed25519 -C "bdc-[env]-deploy" -f ~/.ssh/bdc_[env]_deploy
   ```

2. Copy the private key content:
   ```bash
   cat ~/.ssh/bdc_[env]_deploy
   ```

3. Add to GitHub Secrets (paste the entire private key including headers)

4. Copy public key to server:
   ```bash
   ssh-copy-id -i ~/.ssh/bdc_[env]_deploy.pub deploy@[server]
   ```

## Environment Files

Create environment-specific files in the repository:
- `.env.development`
- `.env.staging`
- `.env.production`

**Note**: Do not commit these files. Add them to `.gitignore`.

## Verifying Secrets

To verify your secrets are set correctly:

1. Go to Actions tab in your repository
2. Run the CI/CD workflow manually
3. Check the logs for any authentication errors

## Security Best Practices

1. Use separate SSH keys for each environment
2. Restrict SSH key permissions on servers
3. Use strong passwords for all secrets
4. Rotate secrets regularly
5. Limit access to production secrets
6. Use GitHub environment protection rules for production

## Troubleshooting

### SSH Connection Failed
- Verify SSH key format (include headers)
- Check server firewall allows GitHub Actions IPs
- Ensure correct username and hostname

### Permission Denied
- Verify user has sudo privileges for deployment
- Check directory ownership and permissions

### Health Check Failed
- Ensure PROD_URL is correctly formatted
- Verify SSL certificate is valid
- Check application is running after deployment