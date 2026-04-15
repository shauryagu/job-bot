# Deployment Guide

## Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose (for containerized deployment)
- Google Cloud Project (for Google Sheets integration)
- Domain name (optional, for production)

## Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/job-bot.git
cd job-bot
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Application Settings
APP_NAME=JobBot
APP_VERSION=0.1.0
DEBUG=False
ENVIRONMENT=production

# Server Settings
HOST=0.0.0.0
PORT=8000

# Database Settings
DATABASE_URL=sqlite:///./data/database/job_bot.db

# Security Settings
SECRET_KEY=your-production-secret-key-here

# Google Sheets API
GOOGLE_SHEETS_CREDENTIALS_PATH=config/credentials.json
GOOGLE_SHEETS_SPREADSHEET_ID=your-spreadsheet-id

# ATS API Keys (optional)
GREENHOUSE_API_KEY=
LEVER_API_KEY=
ASHBY_API_KEY=

# LLM Settings (optional)
ANTHROPIC_API_KEY=
```

### 3. Google Sheets Setup

#### Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Sheets API

#### Create Service Account
1. Go to IAM & Admin > Service Accounts
2. Create a new service account
3. Grant the service account editor access to your spreadsheet
4. Download JSON credentials
5. Save as `config/credentials.json`

#### Create Spreadsheet
1. Create a new Google Sheet with the required tabs
2. Share the sheet with your service account email
3. Copy the spreadsheet ID to `.env`

## Deployment Options

### Option 1: Docker Compose (Recommended)

#### Build and Start Services

```bash
docker-compose up -d
```

#### View Logs

```bash
docker-compose logs -f job-bot
```

#### Stop Services

```bash
docker-compose down
```

#### Update and Restart

```bash
git pull
docker-compose down
docker-compose up -d --build
```

### Option 2: Direct Python Deployment

#### Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install
```

#### Initialize Database

```bash
python -m app.db.init_db
```

#### Start the Server

```bash
python main.py
```

#### Using Gunicorn (Production)

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Option 3: Cloud Deployment

#### Deploy to Render

1. Create a new web service on Render
2. Connect your GitHub repository
3. Add environment variables
4. Deploy

#### Deploy to Railway

1. Create a new project on Railway
2. Add a new service from GitHub
3. Configure environment variables
4. Deploy

#### Deploy to AWS

Using EC2:

```bash
# Launch EC2 instance
# SSH into instance
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Clone repository
git clone https://github.com/yourusername/job-bot.git
cd job-bot

# Configure environment
nano .env

# Start services
docker-compose up -d
```

Using ECS:

1. Create ECR repository
2. Build and push Docker image
3. Create ECS task definition
4. Create ECS service
5. Configure load balancer

## Database Management

### SQLite (Default)

Database file: `data/database/job_bot.db`

#### Backup

```bash
cp data/database/job_bot.db data/database/job_bot.db.backup
```

#### Restore

```bash
cp data/database/job_bot.db.backup data/database/job_bot.db
```

### PostgreSQL (Production)

Update `.env`:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/jobbot
```

#### Run Migrations

```bash
alembic upgrade head
```

#### Create Migration

```bash
alembic revision --autogenerate -m "description"
```

## SSL/TLS Configuration

### Using Let's Encrypt with Nginx

#### Install Certbot

```bash
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx
```

#### Obtain Certificate

```bash
sudo certbot --nginx -d yourdomain.com
```

#### Nginx Configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Monitoring & Logging

### View Logs

```bash
# Docker Compose
docker-compose logs -f job-bot

# Direct deployment
tail -f logs/job_bot.log
```

### Log Rotation

Create `/etc/logrotate.d/job-bot`:

```
/path/to/job-bot/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
}
```

### Health Checks

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy"
}
```

## Backup Strategy

### Automated Backups

Create backup script `scripts/backup.sh`:

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
mkdir -p $BACKUP_DIR

# Backup database
cp data/database/job_bot.db $BACKUP_DIR/job_bot_$DATE.db

# Backup configuration
tar -czf $BACKUP_DIR/config_$DATE.tar.gz config/

# Keep last 7 days
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

Add to crontab:

```bash
0 2 * * * /path/to/scripts/backup.sh
```

## Performance Tuning

### Database Optimization

```sql
-- Create indexes
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_source ON jobs(source);
CREATE INDEX idx_applications_stage ON applications(stage);
```

### Caching

Enable Redis caching in `.env`:

```env
REDIS_URL=redis://localhost:6379/0
ENABLE_CACHE=True
CACHE_TTL=3600
```

### Worker Processes

For Gunicorn:

```bash
gunicorn main:app -w $(nproc) -k uvicorn.workers.UvicornWorker
```

## Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Use strong database passwords
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Set up log monitoring
- [ ] Enable rate limiting
- [ ] Regular security updates
- [ ] Backup strategy in place
- [ ] Review API permissions
- [ ] Enable audit logging

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs job-bot

# Check port availability
netstat -tulpn | grep 8000

# Check environment variables
docker-compose config
```

### Database Connection Issues

```bash
# Check database file permissions
ls -la data/database/

# Test database connection
python -c "from app.db.session import engine; print(engine.connect())"
```

### Google Sheets Sync Issues

```bash
# Verify credentials
cat config/credentials.json

# Test API connection
python scripts/test_sheets.py
```

### Memory Issues

```bash
# Check memory usage
docker stats

# Increase memory limit in docker-compose.yml
services:
  job-bot:
    mem_limit: 2g
```

## Maintenance

### Regular Updates

```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Update Docker images
docker-compose pull
docker-compose up -d
```

### Database Maintenance

```bash
# Vacuum SQLite database
sqlite3 data/database/job_bot.db "VACUUM;"

# Analyze database
sqlite3 data/database/job_bot.db "ANALYZE;"
```

### Log Cleanup

```bash
# Compress old logs
find logs/ -name "*.log" -mtime +30 -exec gzip {} \;

# Remove compressed logs older than 90 days
find logs/ -name "*.gz" -mtime +90 -delete
```

## Support

For issues and questions:
- GitHub Issues: https://github.com/yourusername/job-bot/issues
- Documentation: https://github.com/yourusername/job-bot/docs