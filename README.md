# EcoLearn - Environmental Education Platform

EcoLearn is a comprehensive environmental education platform designed for Zambia, featuring multilingual support (English, Bemba, Nyanja), mobile money integration, and community engagement tools.

## Features

### 🎓 Interactive E-Learning
- Multilingual courses on waste management, recycling, and sustainability
- Video tutorials, quizzes, and hands-on activities
- Progress tracking and completion certificates
- Points-based reward system

### 👥 Community Engagement
- Discussion forums for sharing best practices
- Community events and cleanup campaigns
- Success story sharing with social media integration
- WhatsApp and Facebook integration for notifications

### 📍 Illegal Dumping Reporting
- Anonymous reporting with photo uploads
- GPS location tagging
- Automatic forwarding to local authorities (Lusaka City Council)
- Real-time status tracking

### 💳 Mobile Money Integration
- MTN Mobile Money support
- Airtel Money integration
- Zamtel Kwacha payments
- Premium subscriptions and donations

### 🌍 Multilingual Support
- Full content available in English, Bemba, and Nyanja
- Language-specific user interfaces
- Culturally appropriate content

## Technology Stack

- **Backend**: Django 4.2+ with Python
- **Frontend**: HTML5, Tailwind CSS, JavaScript, Alpine.js
- **Database**: SQLite (development), PostgreSQL (production)
- **APIs**: REST Framework, Mobile Money APIs
- **Maps**: Leaflet.js for location services
- **SMS**: Twilio integration

## Quick Start

### Automated Setup (Recommended)

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd ecolearn_project
   python setup.py
   ```

The setup script will automatically:
- Create virtual environment
- Install all dependencies
- Set up database with migrations
- Create default admin user (admin/admin123)
- Generate sample data for testing

### Manual Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ecolearn_project
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**
   ```bash
   copy .env.example .env  # Windows
   cp .env.example .env    # Linux/Mac
   # Edit .env with your configuration
   ```

5. **Database setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Load sample data (optional)**
   ```bash
   python manage.py shell
   >>> exec(open('setup.py').read())
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Main site: http://127.0.0.1:8000
   - Admin panel: http://127.0.0.1:8000/admin
   - Default admin: username=`admin`, password=`admin123`

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure the following:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite for development)
DATABASE_URL=sqlite:///db.sqlite3

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=EcoLearn <noreply@ecolearn.zm>

# Twilio SMS Configuration
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# Mobile Money API Keys
MTN_API_KEY=your-mtn-api-key
MTN_API_SECRET=your-mtn-api-secret
MTN_SUBSCRIPTION_KEY=your-mtn-subscription-key

AIRTEL_API_KEY=your-airtel-api-key
AIRTEL_API_SECRET=your-airtel-api-secret
AIRTEL_CLIENT_ID=your-airtel-client-id

ZAMTEL_API_KEY=your-zamtel-api-key
ZAMTEL_API_SECRET=your-zamtel-api-secret
ZAMTEL_MERCHANT_ID=your-zamtel-merchant-id

# Security Settings
CSRF_COOKIE_SECURE=False  # Set to True in production
SESSION_COOKIE_SECURE=False  # Set to True in production
SECURE_SSL_REDIRECT=False  # Set to True in production
```

### Required API Registrations

**For SMS functionality:**
1. Create a [Twilio account](https://www.twilio.com/)
2. Get your Account SID, Auth Token, and phone number
3. Add credits for SMS sending

**For email functionality:**
1. Enable 2-factor authentication on Gmail
2. Generate an app-specific password
3. Use the app password in EMAIL_HOST_PASSWORD

### Mobile Money Setup

**Important:** Mobile money integration requires business partnerships with providers. For development/testing, the system includes mock implementations.

1. **MTN Mobile Money**
   - Apply for MTN MoMo API access through [MTN Developer Portal](https://momodeveloper.mtn.com/)
   - Complete KYC and business verification
   - Configure sandbox environment for testing
   - Set up webhook URLs for payment confirmations
   - Production requires signed agreements

2. **Airtel Money**
   - Contact Airtel Business for API access
   - Complete merchant onboarding process
   - Configure test environment credentials
   - Set up callback URLs for transaction status
   - Production requires business partnership

3. **Zamtel Kwacha**
   - Register through Zamtel Business Services
   - Complete merchant verification
   - Configure API endpoints and credentials
   - Set up notification webhooks

**Development Mode:**
The system includes mock payment processors for testing without real API credentials. Set `DEBUG=True` to use mock implementations.

## Project Structure

```
ecolearn_project/
├── accounts/           # User authentication and profiles
├── elearning/          # Learning modules and courses
├── community/          # Forums, events, and social features
├── reporting/          # Illegal dumping reports
├── payments/           # Mobile money integration
├── templates/          # HTML templates
├── static/            # CSS, JS, images
├── media/             # User uploads
├── ecolearn/          # Main project settings
└── manage.py          # Django management script
```

## Usage

### Admin Panel
Access the admin panel at `/admin/` to:
- Manage users and profiles
- Create learning modules and categories
- Monitor dumping reports
- Configure payment plans
- View analytics and statistics

### User Features
- **Registration**: Users can register with email or phone number
- **Learning**: Browse and complete environmental education modules
- **Community**: Participate in forums and events
- **Reporting**: Report illegal dumping sites with photos and GPS
- **Payments**: Subscribe to premium features using mobile money

## API Endpoints

### Authentication
- `POST /accounts/register/` - User registration
- `POST /accounts/login/` - User login
- `POST /accounts/verify/` - SMS verification

### Learning
- `GET /learning/` - List modules
- `GET /learning/module/{id}/` - Module details
- `POST /learning/lesson/{id}/complete/` - Mark lesson complete

### Reporting
- `POST /reporting/report/` - Submit dumping report
- `GET /reporting/track/` - Track report status
- `GET /reporting/map/` - Get reports for map

### Payments
- `GET /payments/plans/` - List payment plans
- `POST /payments/pay/{plan_id}/` - Initiate payment
- `POST /payments/webhook/{provider}/` - Payment webhooks

## Mobile Money Integration

### Payment Flow
1. User selects a payment plan
2. Enters mobile number and provider
3. System initiates payment request
4. User receives SMS prompt on phone
5. User approves payment with PIN
6. System receives webhook confirmation
7. Subscription is activated

### Supported Providers
- **MTN Mobile Money**: Full integration with API
- **Airtel Money**: Complete payment processing
- **Zamtel Kwacha**: Basic payment support

## Deployment

### Production Checklist

1. **Environment Configuration**
   ```env
   DEBUG=False
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   SECRET_KEY=generate-new-secret-key
   ```

2. **Database Setup**
   ```env
   # PostgreSQL (recommended)
   DATABASE_URL=postgresql://user:password@localhost:5432/ecolearn
   
   # Or MySQL
   DATABASE_URL=mysql://user:password@localhost:3306/ecolearn
   ```

3. **Security Settings**
   ```env
   CSRF_COOKIE_SECURE=True
   SESSION_COOKIE_SECURE=True
   SECURE_SSL_REDIRECT=True
   SECURE_HSTS_SECONDS=31536000
   ```

4. **Static Files**
   - WhiteNoise is pre-configured for static file serving
   - Run: `python manage.py collectstatic`
   - Configure CDN for media files (optional)

5. **SSL Certificate**
   - Install SSL certificate (Let's Encrypt recommended)
   - Configure web server (Nginx/Apache)
   - Update ALLOWED_HOSTS with your domain

6. **Production APIs**
   - Replace sandbox API keys with production keys
   - Configure production webhook URLs
   - Test payment flows thoroughly

### Deployment Platforms

**Heroku:**
```bash
# Install Heroku CLI
pip install gunicorn
echo "web: gunicorn ecolearn.wsgi" > Procfile
heroku create your-app-name
heroku config:set DEBUG=False
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
```

**DigitalOcean/VPS:**
```bash
# Install dependencies
sudo apt update
sudo apt install python3-pip python3-venv nginx postgresql

# Setup application
git clone <repository>
cd ecolearn_project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Configure database
sudo -u postgres createdb ecolearn
python manage.py migrate
python manage.py collectstatic

# Setup systemd service
sudo nano /etc/systemd/system/ecolearn.service
sudo systemctl enable ecolearn
sudo systemctl start ecolearn

# Configure Nginx
sudo nano /etc/nginx/sites-available/ecolearn
sudo ln -s /etc/nginx/sites-available/ecolearn /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

### Common Issues

**1. SMS not sending:**
- Check Twilio credentials in .env
- Verify phone number format (+260...)
- Ensure Twilio account has credits

**2. Payment integration errors:**
- Verify API keys are correct
- Check webhook URLs are accessible
- Test with sandbox/development APIs first

**3. Database migration errors:**
- Delete migration files and recreate: `find . -path "*/migrations/*.py" -not -name "__init__.py" -delete`
- Run: `python manage.py makemigrations` then `python manage.py migrate`

**4. Static files not loading:**
- Run: `python manage.py collectstatic`
- Check STATIC_ROOT and STATIC_URL settings
- Verify WhiteNoise is in MIDDLEWARE

**5. Permission errors:**
- Ensure proper file permissions: `chmod -R 755 media/`
- Check directory ownership

### Getting Help

- **Documentation:** Check inline code comments and docstrings
- **Logs:** Check Django debug output and server logs
- **Community:** Django and Python community forums
- **Issues:** Create GitHub issues for bugs and feature requests

### Performance Optimization

**Database:**
- Add database indexes for frequently queried fields
- Use select_related() and prefetch_related() for queries
- Consider database connection pooling

**Caching:**
- Enable Django's cache framework
- Cache expensive database queries
- Use Redis or Memcached for session storage

**Static Files:**
- Configure CDN for static and media files
- Enable gzip compression
- Optimize images and assets

## Acknowledgments

- Zambian Ministry of Environment
- Lusaka City Council
- Environmental education partners
- Mobile money providers (MTN, Airtel, Zamtel)

---

## Development Roadmap

### Phase 1 (Current)
- ✅ Core platform functionality
- ✅ User authentication and profiles
- ✅ E-learning modules with multilingual support
- ✅ Community forums and events
- ✅ Illegal dumping reporting system
- ✅ Mobile money payment integration
- ✅ Admin dashboard and content management

### Phase 2 (Planned)
- 📱 Mobile app (React Native/Flutter)
- 🔔 Push notifications and SMS alerts
- 📊 Advanced analytics and reporting
- 🎮 Gamification features (badges, leaderboards)
- 🤖 AI-powered content recommendations
- 🌐 Multi-tenant support for other regions

### Phase 3 (Future)
- 🛰️ Satellite imagery integration for monitoring
- 🔗 Blockchain-based reward system
- 📈 Carbon footprint tracking
- 🤝 Partnership integrations (NGOs, government)
- 📚 Offline content synchronization
- 🎯 Personalized learning paths

---

**Built with ❤️ for environmental sustainability in Zambia 🇿🇲**

*"Education is the most powerful weapon which you can use to change the world."* - Nelson Mandela
