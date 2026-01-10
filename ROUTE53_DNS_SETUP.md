# AWS Route 53 & DNS Configuration Guide

## Quick Summary
Migrate DNS from Render to AWS Route 53 for domain `vakverse.com`

---

## Step 1: Get ALB DNS Name (from EB)

```bash
# Find the ALB endpoint
eb status

# Look for: "Load Balancer: recruithub-prod-alb-XXXXXXXXX.us-east-1.elb.amazonaws.com"
# Or check AWS Console → EC2 → Load Balancers
```

**Example:**
```
recruithub-prod-alb-12345678.us-east-1.elb.amazonaws.com
```

---

## Step 2: Create Route 53 Hosted Zone

### Via AWS Console:
1. **Go to Route 53 Dashboard**
2. **Click "Create hosted zone"**
3. **Domain name:** `vakverse.com`
4. **Type:** Public hosted zone
5. **Click "Create hosted zone"**

### Via AWS CLI:
```bash
aws route53 create-hosted-zone \
    --name vakverse.com \
    --caller-reference "vakverse-$(date +%s)" \
    --region us-east-1
```

**Note the Hosted Zone ID** (e.g., `Z1234ABCD5678`)

---

## Step 3: Add DNS Records

### Record 1: Alias for Root Domain (@)

**Via Console:**
1. Click "Create record"
2. Record name: Leave blank (or `vakverse.com`)
3. Type: `A`
4. Alias: **Yes**
5. Alias target: Select ALB from dropdown
   - Search: `recruithub-prod-alb`
   - Select: `recruithub-prod-alb-xxxxx.us-east-1.elb.amazonaws.com`
6. Routing policy: `Simple`
7. Evaluate target health: Yes
8. Create record

**Via CLI:**
```bash
aws route53 change-resource-record-sets \
    --hosted-zone-id Z1234ABCD5678 \
    --change-batch '{
      "Changes": [{
        "Action": "CREATE",
        "ResourceRecordSet": {
          "Name": "vakverse.com",
          "Type": "A",
          "AliasTarget": {
            "HostedZoneId": "Z35SXDOTRQ7X7K",
            "DNSName": "recruithub-prod-alb-12345678.us-east-1.elb.amazonaws.com",
            "EvaluateTargetHealth": true
          }
        }
      }]
    }'
```

### Record 2: Alias for www Subdomain

**Via Console:**
1. Click "Create record"
2. Record name: `www`
3. Type: `A`
4. Alias: **Yes**
5. Alias target: Same ALB as above
6. Routing policy: `Simple`
7. Evaluate target health: Yes
8. Create record

**Via CLI:**
```bash
aws route53 change-resource-record-sets \
    --hosted-zone-id Z1234ABCD5678 \
    --change-batch '{
      "Changes": [{
        "Action": "CREATE",
        "ResourceRecordSet": {
          "Name": "www.vakverse.com",
          "Type": "A",
          "AliasTarget": {
            "HostedZoneId": "Z35SXDOTRQ7X7K",
            "DNSName": "recruithub-prod-alb-12345678.us-east-1.elb.amazonaws.com",
            "EvaluateTargetHealth": true
          }
        }
      }]
    }'
```

### Record 3: Email (Optional - if using SES)

**Via Console:**
1. Click "Create record"
2. Record name: Leave blank
3. Type: `MX`
4. Value: `10 mail.vakverse.com` (or SES endpoint)
5. TTL: `3600`
6. Create record

---

## Step 4: Update Nameservers at Registrar

### Copy Route 53 Nameservers

**Route 53 Console:**
1. Click on hosted zone `vakverse.com`
2. Scroll down to "Nameservers"
3. Copy the 4 nameservers:
   ```
   ns-123.awsdns-45.com
   ns-456.awsdns-78.net
   ns-789.awsdns-01.org
   ns-012.awsdns-34.com
   ```

### Update at Your Registrar

**Namecheap (most common):**
1. Login to Namecheap
2. Go to "Manage" for vakverse.com
3. Scroll to "Nameservers"
4. Select "Custom DNS"
5. Paste the 4 Route 53 nameservers
6. Save

**GoDaddy:**
1. Login to GoDaddy
2. Go to "Manage DNS"
3. Find "Nameservers"
4. Change to custom nameservers
5. Paste Route 53 nameservers
6. Save

**Other Registrars:**
- Look for "Nameserver" or "DNS" settings
- Change to custom/external nameservers
- Paste the 4 Route 53 nameservers

---

## Step 5: Add SSL Certificate

### Create in AWS Certificate Manager

**Via Console:**
1. **Go to Certificate Manager**
2. **Click "Request certificate"**
3. **Fully qualified domain names:**
   ```
   vakverse.com
   *.vakverse.com
   www.vakverse.com
   ```
4. **Validation method:** DNS validation
5. **Click "Request"**

**Validate DNS:**
1. Click "Create records in Route 53" (auto-add CNAME)
2. Or manually add CNAME records:
   ```
   Name: _xxxxx.vakverse.com
   Value: _xxxxx.acm-validations.aws
   ```
3. Validation takes 5-30 minutes

### Create via CLI

```bash
aws acm request-certificate \
    --domain-name vakverse.com \
    --subject-alternative-names www.vakverse.com '*.vakverse.com' \
    --validation-method DNS \
    --region us-east-1
```

---

## Step 6: Attach Certificate to ALB

**Via AWS Console:**

1. **Go to EC2 → Load Balancers**
2. **Select ALB** (recruithub-prod-alb)
3. **Go to "Listeners" tab**
4. **Edit Listener for port 443:**
   - Add/Edit HTTPS listener
   - Port: `443`
   - Protocol: `HTTPS`
   - Default certificate: Select from ACM
5. **Update listener for port 80:**
   - Add redirect rule: `HTTP → HTTPS`

**Via CLI:**

```bash
# Get ALB ARN
ALB_ARN=$(aws elbv2 describe-load-balancers \
    --names "recruithub-prod-alb" \
    --query 'LoadBalancers[0].LoadBalancerArn' \
    --output text)

# Get certificate ARN
CERT_ARN=$(aws acm list-certificates \
    --region us-east-1 \
    --query 'CertificateSummaryList[0].CertificateArn' \
    --output text)

# Add HTTPS listener
aws elbv2 create-listener \
    --load-balancer-arn $ALB_ARN \
    --protocol HTTPS \
    --port 443 \
    --certificates CertificateArn=$CERT_ARN \
    --default-actions Type=forward,TargetGroupArn=$TARGET_GROUP_ARN
```

---

## Step 7: Verify DNS Resolution

```bash
# Check DNS propagation
nslookup vakverse.com
# Should return ALB IP address

# Check nameservers
dig vakverse.com NS
# Should show Route 53 nameservers

# Check specific records
dig A vakverse.com
dig CNAME www.vakverse.com

# Full DNS trace
dig +trace vakverse.com

# Online: https://www.whatsmydns.net/
# Enter: vakverse.com
```

---

## Step 8: Test HTTPS

```bash
# Test HTTP → HTTPS redirect
curl -I http://vakverse.com
# Should return 301 with location: https://vakverse.com

# Test HTTPS
curl -I https://vakverse.com
# Should return 200

# Test SSL certificate
openssl s_client -connect vakverse.com:443
# Should show valid certificate for vakverse.com
```

---

## Troubleshooting

### DNS Not Resolving

```bash
# Check if nameservers are updated
whois vakverse.com | grep -i nameserver

# Check Route 53 records
aws route53 list-resource-record-sets \
    --hosted-zone-id Z1234ABCD5678

# DNS propagation can take 24-48 hours
# Check status: https://www.whatsmydns.net/
```

### Certificate Not Valid

```bash
# Check certificate status
aws acm describe-certificate \
    --certificate-arn arn:aws:acm:region:account:certificate/id

# Validate DNS records exist
aws route53 list-resource-record-sets \
    --hosted-zone-id Z1234ABCD5678 \
    --query "ResourceRecordSets[?contains(Name, '_')]"
```

### Redirect Loop

- Ensure ALB listener correctly configured
- Check security group allows ports 80 & 443
- Verify HTTPS redirect only on port 80
- Check Django `SECURE_SSL_REDIRECT` setting

### Mixed Content Warnings

- Ensure all assets use HTTPS
- Update Django static/media URLs
- Check S3 bucket URLs if using external storage

---

## Complete DNS Record Summary

| Name | Type | Value | TTL |
|------|------|-------|-----|
| vakverse.com | A | ALB Alias | 300 |
| www | A | ALB Alias | 300 |
| mail | MX | 10 mail.vakverse.com | 3600 |
| _xxxxx (cert validation) | CNAME | _xxxxx.acm-validations.aws | 300 |

---

## Cost Considerations

| Item | Cost |
|------|------|
| Hosted Zone | $0.50/month |
| DNS Queries | $0.40 per million |
| ACM Certificate | FREE |
| **Total** | **~$1/month** |

---

## Rollback to Previous DNS

If you need to rollback:

```bash
# Keep old Route 53 records
# Update registrar nameservers back to previous provider
# Or update Route 53 records to point to old IP

# Update at registrar (Namecheap, GoDaddy, etc.)
# Change nameservers back to original
```

---

## Next Steps

1. ✅ Create Route 53 hosted zone
2. ✅ Add A records for vakverse.com and www
3. ✅ Update nameservers at registrar
4. ⏳ Wait 24-48 hours for DNS propagation
5. ✅ Create SSL certificate in ACM
6. ✅ Attach certificate to ALB
7. ✅ Verify HTTPS working
8. ✅ Monitor CloudWatch logs
