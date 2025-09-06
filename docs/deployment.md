

docs/deployment.md
# Deployment Guide

## Overview

This guide covers the deployment of EBUSINESS AI on Render.com. The application is designed to be deployed as a comprehensive automation system with web interface, background workers, and scheduled tasks.

## Prerequisites

Before deploying, ensure you have:

1. **Render Account**: A free account on [Render.com](https://render.com)
2. **GitHub Repository**: A repository containing the application code
3. **API Keys**: All required API keys (Mistral AI, SerpAPI, OpenAI)
4. **Email Account**: A Gmail account with app password enabled

## Deployment Steps

### 1. Repository Setup

#### Fork or Clone the Repository

```bash
git clone https://github.com/your-username/ebusiness-ai-prospection.git
cd ebusiness-ai-prospection
```

#### Configure Environment Variables

The application uses environment variables for configuration. These are already set in `render.yaml`:

```yaml
envVars:
  - key: MISTRAL_API_KEY
    value: 6qbOzQH2oncVctSsHjNfiygavJ0anIFl
  - key: EMAIL_ADDRESS
    value: ia.ebusinessag@gmail.com
  - key: EMAIL_PASSWORD
    value: Gepdg2104Succes
  # ... other variables
```

### 2. Render Deployment

#### Method 1: Automatic Deployment via GitHub

1. **Connect GitHub to Render**:
   - Log in to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub account
   - Select the `ebusiness-ai-prospection` repository

2. **Configure Service**:
   - **Name**: `ebusiness-ai-prospection`
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python src/main.py`
   - **Instance Type**: Free (or paid for better performance)

3. **Environment Variables**:
   - The environment variables are already configured in `render.yaml`
   - Render will automatically apply them during deployment

#### Method 2: Manual Deployment via Render Blueprint

1. **Ensure render.yaml is present**:
   The `render.yaml` file should be in the root of your repository:

```yaml
services:
  - type: web
    name: ebusiness-ai-prospection
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python src/main.py
    envVars:
      # ... environment variables
```

2. **Deploy via Blueprint**:
   - In Render Dashboard, click "Blueprints"
   - Connect your GitHub repository
   - Render will detect the `render.yaml` and configure the service automatically

### 3. Background Worker Deployment

The application requires a background worker for scheduled tasks:

1. **Create Worker Service**:
   - In Render Dashboard, click "New +" → "Background Worker"
   - Select the same repository
   - **Name**: `ebusiness-ai-worker`
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python src/scheduler/worker.py`

2. **Configure Environment Variables**:
   - Add the same environment variables as the web service

### 4. Database Setup

The application uses SQLite which is automatically created on first run:

```python
# Database is created automatically at startup
DATABASE_URL = sqlite:///data/prospects.db
```

The database file is stored in the `data/` directory which is persisted across deployments.

### 5. SSL and Custom Domain

#### Enable SSL

Render automatically provides SSL certificates for all services:

1. **Go to Service Settings**
2. **Add Custom Domain** (if applicable)
3. **Enable Automatic HTTPS**

#### Custom Domain

To use a custom domain:

1. **In your DNS provider**, create records:
   ```
   Type: CNAME
   Name: www
   Value: your-service-name.onrender.com
   ```

2. **In Render Dashboard**:
   - Go to service settings
   - Add custom domain
   - Render will automatically provision SSL certificate

## Post-Deployment Configuration

### 1. Initial Setup

After deployment, the system will automatically:

1. **Create Database Tables**: All required tables are created on first run
2. **Start Scheduler**: Background tasks begin running immediately
3. **Initialize Logging**: Log files are created in `data/logs`

### 2. Verify Deployment

#### Check Web Service

```bash
curl https://your-service-name.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-06-17T10:30:00.000Z",
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "scheduler": "running",
    "email_service": "ready"
  }
}
```

#### Check Background Worker

1. **Go to Render Dashboard**
2. **Select the worker service**
3. **Check logs** for any errors

#### Access Dashboard

The Streamlit dashboard is available at:
```
https://your-service-name.onrender.com:8501
```

### 3. Monitor Performance

#### Render Dashboard

Monitor your services through the Render Dashboard:

- **Metrics**: CPU, memory, and response times
- **Logs**: Real-time logs from all services
- **Events**: Deployment events and service status

#### Application Logs

Access application logs:

1. **In Render Dashboard**, select your service
2. **Click "Logs" tab**
3. **View real-time logs**

#### Database Monitoring

The application includes built-in health checks:

```bash
curl https://your-service-name.onrender.com/api/stats
```

### 4. Backup Strategy

#### Automatic Backups

The system includes automatic backup functionality:

1. **Database Backups**: SQLite database is backed up regularly
2. **Log Rotation**: Logs are automatically rotated
3. **Export Functionality**: Data can be exported via the dashboard

#### Manual Backup

Trigger manual backup via API:

```bash
curl -X POST https://your-service-name.onrender.com/api/system/backup \
  -H "Authorization: Bearer your-api-key"
```

## Troubleshooting

### Common Issues

#### 1. Service Not Starting

**Symptoms**: Service shows "Crashed" status

**Solutions**:
1. **Check logs** in Render Dashboard
2. **Verify Python version** (should be 3.13.4)
3. **Check dependencies** in `requirements.txt`

#### 2. Database Connection Issues

**Symptoms**: "Database connection failed" in logs

**Solutions**:
1. **Ensure data directory exists**: `data/` directory should be present
2. **Check file permissions**: SQLite needs write permissions
3. **Verify DATABASE_URL**: Should be `sqlite:///data/prospects.db`

#### 3. Email Sending Issues

**Symptoms**: Emails not being sent

**Solutions**:
1. **Verify email credentials**: Check EMAIL_ADDRESS and EMAIL_PASSWORD
2. **Enable less secure apps**: For Gmail, enable "Less secure apps" or use app password
3. **Check sending limits**: Verify not exceeding daily limits

#### 4. Scheduler Not Running

**Symptoms**: Background tasks not executing

**Solutions**:
1. **Check worker service**: Ensure worker is running
2. **Verify scheduler logs**: Check for errors in worker logs
3. **Check timezone settings**: Verify TIMEZONE environment variable

#### 5. Memory Issues

**Symptoms**: Service crashes due to memory limits

**Solutions**:
1. **Upgrade instance type**: Free tier has limited memory
2. **Optimize memory usage**: Check for memory leaks
3. **Monitor memory usage**: Use Render metrics

### Debug Mode

Enable debug mode for detailed logging:

```yaml
envVars:
  - key: DEBUG_MODE
    value: 'true'
  - key: LOG_LEVEL
    value: 'DEBUG'
```

### Performance Optimization

#### Instance Types

| Instance Type | Memory | CPU | Cost | Use Case |
|---------------|--------|-----|------|----------|
| Free | 512MB | 1x | Free | Development/testing |
| Starter | 1GB | 1x | $7/month | Light production |
| Standard | 2GB | 2x | $25/month | Medium production |
| Standard Plus | 4GB | 4x | $50/month | Heavy production |

#### Database Optimization

For better performance with larger datasets:

1. **Enable WAL mode** for SQLite:
```python
# In src/core/database.py
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)
```

2. **Regular maintenance**:
   - VACUUM database regularly
   - Optimize indexes

#### Caching Strategy

Implement caching for frequently accessed data:

```python
# In src/core/utils.py
from functools import lru_cache

@lru_cache(maxsize=100)
def get_system_stats_cached():
    return get_system_stats()
```

## Security Considerations

### Environment Variables

- **Never commit API keys** to version control
- **Use Render's secret management** for sensitive data
- **Rotate keys regularly** for security

### API Security

- **Use HTTPS** for all communications
- **Implement rate limiting** for API endpoints
- **Validate input data** to prevent injection attacks

### Email Security

- **Use SPF/DKIM** records for email authentication
- **Monitor email reputation** regularly
- **Implement unsubscribe functionality**

## Scaling Considerations

### Vertical Scaling

Upgrade instance types as needed:

1. **Monitor metrics** in Render Dashboard
2. **Upgrade instance** when approaching limits
3. **Test performance** after scaling

### Horizontal Scaling

For high-traffic scenarios:

1. **Load balancer**: Use Render's load balancing
2. **Multiple instances**: Run multiple web service instances
3. **Database scaling**: Consider PostgreSQL for larger datasets

### Background Processing

For heavy background tasks:

1. **Separate worker services** for different task types
2. **Queue systems** for task management
3. **Monitoring** for worker performance

## Maintenance

### Updates

1. **Code Updates**: Push to GitHub, Render auto-deploys
2. **Dependency Updates**: Update `requirements.txt` regularly
3. **Security Updates**: Monitor for security vulnerabilities

### Monitoring

Set up monitoring:

1. **Render Metrics**: Built-in monitoring
2. **Health Checks**: Regular health check endpoints
3. **Alerting**: Set up email alerts for critical issues

### Backup Strategy

1. **Regular Backups**: Automated database backups
2. **Off-site Storage**: Store backups in multiple locations
3. **Recovery Testing**: Regularly test backup recovery

## Support

### Documentation

- **API Documentation**: `/docs/api.md`
- **User Guide**: `/docs/user_guide.md`
- **Architecture**: `/docs/architecture.md`

### Getting Help

- **Render Support**: [Render Docs](https://render.com/docs)
- **GitHub Issues**: Report bugs and request features
- **Email Support**: ia.ebusinessag@gmail.com

### Community

- **Discussions**: GitHub Discussions
- **Issues**: Bug reports and feature requests
- **Contributions**: Pull requests welcome

## Conclusion

EBUSINESS AI is designed to be easily deployable on Render with minimal configuration. The system includes comprehensive monitoring, logging, and backup capabilities to ensure reliable operation in production.

For additional support or questions, refer to the documentation or contact the development team.
