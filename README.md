# course-updates-notfier

# Certification Course Updates Notifier

🔔 Automated monitoring system for certification exam changes across AWS, Azure, Kubernetes, Google Cloud, and DevOps platforms.

## 🎯 Features

- 📡 Monitors official RSS feeds from certification providers
- 🌐 Scans announcement pages for updates
- 📧 Email notifications with beautifully formatted updates
- 💬 Slack notifications (optional)
- ⏰ Runs automatically every Monday at 9 AM UTC
- 🔍 Smart keyword matching and relevance scoring
- 🎨 Beautiful HTML email format

## 📚 Monitored Certifications

### AWS
- Solutions Architect (SAA)
- Developer Associate (DVA)
- SysOps Administrator (SOA)
- DevOps Engineer (DOP)
- All other AWS certifications

### Azure
- AZ-104, AZ-400, AZ-305
- AI, DP, SC, MS, PL series
- All Microsoft Learn certifications

### Kubernetes
- CKA (Certified Kubernetes Administrator)
- CKAD (Certified Kubernetes Application Developer)
- CKS (Certified Kubernetes Security Specialist)

### Google Cloud
- Professional and Associate level certifications

### DevOps
- HashiCorp (Terraform, Vault, Consul)

## 🚀 How It Works

1. **Every Monday at 9 AM UTC**, GitHub Actions automatically runs the monitor
2. Checks RSS feeds and announcement pages from official sources
3. Filters relevant updates using keyword matching
4. Sends formatted email with all certification updates
5. Logs are available in GitHub Actions for review

## 📊 Recent Scans

Check the [Actions tab](../../actions) to see recent scan results and logs.

## ⚙️ Configuration

- **Sources**: `config/sources.yaml` - RSS feeds and pages to monitor
- **Settings**: `config/settings.yaml` - Notification settings and filters

## 🔧 Manual Trigger

To run the scanner immediately (not wait for Monday):

1. Go to the [Actions tab](../../actions)
2. Click "Certification Monitor" on the left
3. Click "Run workflow" button
4. Click the green "Run workflow" button

## 📧 Notification Setup

Notifications are sent via email. To receive notifications:
1. Make sure your email is configured in `config/settings.yaml`
2. GitHub Secret `EMAIL_PASSWORD` must be set (see setup instructions)

## 🔔 Sample Notification

You'll receive emails like:
