# AWS EB Migration - Quick Reference Commands

## Setup & Initialization

```bash
# 1. Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-macos.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

# 2. Install EB CLI
brew install aws-elasticbeanstalk/tap/aws-elasticbeanstalk

# 3. Configure AWS credentials
aws configure
# Enter: AWS Access Key ID, Secret Key, Region (us-east-1), Output format (json)

# 4. Verify installation
aws --version
eb --version
aws sts get-caller-identity
```

---

## Database Migration

```bash
# Export from Render
pg_dump -h [render-host] -U [render-user] -d [render-db] > render_backup.sql

# Create database in RDS
psql -h [rds-endpoint] -U postgres -c "CREATE DATABASE recruithub;"

# Import data to RDS
psql -h [rds-endpoint] -U postgres -d recruithub < render_backup.sql

# Verify (connect to RDS)
psql -h [rds-endpoint] -U postgres -d recruithub
# Then: SELECT COUNT(*) FROM core_userprofile;
# Exit: \q
```

---

## Elastic Beanstalk Initialization

```bash
# Navigate to project directory
cd /Users/tapdiyaom/Desktop/RecruitHub

# Initialize EB application
eb init -p python-3.11 recruithub --region us-east-1

# Create environment (takes 5-10 minutes)
eb create recruithub-prod --instance-type t3.micro

# Check status
eb status

# View environment URL
eb open
```

---

## Environment Variables

```bash
# Method 1: Interactive script
chmod +x set_eb_env_vars.sh
./set_eb_env_vars.sh

# Method 2: From file
chmod +x set_eb_vars.sh
cp .env.prod.example .env.prod
# Edit .env.prod with actual values
eb setenv < .env.prod

# Method 3: Command line
eb setenv \
  DEBUG=False \
  SECRET_KEY='your-secret-key' \
  RDS_HOSTNAME='recruithub-db.xxxxx.us-east-1.rds.amazonaws.com' \
  RDS_USERNAME='postgres' \
  RDS_PASSWORD='your-password' \
  RDS_DB_NAME='recruithub' \
  RDS_PORT='5432'

# Verify variables
eb printenv
```

---

## Deployment

```bash
# Method 1: Using deployment script
chmod +x aws_eb_deploy.sh
./aws_eb_deploy.sh

# Method 2: Manual deployment
python manage.py collectstatic --noinput
pip freeze > requirements.txt
eb deploy

# Watch deployment
eb logs -z    # Real-time logs
eb health     # Health status
eb status     # Overall status
```

---

## Route 53 & DNS

```bash
# List hosted zones
aws route53 list-hosted-zones

# Get nameservers for hosted zone
aws route53 list-resource-record-sets \
    --hosted-zone-id Z__________ | grep NS

# Create A record (root domain)
aws route53 change-resource-record-sets \
    --hosted-zone-id Z__________ \
    --change-batch file://dns-records.json

# Test DNS resolution
nslookup vakverse.com
dig vakverse.com
dig A vakverse.com
dig CNAME www.vakverse.com
```

---

## SSL/TLS Certificate

```bash
# Request certificate
aws acm request-certificate \
    --domain-name vakverse.com \
    --subject-alternative-names www.vakverse.com '*.vakverse.com' \
    --validation-method DNS \
    --region us-east-1

# List certificates
aws acm list-certificates --region us-east-1

# Get certificate details
aws acm describe-certificate \
    --certificate-arn arn:aws:acm:region:account:certificate/id \
    --region us-east-1

# Test SSL certificate
openssl s_client -connect vakverse.com:443
```

---

## Elastic Beanstalk Management

```bash
# Deploy code
eb deploy

# SSH into EC2 instance
eb ssh

# View logs
eb logs              # Latest logs
eb logs -z           # Stream (real-time)
eb logs --all        # Complete logs
eb logs --stream     # Stream complete logs

# Check health
eb health
eb health --refresh  # Continuous update (Ctrl+C to exit)

# Scale instances
eb scale 2           # Set to 2 instances
eb scale 3           # Set to 3 instances

# Terminate environment (DANGER!)
eb terminate recruithub-prod

# Enable/disable monitoring
eb monitoring enable
eb monitoring disable

# Open application
eb open

# Environment configuration
eb config            # Edit configuration
eb config get        # View current config
```

---

## RDS Management

```bash
# List RDS instances
aws rds describe-db-instances

# Create snapshot
aws rds create-db-snapshot \
    --db-instance-identifier recruithub-db \
    --db-snapshot-identifier recruithub-backup-$(date +%Y%m%d)

# List snapshots
aws rds describe-db-snapshots

# Connect to RDS (from EB instance)
eb ssh
psql -h [rds-endpoint] -U postgres -d recruithub

# Monitor RDS
aws rds describe-db-instances \
    --db-instance-identifier recruithub-db \
    --query 'DBInstances[0].{Name:DBInstanceIdentifier,Status:DBInstanceStatus,Engine:Engine,Size:DBInstanceClass}'
```

---

## CloudWatch Monitoring

```bash
# List log groups
aws logs describe-log-groups

# Get recent logs
aws logs tail /aws/elasticbeanstalk/recruithub-prod/var/log/eb-activity.log --follow

# Create alarm (high CPU)
aws cloudwatch put-metric-alarm \
    --alarm-name recruithub-high-cpu \
    --alarm-description "Alert on high CPU" \
    --metric-name CPUUtilization \
    --namespace AWS/EC2 \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2

# List alarms
aws cloudwatch describe-alarms
```

---

## Troubleshooting

```bash
# Check EB status and health
eb status
eb health

# View environment logs
eb logs --all

# SSH into instance and check
eb ssh
tail -f /var/log/eb-activity.log
cd /var/app/current
python manage.py check
python manage.py showmigrations

# Django troubleshooting
source /var/app/venv/*/bin/activate
python manage.py shell
# Then in shell:
# >>> from django.conf import settings
# >>> settings.DATABASES
# >>> from django.db import connection
# >>> connection.ensure_connection()

# Check security groups
aws ec2 describe-security-groups --filters "Name=group-name,Values=*recruithub*"

# Check RDS connectivity
psql -h [rds-endpoint] -U postgres -d recruithub -c "SELECT 1;"
```

---

## Cost Checking

```bash
# Get estimated costs
aws ce get-cost-and-usage \
    --time-period Start=2024-01-01,End=2024-01-31 \
    --granularity MONTHLY \
    --metrics "UnblendedCost" \
    --group-by Type=DIMENSION,Key=SERVICE

# List running instances
aws ec2 describe-instances --query 'Reservations[0].Instances[0].{Name:Tags[0].Value,Type:InstanceType,State:State.Name}'

# RDS costs
aws rds describe-db-instances --query 'DBInstances[0].{Identifier:DBInstanceIdentifier,Class:DBInstanceClass,Storage:AllocatedStorage,MultiAZ:MultiAZEnabled}'
```

---

## Cleanup & Rollback

```bash
# Scale down (stops charges)
eb scale 0

# Terminate environment
eb terminate recruithub-prod

# Keep RDS database
# AWS Console → RDS → Instances → recruithub-db → Actions → Delete
# ⚠️ UNCHECK "Create final snapshot" to delete immediately
# ⚠️ CHECK "Create final snapshot" to keep backup

# Delete Route 53 hosted zone
aws route53 delete-hosted-zone --id Z__________

# Full cleanup
eb terminate --all  # Terminates all environments
```

---

## Useful AWS CLI Queries

```bash
# Get ALB DNS name (for Route 53)
aws elbv2 describe-load-balancers \
    --query 'LoadBalancers[*].[LoadBalancerName,DNSName]' \
    --output table

# Get EC2 security group
aws ec2 describe-security-groups \
    --filters "Name=tag:aws:elasticbeanstalk:environment-name,Values=recruithub-prod" \
    --query 'SecurityGroups[0].GroupId'

# Get RDS endpoint
aws rds describe-db-instances \
    --db-instance-identifier recruithub-db \
    --query 'DBInstances[0].Endpoint.Address'

# List all EB environments
aws elasticbeanstalk describe-environments \
    --query 'Environments[*].[EnvironmentName,Status,Health]' \
    --output table
```

---

## Git Integration

```bash
# Create git branch for AWS migration
git checkout -b aws-elastic-beanstalk

# Stage EB configuration
git add .ebextensions/
git add .env.prod.example
git add aws_eb_deploy.sh set_eb_env_vars.sh
git add AWS_EB_MIGRATION_GUIDE.md ROUTE53_DNS_SETUP.md

# Commit (DO NOT commit .env.prod with real values!)
git commit -m "Add AWS Elastic Beanstalk configuration"

# Push branch
git push origin aws-elastic-beanstalk

# After testing, merge to main
git checkout main
git merge aws-elastic-beanstalk
git push origin main
```

---

## One-Liner Commands

```bash
# Quick status check
echo "EB Status:" && eb status && echo "" && echo "Environment Health:" && eb health

# Deploy and monitor
eb deploy && eb logs -z

# Get all important info
echo "ALB DNS:" && aws elbv2 describe-load-balancers --query 'LoadBalancers[0].DNSName' --output text && echo "" && echo "RDS Host:" && aws rds describe-db-instances --db-instance-identifier recruithub-db --query 'DBInstances[0].Endpoint.Address' --output text

# Get Route 53 records
aws route53 list-resource-record-sets --hosted-zone-id Z__________ --output table

# SSH and run migrations
eb ssh -c "source /var/app/venv/*/bin/activate && cd /var/app/current && python manage.py migrate"
```

---

## Emergency Procedures

```bash
# Quick rollback (point DNS back to Render temporarily)
# 1. Update Route 53 to old IP
# 2. Kill EB instance: eb scale 0
# 3. Restart RDS and verify data

# Restart EB instance
eb restart

# Rebuild environment
eb rebuild

# Full environment replacement (new EC2 instance)
eb terminate -all  # Then eb create
```

---

## Monitoring Dashboard

```bash
# Set up cloudwatch dashboard
aws cloudwatch put-dashboard \
    --dashboard-name recruithub-prod \
    --dashboard-body file://dashboard.json

# View dashboard metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/ElasticBeanstalk \
    --metric-name InstanceHealth \
    --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 60 \
    --statistics Average
```

---

## Pre-Launch Checklist

```bash
# Run this before going live
echo "✓ Checking prerequisites..."

# 1. Code ready
git status | grep "nothing to commit" && echo "✓ All code committed"

# 2. AWS credentials working
aws sts get-caller-identity | grep Account && echo "✓ AWS credentials OK"

# 3. EB initialized
[ -d ".elasticbeanstalk" ] && echo "✓ EB initialized"

# 4. Configuration files present
[ -d ".ebextensions" ] && echo "✓ EB extensions present"
[ -f "requirements.txt" ] && echo "✓ requirements.txt present"

# 5. Django check
python manage.py check && echo "✓ Django check passed"

# 6. Database migrated
echo "✓ Check RDS: aws rds describe-db-instances --db-instance-identifier recruithub-db"

echo ""
echo "Ready to deploy!"
```

---

## Helpful Resources

- AWS EB Docs: https://docs.aws.amazon.com/elasticbeanstalk/
- Route 53 Docs: https://docs.aws.amazon.com/route53/
- Django Deployment: https://docs.djangoproject.com/en/stable/howto/deployment/
- EB CLI Reference: https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3.html
- AWS CLI Reference: https://docs.aws.amazon.com/cli/latest/
- CloudWatch Docs: https://docs.aws.amazon.com/cloudwatch/
