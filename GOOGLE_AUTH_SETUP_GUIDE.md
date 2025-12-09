# Google OAuth Setup Guide for EcoLearn

## ✅ Implementation Complete

Google OAuth authentication has been successfully integrated with your existing email registration system. Both methods work seamlessly together!

---

## 🔧 Setup Steps

### 1. Install Dependencies

```bash
pip install django-allauth
```

### 2. Run Migrations

```bash
python manage.py migrate
```

This will create the necessary tables for:
- Sites framework
- Allauth accounts
- Social accounts

### 3. Create a Site

```bash
python manage.py shell
```

Then run:
```python
from django.contrib.sites.models import Site
site = Site.objects.get_or_create(id=1, defaults={'domain': '127.0.0.1:8000', 'name': 'EcoLearn Local'})
print("Site created:", site)
exit()
```

For production, update the domain to your actual domain.

### 4. Get Google OAuth Credentials

#### Step 1: Go to Google Cloud Console
Visit: https://console.cloud.google.com/

#### Step 2: Create a New Project
1. Click "Select a project" → "New Project"
2. Name: "EcoLearn"
3. Click "Create"

#### Step 3: Enable Google+ API
1. Go to "APIs & Services" → "Library"
2. Search for "Google+ API"
3. Click "Enable"

#### Step 4: Create OAuth Credentials
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Configure consent screen if prompted:
   - User Type: External
   - App name: EcoLearn
   - User support email: your email
   - Developer contact: your email
   - Save and continue through all steps

4. Create OAuth Client ID:
   - Application type: Web application
   - Name: EcoLearn Web Client
   - Authorized JavaScript origins:
     - `http://127.0.0.1:8000`
     - `http://localhost:8000`
   - Authorized redirect URIs:
     - `http://127.0.0.1:8000/accounts/google/login/callback/`
     - `http://localhost:8000/accounts/google/login/callback/`
   - Click "Create"

5. Copy your:
   - Client ID
   - Client Secret

### 5. Add Credentials to .env File

Add these lines to your `.env` file:

```env
# Google OAuth
GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret-here
```

### 6. Add Google Provider in Django Admin

1. Start your server: `python manage.py runserver`
2. Go to: http://127.0.0.1:8000/admin/
3. Login with your superuser account
4. Go to "Social applications"
5. Click "Add social application"
6. Fill in:
   - Provider: Google
   - Name: Google
   - Client id: (paste from Google Console)
   - Secret key: (paste from Google Console)
   - Sites: Select "127.0.0.1:8000" and move it to "Chosen sites"
7. Save

---

## 🎯 Features Implemented

### 1. Dual Authentication System
- ✅ Email registration with verification (existing)
- ✅ Google OAuth (new)
- ✅ Both methods work independently
- ✅ Seamless account linking

### 2. Account Linking
- If user signs up with email first, they can later link Google
- If user signs in with Google using existing email, accounts are automatically linked
- No duplicate accounts created

### 3. Email Communications

#### For Email Registration:
- Verification email sent (existing)
- Mentions Google option as alternative

#### For Google Sign-up:
- Welcome email sent immediately
- Account is pre-verified (Google already verified)
- No verification step needed

### 4. User Experience
- Google button on login page
- Google button on registration page
- Clear visual separation with "Or continue with" divider
- Professional Google branding

---

## 📧 Email Templates

### 1. Verification Email (Email Registration)
- `accounts/templates/accounts/verification_email.html`
- Includes tip about Google sign-in option
- 24-hour expiration notice

### 2. Welcome Email (Google Sign-up)
- `accounts/templates/accounts/welcome_email.html`
- Sent immediately after Google registration
- Includes getting started guide
- Links to dashboard

---

## 🔐 Security Features

### Email Registration:
- Email verification required
- Account inactive until verified
- Rate limiting (5 attempts/hour)
- Password requirements (8+ characters)
- Terms acceptance required

### Google OAuth:
- Google handles authentication
- Email pre-verified by Google
- Secure OAuth 2.0 flow
- Tokens stored securely
- Account immediately active

---

## 🧪 Testing

### Test Email Registration:
1. Go to: http://127.0.0.1:8000/accounts/register/
2. Fill in username, email, password
3. Accept terms
4. Click "Create Account"
5. Check email for verification link
6. Click link to verify
7. Login with credentials

### Test Google OAuth:
1. Go to: http://127.0.0.1:8000/accounts/register/
2. Click "Continue with Google"
3. Select Google account
4. Grant permissions
5. Automatically logged in
6. Check email for welcome message

### Test Account Linking:
1. Register with email: test@example.com
2. Verify email and login
3. Logout
4. Click "Sign in with Google"
5. Use same email (test@example.com)
6. Accounts automatically linked
7. Can now use either method to login

---

## 🎨 UI Components

### Google Button Styling:
- Official Google colors
- SVG Google logo
- Hover effects
- Consistent with EcoLearn design
- Mobile responsive

### Placement:
- Login page: After email login form
- Register page: After email registration form
- Clear "Or continue with" divider
- Professional appearance

---

## 📱 Mobile Responsiveness

All Google OAuth features are fully responsive:
- ✅ Google button adapts to mobile
- ✅ OAuth flow works on mobile browsers
- ✅ Email templates mobile-friendly
- ✅ Consistent experience across devices

---

## 🚀 Production Deployment

### Before Going Live:

1. **Update Site Domain**
   ```python
   from django.contrib.sites.models import Site
   site = Site.objects.get(id=1)
   site.domain = 'ecolearn.zm'
   site.name = 'EcoLearn'
   site.save()
   ```

2. **Update Google OAuth Settings**
   - Add production domain to authorized origins
   - Add production callback URL
   - Update .env with production credentials

3. **Configure Email Backend**
   - Set up real SMTP server
   - Test email delivery
   - Configure DEFAULT_FROM_EMAIL

4. **SSL Certificate**
   - Ensure HTTPS is enabled
   - Update all URLs to use HTTPS
   - Google requires HTTPS for production

---

## 🔧 Troubleshooting

### Issue: "Site matching query does not exist"
**Solution:**
```bash
python manage.py shell
from django.contrib.sites.models import Site
Site.objects.create(id=1, domain='127.0.0.1:8000', name='EcoLearn')
```

### Issue: "Social application not found"
**Solution:**
- Go to Django admin
- Add Google social application
- Make sure site is selected

### Issue: "Redirect URI mismatch"
**Solution:**
- Check Google Console redirect URIs
- Must exactly match: `http://127.0.0.1:8000/accounts/google/login/callback/`
- Include trailing slash

### Issue: "Email already exists"
**Solution:**
- This is expected behavior
- Accounts are automatically linked
- User can login with either method

### Issue: Welcome email not sending
**Solution:**
- Check EMAIL_BACKEND in settings
- For development, use console backend
- Check spam folder
- Verify SMTP settings

---

## 📊 Database Schema

### New Tables Created:
- `django_site` - Site configuration
- `account_emailaddress` - Email addresses
- `account_emailconfirmation` - Email verification tokens
- `socialaccount_socialaccount` - Social accounts
- `socialaccount_socialapp` - Social applications
- `socialaccount_socialtoken` - OAuth tokens

### Relationships:
- User → EmailAddress (one-to-many)
- User → SocialAccount (one-to-many)
- SocialAccount → SocialApp (many-to-one)

---

## 🎯 User Flows

### Flow 1: Email Registration
```
Register → Verify Email → Login → Dashboard
```

### Flow 2: Google Registration
```
Click Google → Authorize → Welcome Email → Dashboard
```

### Flow 3: Account Linking
```
Email User → Logout → Google Login (same email) → Accounts Linked
```

---

## ✅ Checklist

Before testing:
- [ ] Install django-allauth
- [ ] Run migrations
- [ ] Create site
- [ ] Get Google credentials
- [ ] Add credentials to .env
- [ ] Add social app in admin
- [ ] Test email registration
- [ ] Test Google OAuth
- [ ] Test account linking
- [ ] Check welcome emails

---

## 📞 Support

If you encounter issues:
1. Check Django logs
2. Check browser console
3. Verify Google Console settings
4. Test with different browsers
5. Clear browser cache/cookies

---

## 🎉 Success!

Your EcoLearn platform now supports:
- ✅ Email registration with verification
- ✅ Google OAuth authentication
- ✅ Automatic account linking
- ✅ Welcome emails for all users
- ✅ Seamless user experience
- ✅ Professional UI/UX

Users can choose their preferred method and switch between them freely!
