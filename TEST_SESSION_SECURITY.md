# 🧪 Test Session Security - Quick Guide

## Quick Test (5 Minutes)

### 1. Test Session Timeout (Fast Method)

**Temporarily reduce session timeout for testing:**

Edit `ecolearn/settings.py`:
```python
SESSION_COOKIE_AGE = 60  # Change from 3600 to 60 (1 minute for testing)
```

**Test Steps:**
1. Login: `http://localhost:8000/accounts/login/`
2. Go to dashboard: `http://localhost:8000/dashboard/`
3. Wait 1 minute (do nothing)
4. Try to access any page: `http://localhost:8000/elearning/modules/`
5. **Expected:** Redirected to login page
6. Login again
7. **Expected:** Redirected back to modules page

**Don't forget to change it back to 3600 after testing!**

---

### 2. Test Authentication Protection

**Logout first:**
- Click logout or go to: `http://localhost:8000/accounts/logout/`

**Try to access these URLs (should redirect to login):**

```bash
# E-Learning (should require login)
http://localhost:8000/elearning/modules/
http://localhost:8000/dashboard/

# Community (should require login)
http://localhost:8000/community/forum/
http://localhost:8000/community/events/
http://localhost:8000/community/challenges/

# Reporting (should require login)
http://localhost:8000/reporting/report/
http://localhost:8000/reporting/my-reports/

# Admin (should require staff login)
http://localhost:8000/admin-dashboard/
```

**Expected Result:** All redirect to `/accounts/login/?next=/original-url/`

---

### 3. Test Public Pages (Should Work Without Login)

**These should work WITHOUT login:**

```bash
# Public pages
http://localhost:8000/                    # Landing page ✅
http://localhost:8000/about/              # About ✅
http://localhost:8000/features/           # Features ✅
http://localhost:8000/contact/            # Contact ✅
http://localhost:8000/accounts/login/     # Login page ✅
http://localhost:8000/accounts/register/  # Register page ✅
```

**Expected Result:** All pages load without requiring login

---

### 4. Test Session Refresh

**Test that sessions stay alive with activity:**

1. Login
2. Browse pages continuously (click around every 30 seconds)
3. Keep doing this for 2+ minutes (longer than your test timeout)
4. **Expected:** Session stays alive because you're active

---

## Full Test Script

Run this in your browser console after logging in:

```javascript
// Test session status
fetch('/accounts/session/status/')
  .then(r => r.json())
  .then(data => console.log('Session Status:', data));

// Test session keep-alive
fetch('/accounts/session/keep-alive/')
  .then(r => r.json())
  .then(data => console.log('Keep Alive:', data));
```

---

## Expected Behaviors

### ✅ Correct Behavior:

1. **Active user:** Session never expires (resets on each page)
2. **Inactive user:** Session expires after 1 hour
3. **Expired session:** Redirects to login with `?next=` parameter
4. **After login:** Returns to intended page
5. **Logout:** Redirects to landing page `/`
6. **Browser close:** Session destroyed
7. **Protected pages:** Require login
8. **Public pages:** Work without login

### ❌ Incorrect Behavior (Report if you see this):

1. Session expires while user is active
2. No redirect to login on expired session
3. Public pages require login
4. Protected pages accessible without login
5. Login doesn't redirect back to intended page

---

## Quick Commands

### Start Django Server:
```bash
python manage.py runserver
```

### Check Current Session Settings:
```bash
python manage.py shell
```
```python
from django.conf import settings
print(f"Session Age: {settings.SESSION_COOKIE_AGE} seconds")
print(f"Save Every Request: {settings.SESSION_SAVE_EVERY_REQUEST}")
print(f"Expire at Browser Close: {settings.SESSION_EXPIRE_AT_BROWSER_CLOSE}")
```

### Clear All Sessions (if needed):
```bash
python manage.py clearsessions
```

---

## Troubleshooting

### Session not expiring?
- Check `SESSION_SAVE_EVERY_REQUEST = True` in settings
- Clear browser cookies
- Try incognito/private window

### Redirecting to wrong page?
- Check `LOGIN_URL = '/accounts/login/'` in settings
- Check `LOGOUT_REDIRECT_URL = '/'` in settings

### Public pages requiring login?
- Check that landing_page_view, login_view, register_view don't have @login_required
- Check URL patterns in ecolearn/urls.py

---

## Production Checklist

Before deploying to production:

- [ ] Change `SESSION_COOKIE_AGE` back to 3600 (1 hour) or higher
- [ ] Set `SESSION_COOKIE_SECURE = True` (requires HTTPS)
- [ ] Set `CSRF_COOKIE_SECURE = True` (requires HTTPS)
- [ ] Test all protected pages require login
- [ ] Test all public pages work without login
- [ ] Test session timeout behavior
- [ ] Test login redirect behavior
- [ ] Test logout redirect behavior

---

## 🎉 All Tests Passing?

If all tests pass, your session security is working correctly!

Your system now:
✅ Expires sessions after 1 hour of inactivity
✅ Keeps sessions alive while user is active
✅ Redirects to login on session expiry
✅ Returns to intended page after login
✅ Protects all authenticated pages
✅ Allows public access to landing/info pages
