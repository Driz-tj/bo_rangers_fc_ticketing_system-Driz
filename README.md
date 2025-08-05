<<<<<<< HEAD
# Bo Rangers FC Digital Ticketing and Match Information System

A comprehensive web application built with Django for managing football club operations, including online ticket sales, match fixtures, club news, and administrative tools.

## 🏆 Features

### Fan Interface
- **User Registration & Authentication**: Secure user accounts with profile management
- **Match Fixtures**: View upcoming, live, and completed matches with filtering options
- **Online Ticket Booking**: Select matches, choose ticket categories, and complete purchases
- **Digital Tickets**: QR code generation for stadium entry
- **Mobile Money Integration**: Mock payment system supporting Orange Money and Africell Money
- **Club News**: Latest news, press releases, and match recaps with categorization
- **Responsive Design**: Mobile-friendly interface using Bootstrap 5

### Admin Interface
- **Dashboard Analytics**: Sales reports, revenue tracking, and attendance statistics
- **Match Management**: Add, edit, and update match information and status
- **News Management**: Create and publish news articles with image support
- **Ticket Sales Tracking**: Monitor ticket sales and generate reports
- **User Management**: View and manage registered users
- **Django Admin Integration**: Full administrative control through Django's admin interface

### Technical Features
- **QR Code Generation**: Automatic QR code creation for valid tickets
- **Real-time Updates**: Live match status updates
- **Data Visualization**: Charts and graphs for sales analytics using Chart.js
- **Email Integration**: Ready for email notifications (configured for development)
- **Security**: CSRF protection, secure authentication, and input validation
- **Database**: SQLite for easy deployment and development

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)

### Installation

1. **Extract the project files**:
   ```bash
   unzip bo_rangers_fc_ticketing_system.zip
   cd bo_rangers_fc_ticketing_system
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Populate sample data** (optional but recommended):
   ```bash
   python manage.py populate_data
   ```

6. **Create a superuser** (if not using sample data):
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server**:
   ```bash
   python manage.py runserver
   ```

8. **Access the application**:
   - Main website: http://localhost:8000/
   - Admin panel: http://localhost:8000/admin/

## 👥 Default Accounts

If you ran the `populate_data` command, the following accounts are available:

### Admin Account
- **Username**: admin
- **Password**: admin123
- **Role**: Administrator (full access)

### Sample Fan Accounts
- **Username**: john_fan, **Password**: password123
- **Username**: mary_supporter, **Password**: password123
- **Username**: david_rangers, **Password**: password123
- **Username**: sarah_fc, **Password**: password123

## 📱 Usage Guide

### For Fans

1. **Registration**: Create an account using the "Register" button
2. **Browse Fixtures**: View upcoming matches and match details
3. **Book Tickets**: 
   - Select a match from the fixtures page
   - Choose ticket category and quantity
   - Complete payment using mock mobile money
   - Download your digital ticket with QR code
4. **View Profile**: Access your booking history and account details
5. **Read News**: Stay updated with the latest club news and announcements

### For Administrators

1. **Access Admin Dashboard**: Login with admin credentials
2. **Manage Matches**: 
   - Add new matches through Django admin
   - Update match status (upcoming → live → completed)
   - View ticket sales per match
3. **Publish News**: Create and publish news articles with images
4. **Monitor Sales**: View detailed reports and analytics
5. **User Management**: Monitor registered users and their activities

## 🛠️ Technical Details

### Project Structure
```
bo_rangers_fc_ticketing_system/
├── borangersfc/                 # Django project settings
│   ├── settings.py             # Main configuration
│   ├── urls.py                 # URL routing
│   └── wsgi.py                 # WSGI configuration
├── ticketing/                   # Main application
│   ├── models.py               # Database models
│   ├── views.py                # View functions
│   ├── urls.py                 # App URL patterns
│   ├── forms.py                # Django forms
│   ├── admin.py                # Admin configuration
│   └── management/             # Custom management commands
├── templates/                   # HTML templates
│   ├── base.html               # Base template
│   ├── ticketing/              # App-specific templates
│   └── registration/           # Authentication templates
├── static/                      # Static files
│   ├── css/                    # Custom CSS
│   └── js/                     # Custom JavaScript
├── media/                       # User-uploaded files
├── requirements.txt             # Python dependencies
└── manage.py                   # Django management script
```

### Database Models
- **User**: Extended with UserProfile for additional fields
- **Match**: Match information and status
- **TicketCategory**: Different ticket types and pricing
- **Ticket**: Individual ticket bookings with QR codes
- **News**: Club news and announcements
- **Report**: Sales and attendance reports

### Key Dependencies
- **Django 5.2.4**: Web framework
- **qrcode**: QR code generation
- **Pillow**: Image processing
- **Bootstrap 5**: Frontend framework
- **Chart.js**: Data visualization

## 🔧 Configuration

### Settings
The application uses Django's default settings with the following customizations:
- SQLite database for easy deployment
- Static files configuration for CSS/JS
- Media files configuration for uploads
- Template directories setup

### Environment Variables
For production deployment, consider setting:
- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to False for production
- `ALLOWED_HOSTS`: Add your domain names

## 📊 Sample Data

The `populate_data` command creates:
- 7 matches (3 completed, 4 upcoming)
- 4 ticket categories (VIP, Regular, Student, Family)
- 5 news articles with different categories
- 4 sample fan accounts
- Sample ticket bookings and sales reports
- 1 admin account

## 🎨 Customization

### Styling
- Custom CSS in `static/css/custom.css`
- Bootstrap 5 classes used throughout
- Responsive design for mobile devices
- Custom color scheme using Bo Rangers FC branding

### Adding Features
- Models: Add new fields in `ticketing/models.py`
- Views: Create new views in `ticketing/views.py`
- Templates: Add HTML templates in `templates/ticketing/`
- URLs: Update URL patterns in `ticketing/urls.py`

## 🔒 Security Features

- CSRF protection on all forms
- User authentication and authorization
- Admin-only access to management features
- Input validation and sanitization
- Secure password handling

## 📱 Mobile Responsiveness

The application is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones
- Various screen sizes and orientations

## 🚀 Deployment

For production deployment:

1. Set `DEBUG = False` in settings.py
2. Configure `ALLOWED_HOSTS`
3. Set up a production database (PostgreSQL recommended)
4. Configure static file serving
5. Set up a production WSGI server (Gunicorn, uWSGI)
6. Configure a reverse proxy (Nginx, Apache)

## 🐛 Troubleshooting

### Common Issues

1. **Server won't start**:
   - Check if virtual environment is activated
   - Ensure all dependencies are installed
   - Run `python manage.py migrate`

2. **Static files not loading**:
   - Run `python manage.py collectstatic` for production
   - Check `STATIC_URL` and `STATICFILES_DIRS` settings

3. **QR codes not generating**:
   - Ensure Pillow is installed correctly
   - Check media directory permissions

4. **Admin access denied**:
   - Create superuser with `python manage.py createsuperuser`
   - Or use the default admin account (admin/admin123)

## 📞 Support

For technical support or questions:
- Check the Django documentation: https://docs.djangoproject.com/
- Review the code comments for implementation details
- Test with the provided sample data

## 📄 License

This project is created for educational and demonstration purposes. Feel free to modify and use as needed.

## 🏆 Credits

Developed for Bo Rangers FC - Sierra Leone's Premier Football Club
Built with Django, Bootstrap 5, and modern web technologies.

---

**Note**: This is a demonstration application with mock payment integration. For production use, integrate with real payment gateways and implement additional security measures.

=======
"# bo_rangers_fc_ticketing_system-Driz" 
"# bo_rangers_fc_ticketing_system-Driz" 
>>>>>>> a1811e08b1f0581a0a1fe3d30f5830855426dfef
