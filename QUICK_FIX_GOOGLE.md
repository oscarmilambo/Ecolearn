# Quick Fix Applied ✅

## Issue Fixed
The `MultipleObjectsReturned` error was caused by the `APP` configuration in `SOCIALACCOUNT_PROVIDERS`. 

## What I Changed
Removed the `APP` dictionary from settings.py. Google credentials should only be configured in Django admin, not in both places.

## ✅ Fixed Configuration

```python
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'}
    }
}
```

## 🚀 Next Steps

1. **Restart your Django server** (Ctrl+C, then `python manage.py runserver`)

2. **Visit registration page:**
   ```
   http://127.0.0.1:8000/accounts/register/
   ```

3. **You should see:**
   - Email registration form
   - "Continue with Google" button

## 📝 Note

The Google app is already configured in your database with ID: 1. The credentials are stored there, not in settings.py.

If you need to update Google credentials:
1. Go to: http://127.0.0.1:8000/admin/socialaccount/socialapp/
2. Edit the existing Google app
3. Update Client ID and Secret

**The error should now be resolved!** ✅
