# Alertmanager Configuration

## Environment Variables

The alertmanager.yml file uses environment variable substitution. You need to set the following environment variables:

- `SMTP_HOST`: SMTP server hostname (e.g., smtp.gmail.com)
- `SMTP_PORT`: SMTP server port (e.g., 587)
- `SMTP_FROM`: Email address to send alerts from
- `SMTP_USERNAME`: SMTP authentication username
- `SMTP_PASSWORD`: SMTP authentication password

## Usage with Docker

When running Alertmanager with Docker, pass these environment variables:

```bash
docker run -d \
  -e SMTP_HOST=smtp.gmail.com \
  -e SMTP_PORT=587 \
  -e SMTP_FROM=alerts@yourdomain.com \
  -e SMTP_USERNAME=your-email@gmail.com \
  -e SMTP_PASSWORD=your-app-password \
  -v $(pwd)/alertmanager.yml:/etc/alertmanager/alertmanager.yml \
  prom/alertmanager
```

## Note

The YAML file uses `${VARIABLE}` syntax for environment substitution. Make sure your deployment method supports this (e.g., using envsubst or a configuration management tool).