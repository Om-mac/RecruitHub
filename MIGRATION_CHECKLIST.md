# AWS Elastic Beanstalk Migration Checklist

## Pre-Migration (This Week)

### AWS Account Setup
- [ ] AWS Account created and verified
- [ ] Billing enabled and payment method added
- [ ] IAM user created with programmatic access
- [ ] AWS Access Key ID saved securely
- [ ] AWS Secret Access Key saved securely
- [ ] EC2 key pair created and downloaded (.pem file)

### Local Environment Setup
- [ ] AWS CLI v2 installed: `aws --version`
- [ ] EB CLI installed: `eb --version`
- [ ] AWS credentials configured: `aws configure`
- [ ] Git repository up to date
- [ ] All code changes committed

### Documentation Review
- [ ] Read: AWS_EB_MIGRATION_GUIDE.md
- [ ] Read: ROUTE53_DNS_SETUP.md
- [ ] Understand the architecture and flow
- [ ] Identified potential issues/concerns

---

## Phase 1: AWS Infrastructure Setup (Day 1)

### RDS Database Creation
- [ ] Navigate to RDS Dashboard
- [ ] Create PostgreSQL database:
  - [ ] Instance identifier: `recruithub-db`
  - [ ] Master username: `postgres`
  - [ ] Master password: [STRONG-PASSWORD] (saved)
  - [ ] Instance class: `db.t3.micro`
  - [ ] Storage: 20 GB
  - [ ] Public accessibility: No
  - [ ] Backup enabled: Yes
  - [ ] Multi-AZ: No
- [ ] Database created successfully
- [ ] RDS endpoint noted: `recruithub-db.xxxxx.us-east-1.rds.amazonaws.com`
- [ ] Security group configured for EB access

### RDS Security Configuration
- [ ] RDS security group created/configured
- [ ] Inbound rule: PostgreSQL (5432) from EB security group
- [ ] OR Inbound rule: PostgreSQL (5432) from 0.0.0.0/0 (temporary)
- [ ] Outbound rules allow database connections

### Database Migration
- [ ] Connected to Render PostgreSQL
- [ ] Exported database: `pg_dump` command successful
- [ ] Backup file created: `render_backup.sql` (size: ____)
- [ ] Created database in RDS: `psql` connected successfully
- [ ] Imported data from render_backup.sql
- [ ] Verified table count in RDS matches Render
- [ ] Spot-checked key tables (users, profiles, etc.)

---

## Phase 2: Django Application Preparation (Day 1-2)

### EB Configuration Files
- [ ] `.ebextensions/` directory created
- [ ] `01_django.config` - Django settings ✅
- [ ] `02_alb.config` - ALB configuration ✅
- [ ] `03_autoscaling.config` - Auto scaling ✅
- [ ] `04_security.config` - Security headers ✅
- [ ] `05_https_redirect.config` - HTTPS redirect ✅

### Python Dependencies
- [ ] `requirements.txt` generated: `pip freeze > requirements.txt`
- [ ] `psycopg2-binary` included (PostgreSQL)
- [ ] `gunicorn` included (EB WSGI server)
- [ ] `python-decouple` or `django-environ` included
- [ ] All other dependencies listed

### Django Settings Updates
- [ ] Updated `auth_project/settings.py`:
  - [ ] `ALLOWED_HOSTS` includes:
    - `vakverse.com`
    - `www.vakverse.com`
    - `*.elasticbeanstalk.com`
  - [ ] Database configuration uses RDS env vars:
    - `RDS_DB_NAME`
    - `RDS_USERNAME`
    - `RDS_PASSWORD`
    - `RDS_HOSTNAME`
    - `RDS_PORT`
  - [ ] `STATIC_ROOT` configured: `/var/app/current/staticfiles`
  - [ ] `MEDIA_ROOT` configured (if needed)
  - [ ] Security settings for production:
    - [ ] `SECURE_SSL_REDIRECT = True`
    - [ ] `SESSION_COOKIE_SECURE = True`
    - [ ] `CSRF_COOKIE_SECURE = True`
    - [ ] `SECURE_BROWSER_XSS_FILTER = True`
  - [ ] Logging configured for CloudWatch

### Static Files
- [ ] Local static files collected: `python manage.py collectstatic --noinput`
- [ ] No errors during collection
- [ ] Static root directory populated

### Local Testing
- [ ] All unit tests pass: `python manage.py test`
- [ ] Manual testing of key features
- [ ] No database migrations pending: `python manage.py showmigrations`
- [ ] No Django warnings: `python manage.py check`

---

## Phase 3: Elastic Beanstalk Initialization (Day 2)

### EB Application Creation
- [ ] EB initialized: `eb init -p python-3.11 recruithub --region us-east-1`
- [ ] `.elasticbeanstalk/` directory created
- [ ] Application name: `recruithub`
- [ ] Environment name: `recruithub-prod`
- [ ] Region: `us-east-1`

### EB Environment Configuration
- [ ] EB environment created: `eb create recruithub-prod`
- [ ] Instance type: `t3.micro`
- [ ] Load balanced: Yes (ALB created)
- [ ] Environment variables set (see Phase 4)
- [ ] Deployment successful (green health status)

### EB Environment Setup
- [ ] EB CLI working: `eb status`
- [ ] Application accessible: `eb open`
- [ ] Environment details noted:
  - [ ] EB URL: `recruithub-prod.us-east-1.elasticbeanstalk.com`
  - [ ] ALB DNS: `recruithub-prod-alb-xxxxx.us-east-1.elb.amazonaws.com`

---

## Phase 4: Environment Variables Configuration (Day 2)

### Prepare Environment File
- [ ] Copy `.env.prod.example` → `.env.prod`
- [ ] Fill in all required values:
  - [ ] `DEBUG=False`
  - [ ] `SECRET_KEY=[unique-secret-key]`
  - [ ] `RDS_HOSTNAME=[rds-endpoint]`
  - [ ] `RDS_USERNAME=postgres`
  - [ ] `RDS_PASSWORD=[rds-password]`
  - [ ] `RDS_DB_NAME=recruithub`
  - [ ] `RDS_PORT=5432`
  - [ ] `ALLOWED_HOSTS=vakverse.com,www.vakverse.com,*.elasticbeanstalk.com`
  - [ ] Email settings (if not using defaults)
  - [ ] S3 settings (if using)

### Set in Elastic Beanstalk
- [ ] Run: `chmod +x set_eb_env_vars.sh && ./set_eb_env_vars.sh`
- [ ] OR: `eb setenv < .env.prod`
- [ ] OR: Set via AWS Console → EB → Configuration → Software → Environment properties
- [ ] Verify: `eb printenv` shows all variables
- [ ] Sensitive data NOT in version control:
  - [ ] `.env.prod` NOT committed
  - [ ] `.env.prod.example` only (placeholders)

---

## Phase 5: SSL/TLS Certificate Setup (Day 2-3)

### AWS Certificate Manager
- [ ] Navigate to AWS Certificate Manager (ACM)
- [ ] Request certificate:
  - [ ] Domains:
    - `vakverse.com`
    - `*.vakverse.com`
    - `www.vakverse.com`
  - [ ] Validation method: DNS
  - [ ] Request submitted
- [ ] DNS validation records created:
  - [ ] CNAME records added to Route 53 automatically
  - [ ] OR manually added CNAME records
- [ ] Certificate status: Verified (takes 5-30 minutes)
- [ ] Certificate ARN noted: `arn:aws:acm:...`

### ALB Configuration
- [ ] ALB listener on port 443 added:
  - [ ] Protocol: HTTPS
  - [ ] Certificate: ACM certificate selected
  - [ ] Default action: Forward to target group
- [ ] HTTP (port 80) redirect to HTTPS:
  - [ ] Listener rule created
  - [ ] Action: Redirect to HTTPS
- [ ] Security group allows:
  - [ ] Inbound 80 (HTTP)
  - [ ] Inbound 443 (HTTPS)
  - [ ] Outbound to EC2 instances

---

## Phase 6: Route 53 DNS Setup (Day 3)

### Route 53 Hosted Zone
- [ ] Route 53 dashboard opened
- [ ] Hosted zone created: `vakverse.com`
- [ ] Hosted Zone ID noted: `Z____________`
- [ ] Nameservers copied (4 of them)

### DNS Records
- [ ] A record created for root domain:
  - [ ] Name: `vakverse.com`
  - [ ] Type: A
  - [ ] Alias: Yes
  - [ ] Target: ALB DNS name
- [ ] A record created for www:
  - [ ] Name: `www.vakverse.com`
  - [ ] Type: A
  - [ ] Alias: Yes
  - [ ] Target: ALB DNS name
- [ ] ACM validation CNAME (if not auto-added):
  - [ ] Records created and status: Verified
- [ ] (Optional) MX records for email

### Registrar Nameserver Update
- [ ] Login to domain registrar (Namecheap, GoDaddy, etc.)
- [ ] Found DNS/Nameserver settings
- [ ] Updated nameservers to Route 53:
  ```
  ns-123.awsdns-45.com
  ns-456.awsdns-78.net
  ns-789.awsdns-01.org
  ns-012.awsdns-34.com
  ```
- [ ] Changes saved
- [ ] Note: DNS propagation can take 24-48 hours

### DNS Verification
- [ ] DNS propagation started (check at whatsmydns.net)
- [ ] Local DNS resolution: `nslookup vakverse.com`
- [ ] Nameservers correct: `dig vakverse.com NS`
- [ ] A record correct: `dig A vakverse.com`

---

## Phase 7: Application Deployment (Day 3)

### Pre-Deployment Checks
- [ ] All code committed to git
- [ ] No uncommitted changes: `git status`
- [ ] `.ebextensions/` configured correctly
- [ ] `requirements.txt` up to date
- [ ] Django settings validated locally

### Deploy to EB
- [ ] Run: `chmod +x aws_eb_deploy.sh && ./aws_eb_deploy.sh`
- [ ] OR: `eb deploy`
- [ ] Deployment starts...
- [ ] Monitor: `eb logs -z`
- [ ] Watch health: `eb health`

### Deployment Verification
- [ ] Deployment completed: Status shows "Green"
- [ ] EB URL accessible: `eb open` works
- [ ] Django admin reachable: `https://[eb-url]/admin`
- [ ] No errors in logs: `eb logs`
- [ ] Database migrations ran: `eb ssh` → `python manage.py showmigrations`

---

## Phase 8: Functional Testing (Day 3-4)

### Core Features Testing
- [ ] User registration works
- [ ] User login works
- [ ] Password reset works
- [ ] Profile creation works
- [ ] File uploads/downloads work (if applicable)
- [ ] Email notifications sent (if applicable)
- [ ] Admin panel accessible
- [ ] Admin can manage users/content

### HTTPS & Security
- [ ] HTTP redirects to HTTPS
- [ ] Certificate valid: `openssl s_client -connect vakverse.com:443`
- [ ] No mixed content warnings
- [ ] No SSL/TLS errors
- [ ] Security headers present: `curl -I https://vakverse.com`

### Performance Testing
- [ ] Page loads reasonably fast
- [ ] Admin dashboard responsive
- [ ] Database queries efficient
- [ ] No obvious memory leaks
- [ ] CloudWatch metrics normal

### Mobile/Browser Testing
- [ ] Works on Chrome/Firefox/Safari
- [ ] Mobile responsive
- [ ] No console errors

---

## Phase 9: Monitoring & Logging (Day 4)

### CloudWatch Setup
- [ ] CloudWatch Logs enabled
- [ ] Log group created: `/aws/elasticbeanstalk/recruithub-prod`
- [ ] Log retention: 7 days
- [ ] Alarms created:
  - [ ] High CPU (>80%)
  - [ ] Unhealthy hosts
  - [ ] Failed deployments
  - [ ] Disk space

### Application Monitoring
- [ ] EB Health Dashboard configured
- [ ] Health check endpoint working
- [ ] Auto-scaling configured:
  - [ ] Min instances: 1
  - [ ] Max instances: 3
  - [ ] Scale trigger: CPU > 70%
- [ ] CloudWatch agent monitoring enabled

### Log Review
- [ ] Application logs accessible
- [ ] Error patterns identified (if any)
- [ ] Performance baselines established

---

## Phase 10: Database Backups (Day 4)

### RDS Backup Configuration
- [ ] Automated backups enabled: 30 days
- [ ] Backup window: 03:00-04:00 UTC
- [ ] Multi-AZ backup: No (can enable later)
- [ ] Copy backups to another region: No (optional)

### Manual Backup
- [ ] Create manual snapshot now:
  ```bash
  aws rds create-db-snapshot \
      --db-instance-identifier recruithub-db \
      --db-snapshot-identifier recruithub-backup-$(date +%Y%m%d)
  ```
- [ ] Snapshot created and status: Available

### Backup Testing
- [ ] (Optional) Restore from backup to test environment
- [ ] Document restore procedure

---

## Phase 11: Render Decommissioning (Day 4-5)

### Final Render Backup
- [ ] One more export from Render PostgreSQL: `pg_dump`
- [ ] Backup file saved: `final_render_backup.sql`
- [ ] Backed up to external storage (S3, GitHub, personal drive)

### Render Cleanup
- [ ] Verified vakverse.com works on AWS for 24+ hours
- [ ] No issues reported by users
- [ ] Killed Django web service on Render
- [ ] Stopped accepting requests on Render
- [ ] Render database destroyed (IRREVERSIBLE - ensure AWS copy is working)
- [ ] Render domain binding removed
- [ ] Render application deleted
- [ ] Render dashboard cleaned up

### Cost Verification
- [ ] Render services fully stopped
- [ ] No ongoing Render charges
- [ ] AWS RDS/EB running and costs acceptable

---

## Phase 12: Documentation & Handoff (Day 5)

### Documentation Complete
- [ ] README.md updated:
  - [ ] Deployment instructions updated
  - [ ] References Elastic Beanstalk
  - [ ] AWS setup information
- [ ] DEPLOYMENT_GUIDE.md updated:
  - [ ] AWS EB deployment process
  - [ ] Rollback procedure
  - [ ] Troubleshooting section
- [ ] AWS_EB_MIGRATION_GUIDE.md finalized
- [ ] ROUTE53_DNS_SETUP.md finalized
- [ ] Environmental variables documented
- [ ] SSL certificate renewal noted (auto-renewed by ACM)

### Scripts & Tools
- [ ] All deployment scripts executable: `chmod +x *.sh`
- [ ] Scripts documented with examples
- [ ] Emergency procedures documented

### Knowledge Transfer
- [ ] Team trained on EB operations
- [ ] CloudWatch dashboard shared
- [ ] AWS console access verified
- [ ] On-call procedures established

### Post-Launch Monitoring
- [ ] Week 1: Daily check of CloudWatch metrics
- [ ] Week 2-4: Every other day checks
- [ ] Then: Weekly reviews
- [ ] Keep Render emergency contact info for 1-2 weeks

---

## Post-Migration (Ongoing)

### Weekly Tasks
- [ ] [ ] Review CloudWatch metrics
- [ ] [ ] Check error logs
- [ ] [ ] Verify backups created
- [ ] [ ] Monitor costs
- [ ] [ ] Test critical features

### Monthly Tasks
- [ ] [ ] Review security settings
- [ ] [ ] Update dependencies
- [ ] [ ] Test backup restore
- [ ] [ ] Analyze performance trends
- [ ] [ ] Update documentation if needed

### Quarterly Tasks
- [ ] [ ] Security audit
- [ ] [ ] Cost optimization review
- [ ] [ ] DR procedure test
- [ ] [ ] Capacity planning review

---

## Estimated Timeline

| Phase | Duration | Status |
|-------|----------|--------|
| Phase 1: AWS Setup | 1-2 hours | ⏳ |
| Phase 2: Django Prep | 2-4 hours | ⏳ |
| Phase 3: EB Init | 15 minutes | ⏳ |
| Phase 4: Env Vars | 30 minutes | ⏳ |
| Phase 5: SSL Setup | 1 hour | ⏳ |
| Phase 6: Route 53 | 1 hour | ⏳ |
| Phase 7: Deploy | 1-2 hours | ⏳ |
| Phase 8: Testing | 2-4 hours | ⏳ |
| Phase 9: Monitoring | 1 hour | ⏳ |
| Phase 10: Backups | 30 minutes | ⏳ |
| Phase 11: Cleanup | 1 hour | ⏳ |
| Phase 12: Docs | 2 hours | ⏳ |
| **TOTAL** | **14-20 hours** | |

**Recommendation:** Spread over 3-5 days for safety and testing

---

## Success Criteria

- ✅ vakverse.com resolves to AWS ALB
- ✅ HTTPS working with valid certificate
- ✅ Application accessible and functional
- ✅ Database migrated and verified
- ✅ All features working identically to Render
- ✅ CloudWatch monitoring active
- ✅ Backups configured and tested
- ✅ No user-facing downtime
- ✅ Costs acceptable (<$100/month)
- ✅ Documentation complete

---

## Emergency Rollback Plan

If critical issues occur:

```bash
# 1. Immediately update Route 53 to point back to Render
aws route53 change-resource-record-sets \
    --hosted-zone-id Z__________ \
    --change-batch file://rollback.json

# 2. Revert nameservers at registrar (if possible)

# 3. Scale down EB (stop charges):
eb scale 0

# 4. Investigate issue in parallel
eb logs --all

# 5. Once fixed, redeploy to AWS
```

**Keep Render database backup accessible for 2 weeks post-launch**

---

## Contact & Support

- [ ] AWS Support Plan: Business ($100/month) - Consider for launch week
- [ ] EB Documentation: https://docs.aws.amazon.com/elasticbeanstalk/
- [ ] Route 53 Guide: https://docs.aws.amazon.com/route53/
- [ ] Django + AWS: https://docs.djangoproject.com/en/stable/howto/deployment/
