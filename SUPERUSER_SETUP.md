# Superuser Setup from Environment Variables

## Overview
This system allows you to create the Django admin superuser using environment variables, but **only during initial setup**. After creation, the superuser is stored in the database and Django uses normal database authentication.

## Security Approach ✅

1. **Environment variables used ONCE** - during initial setup
2. **Password stored in database** - as hashed password (secure)
3. **Login authenticated by Django** - using database, not env vars
4. **No env var checks on every login** - much more secure

## Setup Instructions

### Option 1: Automatic Setup (Recommended)

The startup script automatically creates the superuser if you set these environment variables:

```bash
export ADMIN_USERNAME=admin
export ADMIN_PASSWORD=your_secure_password_here
export ADMIN_EMAIL=admin@recruithub.com
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
export ADMIN_USERNAME=admin
export ADMIN_PASSWORD=your_secure_password_here
export ADMIN_EMAIL=admin@recruithub.com

python manage.py create_superuser_from_env
```

### Option 3: Update Existing Superuser

To change the superuser password later:

```bash
export ADMIN_USERNAME=admin
export ADMIN_PASSWORD=new_secure_password
export ADMIN_EMAIL=admin@recruithub.com

python manage.py create_superuser_from_env
```

This will **update** the existing superuser with the new credentials.

## Environment Variables Required

| Variable | Purpose | Example |
|----------|---------|---------|
| `ADMIN_USERNAME` | Django admin username | `admin` |
| `ADMIN_PASSWORD` | Admin password (will be hashed) | `MySecure$Password123` |
| `ADMIN_EMAIL` | Admin email address | `admin@recruithub.com` |

## How It Works

### Startup Process
```
1. run_startup.py starts
   ↓
2. Run database migrations
   ↓
3. Initialize default data
   ↓
4. Check for ADMIN_USERNAME, ADMIN_PASSWORD, ADMIN_EMAIL env vars
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
unset ADMIN_USERNAME
unset ADMIN_PASSWORD
unset ADMIN_EMAIL
```

The app will still work fine because the superuser is now in the database.

## Login Process

After initial setup, login to `/admin/` using:
- **Username**: Whatever you set in `ADMIN_USERNAME`
- **Password**: Whatever you set in `ADMIN_PASSWORD`

Django will authenticate against the **database**, not environment variables.

## Changing Password Later

If you need to change the admin password:

```bash
# Option A: Using the command
export ADMIN_USERNAME=admin
export ADMIN_PASSWORD=new_password
python manage.py create_superuser_from_env

# Option B: Using Django shell
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(username='admin')
>>> user.set_password('new_password')
>>> user.save()

# Option C: Using manage.py (traditional Django way)
python manage.py changepassword admin
```

## In Production (Render.com)

1. Set environment variables in Render dashboard:
   - `ADMIN_USERNAME=admin`
   - `ADMIN_PASSWORD=your_secure_password`
   - `ADMIN_EMAIL=admin@recruithub.com`

2. Deploy the app

3. First deployment will create the superuser automatically

4. After that, you can remove the `ADMIN_PASSWORD` from Render (optional)
   - Or keep it for quick updates with the command

## Security Benefits ✅

| Aspect | This Approach | Previous Approach |
|--------|------|------|
| Password Storage | Hashed in database ✅ | Checked every login ⚠️ |
| Exposure Risk | Low (one-time use) | Medium (env var check on every request) |
| Logs | No passwords logged | Potential password in logs |
| Rotation | Easy (change in dashboard) | Easy (change env var) |
| Breach Impact | Only this app | Only this app |

## Troubleshooting

### "ADMIN_USERNAME environment variable not set"

Set all three environment variables:
```bash
export ADMIN_USERNAME=admin
export ADMIN_PASSWORD=your_password
export ADMIN_EMAIL=admin@example.com
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
python manage.py changepassword admin
```

Or use the environment variables approach:
```bash
export ADMIN_PASSWORD=new_password
python manage.py create_superuser_from_env
```

## Summary

✅ **This approach is MORE secure than checking env vars on every login**
- Environment variables used only **once** during setup
- Password stored **safely hashed** in database
- No env vars checked during authentication
- Standard Django security mechanisms
