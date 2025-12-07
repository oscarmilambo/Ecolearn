# 🚀 Start EcoLearn with MySQL Database

## Your Situation
- ✅ All your accounts (including admin) are in MySQL database
- ✅ MySQL80 service is installed but stopped
- ✅ XAMPP is installed on your system
- ✅ Settings updated to use MySQL when available

## Quick Start (3 Steps)

### Step 1: Start MySQL Server

**Option A - XAMPP Control Panel (Easiest):**
1. Press Windows key
2. Type "XAMPP"
3. Open "XAMPP Control Panel"
4. Click "Start" button next to MySQL
5. Wait for it to show "Running" in green

**Option B - Run the batch file:**
```bash
start_mysql.bat
```

**Option C - Windows Services (Requires Admin):**
1. Press Windows + R
2. Type: `services.msc`
3. Find "MySQL80"
4. Right-click → Start

### Step 2: Verify MySQL is Running

Open a new terminal and run:
```bash
mysql -u root -pbadman2001 -e "SHOW DATABASES;"
```

You should see your `marabo` database listed.

### Step 3: Start Django Server

```bash
python manage.py runserver
```

## ✅ What's Been Updated

Your `.env` file now has:
```env
USE_MYSQL=True
DB_ENGINE=django.db.backends.mysql
DB_NAME=marabo
DB_USER=root
DB_PASSWORD=badman2001
DB_HOST=localhost
DB_PORT=3306
```

Your `settings.py` will automatically:
- Use MySQL when `USE_MYSQL=True` and MySQL is running
- Fall back to SQLite if MySQL is not available

## 🔐 Login with Your Existing Account

Once MySQL is running and Django server starts:

1. **Go to:** http://127.0.0.1:8000/accounts/login/
2. **Use your existing credentials:**
   - Username: (your admin username)
   - Password: (your admin password)
3. **Access AI Assistant:** http://127.0.0.1:8000/ai-assistant/

## 🐛 Troubleshooting

### "Can't connect to MySQL server"
- Make sure MySQL is running in XAMPP Control Panel
- Check if port 3306 is not blocked by firewall
- Verify MySQL service shows "Running" status

### "Access denied for user 'root'"
- Check password in .env matches your MySQL root password
- Current password in .env: `badman2001`

### "Unknown database 'marabo'"
- Your database might have a different name
- Check with: `mysql -u root -pbadman2001 -e "SHOW DATABASES;"`
- Update `DB_NAME` in .env if needed

### MySQL won't start in XAMPP
- Check if port 3306 is already in use
- Try stopping other MySQL services
- Check XAMPP error logs at: `C:\xampp\mysql\data\mysql_error.log`

## 📊 Database Status Check

Run this to check your database:
```bash
python manage.py dbshell
```

Then in MySQL prompt:
```sql
SHOW TABLES;
SELECT username, email, is_staff FROM accounts_customuser;
EXIT;
```

## 🔄 Switching Between Databases

### Use MySQL (your accounts):
```env
USE_MYSQL=True
```

### Use SQLite (fresh start):
```env
USE_MYSQL=False
```

Then restart Django server.

## ⚡ Quick Commands

### Start Everything:
```bash
# Terminal 1: Start MySQL via XAMPP Control Panel
# Terminal 2:
python manage.py runserver
```

### Check MySQL Status:
```bash
mysql -u root -pbadman2001 -e "SELECT 1;"
```

### View Your Admin Account:
```bash
python manage.py shell
```
```python
from accounts.models import CustomUser
admin = CustomUser.objects.filter(is_staff=True).first()
print(f"Admin: {admin.username} - {admin.email}")
```

---

## 🎯 Next Steps After MySQL Starts

1. ✅ Start MySQL (XAMPP Control Panel)
2. ✅ Run: `python manage.py runserver`
3. ✅ Login with your existing admin account
4. ✅ Test AI Assistant at /ai-assistant/
5. ⚠️ Add Gemini API key to .env for AI responses

**Your accounts are safe in MySQL - just need to start the server!**