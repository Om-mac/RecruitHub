# S3 CORS & CSP Fix - Complete Setup Guide

## Issues Resolved

### 1. **CSP Error** (Content Security Policy)
```
Error: The source list for Content Security Policy directive 'connect-src' 
contains an invalid source: 'https://*.s3-*.amazonaws.com'
```
**Cause**: Django CSP policy didn't allow connections to S3

**Fix**: Updated `auth_project/settings.py` to add S3 domains to `connect-src` directive

### 2. **CORS Error** (Cross-Origin Resource Sharing)
```
Error: Origin https://vakverse.com is not allowed by 
Access-Control-Allow-Origin. Status code: 403
```
**Cause**: S3 bucket wasn't configured to accept requests from your domain

**Fix**: Configure S3 bucket CORS policy to allow requests from `https://vakverse.com`

## Implementation Steps

### Step 1: Verify CSP Settings ✅
Already updated in `auth_project/settings.py`:

```python
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
    "script-src": ("'self'", "'unsafe-inline'", "cdn.jsdelivr.net", "cdnjs.cloudflare.com"),
    "style-src": ("'self'", "'unsafe-inline'", "cdn.jsdelivr.net", "cdnjs.cloudflare.com"),
    "img-src": ("'self'", "data:", "*.s3.amazonaws.com", "*.s3.*.amazonaws.com"),
    "font-src": ("'self'", "cdnjs.cloudflare.com", "fonts.googleapis.com", "fonts.gstatic.com"),
    "connect-src": ("'self'", "*.s3.amazonaws.com", "*.s3.*.amazonaws.com"),  # ← NEW
}
```

**What it does**: Allows your browser to connect to S3 domains for uploads and downloads.

### Step 2: Configure S3 CORS Policy

Run the provided setup script:

```bash
# Ensure environment variables are set
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_STORAGE_BUCKET_NAME="recruithub-amzn-bucket"
export AWS_S3_REGION_NAME="us-east-1"
export DOMAIN_NAME="https://vakverse.com"

# Run the configuration script
python configure_s3_cors.py
```

**What it does**: Configures the S3 bucket to accept requests from your domain.

**CORS Rules Applied**:
- ✅ Allow GET, PUT, POST, DELETE, HEAD methods
- ✅ Allow requests from `https://vakverse.com` and `https://www.vakverse.com`
- ✅ Allow custom headers (`*`)
- ✅ Cache policy for 3000 seconds (50 minutes)

### Step 3: Verify Everything Works

After running the configuration:

1. **Restart Django Server**:
   ```bash
   python manage.py runserver
   ```

2. **Test Upload**:
   - Go to Dashboard → Upload Document
   - Select a PDF/image file
   - Click Upload
   - Should complete without CORS errors

3. **Test Download**:
   - Go to Dashboard → Documents section
   - Click Download on a document
   - File should download successfully

## Understanding the Fix

### How Presigned URLs Work

1. **User clicks "Download"** → Browser sends request to Django
2. **Django validates** → Checks if user owns the file
3. **Django generates** → Creates a presigned URL (valid 5 minutes)
4. **Returns URL** → Browser gets the temporary S3 URL
5. **Browser downloads** → Uses presigned URL directly from S3
6. **URL expires** → After 5 minutes, URL becomes invalid

### Why CORS is Required

```
Browser (vakverse.com)
    ↓
Django Server (vakverse.com)
    ↓
S3 Bucket (s3.amazonaws.com) ← REQUIRES CORS!
```

Without CORS configured on S3, the browser blocks cross-origin requests from `vakverse.com` to `s3.amazonaws.com`.

### Why CSP Header is Required

Modern browsers enforce Content Security Policy to prevent XSS attacks. The CSP header tells the browser which domains are safe to connect to.

**Our CSP allows**:
- `'self'` → Your own domain (vakverse.com)
- `*.s3.amazonaws.com` → All AWS S3 endpoints
- `*.s3.*.amazonaws.com` → S3 endpoints with region (e.g., s3.us-east-1.amazonaws.com)

## Troubleshooting

### Still Getting CORS Errors?

1. **Verify environment variables**:
   ```bash
   echo $AWS_ACCESS_KEY_ID
   echo $AWS_STORAGE_BUCKET_NAME
   ```

2. **Check S3 CORS configuration**:
   ```python
   import boto3
   s3 = boto3.client('s3')
   cors = s3.get_bucket_cors(Bucket='recruithub-amzn-bucket')
   print(cors['CORSRules'])
   ```

3. **Verify bucket name** is correct (no typos)

4. **Check AWS credentials** have `s3:PutBucketCors` permission

### Still Getting CSP Errors?

1. **Clear browser cache** (Ctrl+Shift+Delete)
2. **Restart Django server**
3. **Check that CSP header is being sent**:
   - Open DevTools → Network → Click a request
   - Look for `Content-Security-Policy` header

## Files Modified

1. ✅ `auth_project/settings.py` - Added `connect-src` to CSP
2. ✅ `configure_s3_cors.py` - New script to set up S3 CORS
3. ✅ `core/templates/core/dashboard.html` - Using presigned URLs for downloads
4. ✅ `core/admin.py` - Admin panel using presigned URLs

## Security Features

✅ **Presigned URLs expire** in 5 minutes  
✅ **Only authenticated users** can request URLs  
✅ **Ownership validation** prevents IDOR attacks  
✅ **CSP headers** prevent XSS attacks  
✅ **CORS restricted** to your domain only  
✅ **Bucket policies** restrict public access  

## Next Steps

If you still encounter issues:

1. Check CloudWatch logs for S3 errors
2. Verify S3 bucket public access settings
3. Ensure IAM user has correct permissions
4. Test with browser DevTools to see actual S3 response

## Commands Reference

```bash
# Configure S3 CORS
python configure_s3_cors.py

# Verify S3 bucket CORS
aws s3api get-bucket-cors --bucket recruithub-amzn-bucket

# Check Django CSP headers
curl -I https://vakverse.com/dashboard/ | grep -i content-security

# View S3 bucket policy
aws s3api get-bucket-policy --bucket recruithub-amzn-bucket
```
