# Admin Dashboard USER_ROLES AttributeError - FIXED

## Issue
The admin dashboard was throwing an AttributeError:
```
type object 'CustomUser' has no attribute 'USER_ROLES'
```

## Root Cause
The admin dashboard views were trying to access `CustomUser.USER_ROLES` but the model actually defines `CustomUser.ROLE_CHOICES`.

## Fix Applied
Updated two locations in `admin_dashboard/views.py`:

1. **Line 208** (user_management view):
   ```python
   # Before
   'role_choices': CustomUser.USER_ROLES,
   
   # After  
   'role_choices': CustomUser.ROLE_CHOICES,
   ```

2. **Line 2078** (notification_create view):
   ```python
   # Before
   'role_choices': CustomUser.USER_ROLES,
   
   # After
   'role_choices': CustomUser.ROLE_CHOICES,
   ```

## Verification
- ✅ `CustomUser.ROLE_CHOICES` returns: `[('user', 'User'), ('admin', 'Admin')]`
- ✅ Admin dashboard should now load without AttributeError
- ✅ User management page should work: `http://127.0.0.1:8000/admin-dashboard/users/`

## Status
**FIXED** - The admin dashboard should now work properly without the AttributeError.