# 🔧 Fix Google OAuth Connection Error

## Problem
Getting `ConnectionRefusedError` when trying to use Google OAuth login.

## Root Cause
The redirect URI is not properly configured in Google Cloud Console.

## ✅ Solution Steps

### 1. Go to Google Cloud Console
Visit: https://console.cloud.google.com/

### 2. Select Your Project
- If you don't have a project, create one
- Select the project containing your OAuth app

### 3. Enable Google+ API (if not already enabled)
- Go to "APIs & Services" > "Library"
- Search for "Google+ API" 
- Click "Enable"

### 4. Configure OAuth Consent Screen
- Go to "APIs & Services" > "OAuth consent screen"
- Choose "External" user type
- Fill in required fields:
  - App name: "EcoLearn"
  - User support email: your email
  - Developer contact: your email
- Save and continue through all steps

### 5. Create/Update OAuth 2.0 Client
- Go to "APIs & Services" > "Credentials"
- Click "Create Credentials" > "OAuth 2.0 Client ID"
- Application type: "Web application"
- Name: "EcoLearn Web Client"

### 6. Add Authorized Redirect URIs
**CRITICAL:** Add these exact URIs:
```
http://127.0.0.1:8000/accounts/google/login/callback/
http://localhost:8000/accounts/google/login/callback/
```

### 7. Copy Credentials
- Copy the Client ID and Client Secret
- Update your `.env` file:
```
GOOGLE_CLIENT_ID=your_actual_client_id_here
GOOGLE_CLIENT_SECRET=your_actual_client_secret_here
```

### 8. Update Django Configuration
Run the setup script again:
```bash
python setup_google_oauth.py
```

## 🧪 Test the Fix

1. Start your Django server:
```bash
python manage.py runserver
```

2. Visit the registration page:
```
http://127.0.0.1:8000/accounts/register/
```

3. Click "Continue with Google"

4. You should be redirected to Google's OAuth page without errors

## 🚨 Common Issues

### Issue 1: "redirect_uri_mismatch"
**Solution:** Make sure the redirect URI in Google Console exactly matches:
`http://127.0.0.1:8000/accounts/google/login/callback/`

### Issue 2: "access_blocked"
**Solution:** 
- Make sure OAuth consent screen is configured
- Add your email as a test user if app is in testing mode

### Issue 3: Still getting ConnectionRefusedError
**Solution:**
- Check internet connection
- Try using `localhost` instead of `127.0.0.1`
- Make sure no firewall is blocking the connection

## 📝 Current Configuration Status

✅ Django allauth installed and configured
✅ Google OAuth app created in Django admin
✅ Redirect URIs identified
⚠️  Need to verify Google Cloud Console setup

## 🔄 Alternative: Disable Google OAuth Temporarily

If you want to test registration without Google OAuth, you can temporarily comment out the Google login button in the template:

```html
<!-- Temporarily disabled
<div class="mt-6">
    <a href="{% provider_login_url 'google' %}" 
       class="w-full flex justify-center items-center py-3 px-4 border-2 border-gray-300 rounded-lg shadow-sm text-base font-semibold text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-all">
        <svg class="w-5 h-5 mr-2" viewBox="0 0 24 24">
            <!-- Google icon SVG -->
        </svg>
        Continue with Google
    </a>
</div>
-->
```

This will allow you to test the new registration form fields without the Google OAuth dependency.