# Superuser Setup from Environment Variables

## Overview
This system uses **Django's official environment variables** to create the Django admin superuser. Environment variables are used **only during initial setup**. After creation, the superuser is stored in the database and Django uses normal database authentication.

## Security Approach ✅

1. **Environment variables used ONCE** - during initial setup only
2. **Password stored in database** - as hashed password (secure)
3. **Login authenticated by Django** - using database, not env vars
4. **No env var checks on every login** - much more secure

## Setup Instructions

### Option 1: Automatic Setup (Recommended)

The startup script automatically creates the superuser if you set these environment variables:

```bash
export DJANGO_SUPERUSER_USERNAME=tapdiyaom
export DJANGO_SUPERUSER_PASSWORD=Admin123456
export DJANGO_SUPERUSER_EMAIL=admin@recruithub.com
```

Then start the app:
```bash
python run_startup.py
# OR in production:
gunicorn auth_project.wsgi:application
```

The superuser will be created automatically on first run.

### Option 2: Manual Setup

If you didn't set the environment variables during startup, you can create the superuser later:

```bash
export DJANGO_SUPERUSER_USERNAME=tapdiyaom
export DJANGO_SUPERUSER_PASSWORD=Admin123456
export DJANGO_SUPERUSER_EMAIL=admin@recruithub.com

python manage.py create_superuser_from_env
```

### Option 3: Update Existing Superuser

To change the superuser password later:

```bash
export DJANGO_SUPERUSER_USERNAME=tapdiyaom
export DJANGO_SUPERUSER_PASSWORD=NewSecurePassword
export DJANGO_SUPERUSER_EMAIL=admin@recruithub.com

python manage.py create_superuser_from_env
```

This will **update** the existing superuser with the new credentials.

## Environment Variables Required

These are **Django's official environment variables**:

| Variable | Purpose | Example |
|----------|---------|---------|
| `DJANGO_SUPERUSER_USERNAME` | Django admin username | `tapdiyaom` |
| `DJANGO_SUPERUSER_PASSWORD` | Admin password (will be hashed) | `Admin123456` |
| `DJANGO_SUPERUSER_EMAIL` | Admin email address | `admin@recruithub.com` |

> **Note**: These are the official Django variables used by the `createsuperuser` command. Already in `.env.example`.

## How It Works

### Startup Process
```
1. run_startup.py starts
   ↓
2. Run database migrations
   ↓
3. Initialize default data
   ↓
4. Check for DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_PASSWORD, DJANGO_SUPERUSER_EMAIL
   ├─ If set: Call create_superuser_from_env
   │  └─ Reads env vars ONCE
   │  └─ Creates/updates superuser in database
   │  └─ NEVER touches env vars again
   └─ If not set: Skip (will create manually later)
   ↓
5. App starts normally
   ↓
6. User logs in via /admin/
   ├─ Django checks database for user
   ├─ Compares passwords (database-stored hash)
   ├─ No env vars involved
   └─ Authentication complete ✅
```

### After Initial Setup

Once the superuser is created:
- **Environment variables are no longer used**
- **Database stores the hashed password**
- **Django handles authentication normally**
- **You can unset the env variables if you want**

```bash
# Optional: Clear env vars after setup
unset DJANGO_SUPERUSER_USERNAME
unset DJANGO_SUPERUSER_PASSWORD
unset DJANGO_SUPERUSER_EMAIL
```

The app will still work fine because the superuser is now in the database.

## Login Process

After initial setup, login to `/admin/` using:
- **Username**: Whatever you set in `DJANGO_SUPERUSER_USERNAME` (e.g., `tapdiyaom`)
- **Password**: Whatever you set in `DJANGO_SUPERUSER_PASSWORD` (e.g., `Admin123456`)

Django will authenticate against the **database**, not environment variables.

## Changing Password Later

If you need to change the admin password:

```bash
# Option A: Using the command
export DJANGO_SUPERUSER_USERNAME=tapdiyaom
export DJANGO_SUPERUSER_PASSWORD=NewPassword
export DJANGO_SUPERUSER_EMAIL=admin@recruithub.com
python manage.py create_superuser_from_env

# Option B: Using Django shell
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(username='tapdiyaom')
>>> user.set_password('NewPassword')
>>> user.save()

# Option C: Using manage.py (traditional Django way)
python manage.py changepassword tapdiyaom
```

## In Production (Render.com)

1. Set environment variables in Render dashboard:
   - `DJANGO_SUPERUSER_USERNAME=tapdiyaom`
   - `DJANGO_SUPERUSER_PASSWORD=Admin123456`
   - `DJANGO_SUPERUSER_EMAIL=admin@recruithub.com`

2. Deploy the app

3. First deployment will create the superuser automatically

4. After that, you can remove the `DJANGO_SUPERUSER_PASSWORD` from Render (optional)
   - Or keep it for quick updates with the command

## Security Benefits ✅

| Aspect | This Approach | Checking Env Vars on Every Login |
|--------|------|------|
| Password Storage | Hashed in database ✅ | Would check plaintext ⚠️ |
| Exposure Risk | Low (one-time use) | Medium (env var check on every request) |
| Logs | No passwords logged | Potential passwords in logs |
| Rotation | Easy (change env var) | Easy (change env var) |
| Official Django | ✅ Yes | ❌ No |
| Breach Impact | Only this app | Only this app |

## Troubleshooting

### "DJANGO_SUPERUSER_USERNAME environment variable not set"

Set all three environment variables:
```bash
export DJANGO_SUPERUSER_USERNAME=tapdiyaom
export DJANGO_SUPERUSER_PASSWORD=Admin123456
export DJANGO_SUPERUSER_EMAIL=admin@recruithub.com
python manage.py create_superuser_from_env
```

### Can't login to admin

Make sure you:
1. Created the superuser (check with the command above)
2. Using correct username and password
3. Database migrations ran successfully

### Forgot the admin password?

Set a new one:
```bash
python manage.py changepassword tapdiyaom
```

Or use the environment variables approach:
```bash
export DJANGO_SUPERUSER_PASSWORD=new_password
python manage.py create_superuser_from_env
```

## Summary

✅ **Using Django's Official Environment Variables**
- Environment variables used only **once** during setup
- Password stored **safely hashed** in database
- No env vars checked during authentication
- Standard Django security mechanisms
- Already in `.env.example`
