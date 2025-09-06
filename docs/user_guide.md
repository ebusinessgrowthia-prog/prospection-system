

docs/user_guide.md
# User Guide

## Getting Started

Welcome to EBUSINESS AI! This guide will help you understand how to use the automated prospecting system to find, qualify, and contact e-commerce businesses in French-speaking Europe.

## Overview

EBUSINESS AI is an intelligent automation system that:
- 🔍 **Finds prospects** using Google Dorks and web scraping
- 🎯 **Qualifies leads** based on your target criteria
- ✏️ **Generates personalized emails** using AI
- 📧 **Sends emails** according to your schedule
- 📊 **Tracks performance** with real-time analytics

## First Steps

### 1. Access the Dashboard

After deployment, access the main dashboard at:
```
https://your-app-name.onrender.com:8501
```

The dashboard provides:
- **Real-time metrics** on prospecting activities
- **Prospect management** with filtering and search
- **Campaign performance** tracking
- **System health** monitoring

### 2. Initial Configuration

The system comes pre-configured with:
- **Target sectors**: Mode, Électronique, Services, Digital, Retail
- **Target countries**: France, Belgique, Suisse, Luxembourg, Monaco, and more
- **Email settings**: Pre-configured with your Gmail account
- **Scheduling**: Tuesday to Friday, 9 AM to 5 PM (France time)

### 3. Verify System Status

Check the system status in the dashboard:
- **System Health**: Should show "Actif" (green)
- **Services**: All services should be running
- **Last Update**: Should show recent activity

## Using the Dashboard

### Main Dashboard View

The main dashboard displays key metrics:

| Metric | Description | What to Look For |
|--------|-------------|------------------|
| Prospects Qualifiés | Total qualified prospects | Steady increase over time |
| Emails Envoyés | Total emails sent | Should match your daily limits |
| Taux d'Ouverture | Email open rate | Industry average is 20-30% |
| Audits Réservés | Completed audits | Your conversion metric |

### Navigation Menu

Use the sidebar to navigate:
- **Accueil**: Main dashboard with overview metrics
- **Prospects**: Prospect management and search
- **Campaigns**: Email campaign performance
- **Analytics**: Detailed analytics and reports

## Managing Prospects

### Finding Prospects

The system automatically searches for prospects every 2 hours. You can also trigger manual searches:

1. Go to **Prospects** page
2. Click **"Recherche Manuelle"**
3. Select specific Google Dorks or use defaults
4. Click **"Lancer la Recherche"**

### Qualifying Prospects

Prospects are automatically qualified based on:
- **Sector match**: Must be in your target sectors
- **Country match**: Must be in your target countries
- **Email quality**: Professional email addresses
- **Website presence**: Valid e-commerce website

#### Qualification Criteria

| Criteria | Weight | Description |
|----------|--------|-------------|
| Target Sector | 2.0 | Business operates in your target sectors |
| Target Country | 2.0 | Business located in your target countries |
| Professional Email | 1.5 | Uses business email (not Gmail/Yahoo) |
| Website Present | 1.5 | Has valid e-commerce website |
| E-commerce Detected | 2.0 | Confirmed e-commerce activity |
| Appropriate Size | 1.0 | Business size matches your criteria |

### Viewing Prospect Details

Click on any prospect to see detailed information:
- **Contact Information**: Name, company, email, phone
- **Business Details**: Sector, country, website
- **Qualification**: Score and reasons
- **Activity History**: Email interactions and responses

### Filtering and Searching

Use the filtering options to find specific prospects:

#### By Status
- **Nouveau**: Recently found, not yet qualified
- **Qualifié**: Meets your criteria
- **Contacté**: Email sent
- **Répondu**: Opened or clicked email
- **Audit Réservé**: Booked an audit

#### By Sector
Select specific sectors: Mode, Électronique, Services, Digital, Retail

#### By Country
Filter by country: France, Belgique, Suisse, etc.

#### Search Function
Use the search bar to find prospects by:
- Company name
- Person name
- Email address
- Website URL

## Email Campaigns

### Understanding Email Automation

The system handles email campaigns automatically:

1. **Generation**: Creates personalized emails using AI
2. **Scheduling**: Sends emails Tuesday-Friday, 9 AM-5 PM
3. **Tracking**: Monitors opens and clicks
4. **Follow-up**: Manages responses and bookings

### Email Personalization

Each email is personalized using:
- **Prospect name**: Personal greeting
- **Company name**: Business-specific content
- **Sector expertise**: Industry-specific messaging
- **Detected problems**: Address specific pain points
- **Personalized CTA**: Custom call-to-action

### Email Templates

The system uses professionally designed templates:

#### French Template
```
Bonjour [Name],

J'ai remarqué que votre entreprise [Company] semble prometteuse. 
Avez-vous déjà mesuré comment vos données pourraient optimiser votre performance ?

Un e-commerçant similaire a récemment découvert grâce à notre audit qu'il 
pouvait réduire ses coûts d'acquisition de 25% en exploitant mieux ses données.

J'ai conçu un framework d'audit gratuit qui pourrait vous révéler des opportunités 
cachées dans vos données. Souhaitez-vous y jeter un œil ?

🚀 Découvre comment exploiter tes données e-commerce

Merci,
EBUSINESS AI
ia.ebusinessag@gmail.com
```

### Tracking Performance

Monitor email performance through the **Campaigns** page:

| Metric | Description | Good Performance |
|--------|-------------|------------------|
| Sent | Total emails sent | Consistent with your goals |
| Opened | Emails opened | 20-30% is good |
| Clicked | Links clicked | 2-5% of opened emails |
| Booked | Audits booked | 1-3% of sent emails |

### Manual Email Actions

You can manually:
- **Generate Email**: Create personalized email for a prospect
- **Send Email**: Send email immediately
- **View Content**: See generated email content
- **Track Performance**: Monitor opens and clicks

## Scheduling and Automation

### Understanding the Schedule

The system operates on a strict schedule:

#### Search Schedule
- **Frequency**: Every 2 hours
- **Action**: Find new prospects using Google Dorks
- **Result**: New prospects added to database

#### Qualification Schedule
- **Frequency**: Every 1 hour
- **Action**: Qualify newly found prospects
- **Result**: Prospects marked as "qualifié"

#### Email Generation
- **Frequency**: Every 30 minutes (business hours only)
- **Action**: Generate personalized emails
- **Result**: Emails ready for sending

#### Email Sending
- **Frequency**: Every 15 minutes (business hours only)
- **Action**: Send generated emails
- **Result**: Emails delivered to prospects

### Business Hours Configuration

The system respects business hours:
- **Days**: Tuesday, Wednesday, Thursday, Friday
- **Hours**: 9:00 AM to 5:00 PM (France time)
- **Timezone**: Europe/Paris

### Customizing Schedules

You can modify schedules through the **Configuration** page:
- **Search Frequency**: How often to search for prospects
- **Email Limits**: Maximum emails per day
- **Business Hours**: Custom days and times
- **Target Criteria**: Sectors and countries

## Analytics and Reporting

### Understanding Analytics

The **Analytics** page provides comprehensive insights:

#### Prospect Analytics
- **Total Prospects**: Overall number of prospects
- **Qualified Rate**: Percentage that meet criteria
- **Source Breakdown**: Where prospects come from
- **Geographic Distribution**: Countries and regions

#### Email Analytics
- **Delivery Rate**: Emails successfully delivered
- **Open Rate**: Emails opened by recipients
- **Click Rate**: Links clicked in emails
- **Conversion Rate**: Audits booked

#### Performance Trends
- **Daily Metrics**: Day-by-day performance
- **Weekly Trends**: Week-over-week changes
- **Monthly Reports**: Monthly summaries

### Exporting Data

Export data for external analysis:

#### Prospect Export
1. Go to **Prospects** page
2. Click **"Exporter les prospects"**
3. Choose format (CSV, Excel, JSON)
4. Select date range and filters
5. Click **"Exporter"**

#### Campaign Export
1. Go to **Campaigns** page
2. Click **"Exporter les données"**
3. Choose format and date range
4. Click **"Exporter"**

### Understanding Reports

Key reports and what they mean:

#### Prospect Quality Report
- **High Score (8-10)**: Excellent matches, prioritize contact
- **Medium Score (5-7)**: Good matches, consider contact
- **Low Score (0-4)**: Poor matches, review criteria

#### Email Performance Report
- **High Open Rate (>30%)**: Compelling subject lines
- **Low Open Rate (<15%)**: Need subject line improvement
- **High Click Rate (>5%)**: Engaging content
- **Low Click Rate (<2%)**: Need content improvement

## System Configuration

### Accessing Configuration

Go to **Configuration** in the sidebar to modify:
- **Target Settings**: Sectors and countries
- **Email Settings**: Sending limits and schedules
- **AI Settings**: Personalization parameters
- **System Settings**: Logging and monitoring

### Target Configuration

#### Sectors
Configure your target business sectors:
- **Mode**: Fashion and clothing
- **Électronique**: Electronics and tech
- **Services**: Professional services
- **Digital**: Digital products
- **Retail**: General retail

#### Countries
Select target countries:
- **France**: Primary market
- **Belgique**: French-speaking Belgium
- **Suisse**: French-speaking Switzerland
- **Luxembourg**: Luxembourg market
- **Monaco**: Monaco market
- **Canada (Québec)**: Quebec market
- **Francophone Africa**: African markets

### Email Configuration

#### Sending Limits
- **Max Emails Per Day**: Maximum emails to send daily
- **Delay Between Emails**: Seconds between each email
- **Business Hours**: Days and times for sending

#### Email Templates
Customize email templates:
- **Subject Lines**: Test different subject lines
- **Content**: Modify email body content
- **CTA**: Customize call-to-action buttons
- **Signature**: Update email signature

### AI Configuration

#### Personalization Settings
- **Tone**: Professional, friendly, formal
- **Length**: Email length preferences
- **Personalization Level**: How much to customize
- **Language**: French or English

#### AI Model Settings
- **Model Selection**: Choose AI model
- **Temperature**: Creativity level (0.1-1.0)
- **Max Tokens**: Maximum response length

## Troubleshooting

### Common Issues

#### System Not Working

**Symptoms**: Dashboard shows errors, prospects not found

**Solutions**:
1. **Check System Status**: Verify all services are running
2. **Review Logs**: Check for error messages
3. **API Keys**: Verify all API keys are valid
4. **Internet Connection**: Ensure stable internet

#### Emails Not Sending

**Symptoms**: Emails not being sent, high failure rates

**Solutions**:
1. **Email Configuration**: Verify email settings
2. **Gmail Settings**: Enable less secure apps or app passwords
3. **Sending Limits**: Check daily limits not exceeded
4. **Spam Filters**: Verify emails not marked as spam

#### Poor Email Performance

**Symptoms**: Low open rates, few clicks

**Solutions**:
1. **Subject Lines**: Test different subject lines
2. **Content Quality**: Improve email content
3. **Targeting**: Review prospect targeting
4. **Timing**: Adjust sending schedule

#### Database Issues

**Symptoms**: Data loss, slow performance

**Solutions**:
1. **Backup**: Restore from backup
2. **Optimization**: Run database optimization
3. **Storage**: Check available storage space
4. **Integrity**: Verify database integrity

### Getting Help

#### Dashboard Help
- **Tooltips**: Hover over elements for help
- **Documentation**: Access built-in documentation
- **Tours**: Take guided tours of features

#### Support Resources
- **Email Support**: ia.ebusinessag@gmail.com
- **Documentation**: Complete API docs
- **Community**: User forums and discussions
- **Issues**: Report bugs and request features

### Best Practices

#### Daily Usage
1. **Check Dashboard**: Review metrics every morning
2. **Monitor Performance**: Track email performance
3. **Adjust Settings**: Optimize based on results
4. **Export Data**: Regular data exports

#### Weekly Usage
1. **Weekly Reports**: Review weekly performance
2. **Prospect Review**: Qualify new prospects
3. **Campaign Analysis**: Analyze campaign results
4. **System Maintenance**: Check system health

#### Monthly Usage
1. **Monthly Reports**: Comprehensive monthly analysis
2. **Strategy Review**: Adjust targeting strategy
3. **System Updates**: Apply updates and patches
4. **Backup**: Create system backups

## Advanced Features

### A/B Testing

Test different email approaches:

1. **Create Variants**: Different subject lines or content
2. **Split Audience**: Divide prospects into groups
3. **Send Campaigns**: Send different variants
4. **Analyze Results**: Compare performance

### Custom Workflows

Create custom automation workflows:

1. **Define Triggers**: Events that start workflows
2. **Set Actions**: What happens when triggered
3. **Configure Logic**: Rules and conditions
4. **Test Workflows**: Verify they work correctly

### Integration Options

Integrate with other systems:

1. **API Access**: Use REST API for integration
2. **Webhooks**: Real-time notifications
3. **Zapier**: Connect with 5000+ apps
4. **Custom Scripts**: Create custom integrations

## Security

### Account Security

- **Strong Passwords**: Use complex, unique passwords
- **Two-Factor Authentication**: Enable 2FA when available
- **Regular Updates**: Keep software updated
- **Access Control**: Limit access to authorized users

### Data Security

- **Encryption**: All data encrypted in transit
- **Backups**: Regular, secure backups
- **Access Logs**: Monitor data access
- **Compliance**: GDPR and privacy compliance

### Email Security

- **Authentication**: Secure email authentication
- **SPF/DKIM**: Email authentication standards
- **Unsubscribe**: Easy unsubscribe options
- **Compliance**: CAN-SPAM compliance

## Conclusion

EBUSINESS AI is designed to be intuitive and powerful. With proper configuration and regular monitoring, it will help you find and connect with qualified e-commerce prospects efficiently.

### Key Success Factors
1. **Configuration**: Proper initial setup
2. **Monitoring**: Regular performance review
3. **Optimization**: Continuous improvement
4. **Patience**: Allow time for results

### Next Steps
1. **Complete Setup**: Finish initial configuration
2. **Monitor Performance**: Track key metrics
3. **Optimize**: Adjust based on results
4. **Scale**: Expand successful strategies

For additional support or questions, don't hesitate to reach out to our support team or consult the comprehensive documentation.

Happy prospecting! 🚀
