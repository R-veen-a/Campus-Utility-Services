# Campus Management System

A comprehensive Flask-based campus management system with role-based authentication and interactive features for students, faculty, admin, chef, and bus coordinator.

## Features

### 🎯 Core Features
- **Role-based Authentication**: Secure login system for different user types
- **Interactive Dashboards**: Customized dashboards for each role
- **Real-time Notifications**: Instant alerts and updates
- **Responsive Design**: Modern UI with Bootstrap and custom CSS

### 👥 Role-Specific Features

#### Students
- Book rooms and view availability
- Report issues and maintenance requests
- View teacher availability
- Check bus schedules
- View canteen menus
- Receive notifications
- Check library status
- View washroom status

#### Faculty
- Manage teacher availability
- Book rooms for classes
- Report issues
- View notifications
- Check bus schedules
- Monitor classroom status
- Send system alerts

#### Admin
- Manage all users
- View and resolve issues
- Manage room bookings
- System-wide notifications
- Complete system oversight
- Monitor campus statistics

#### Chef
- Manage canteen menus
- View inventory status
- Monitor kitchen equipment
- Track food safety
- View popular items
- Manage daily operations

#### Bus Coordinator
- Manage bus routes
- View bus status and tracking
- Monitor canteen camera feed
- Handle bus-related issues
- Send bus alerts
- Update schedules

### 🏗️ System Features

#### AI & Smart Features
- **AI Voice Alerts**: Maintain silence in library
- **Camera Access**: Monitor classroom occupancy
- **Person Detection**: Check library and canteen availability
- **System Monitoring**: Detect computers left on and send notifications

#### Room Management
- **Smart Booking**: Real-time availability checking
- **Conflict Detection**: Prevent double bookings
- **Room Status**: Track room usage and maintenance

#### Issue Reporting
- **Multi-category Issues**: Washroom, water, food, classroom, bus, electrical, etc.
- **Priority Levels**: Low, medium, high, urgent
- **Status Tracking**: Open, in progress, resolved, closed
- **Location-based**: Specific location reporting

#### Transportation
- **Bus Routes**: Manage multiple routes
- **Real-time Tracking**: Live bus status
- **Schedule Management**: Departure times and destinations
- **Passenger Monitoring**: Occupancy tracking

#### Canteen Management
- **Daily Menus**: Day-wise menu planning
- **Inventory Tracking**: Stock monitoring
- **Food Safety**: Temperature and hygiene monitoring
- **Popular Items**: Track most ordered items

#### Washroom Management
- **Status Tracking**: Clean, unclean, maintenance, occupied
- **Location-based**: Multiple washroom locations
- **Real-time Updates**: Live status updates

## 🚀 Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Step-by-Step Setup

1. **Clone or Download the Project**
   ```bash
   # If using git
   git clone <repository-url>
   cd campus-management-system
   
   # Or download and extract the ZIP file
   ```

2. **Create Virtual Environment (Recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```bash
   python app.py
   ```

5. **Access the Application**
   - Open your web browser
   - Go to: `http://localhost:5000`
   - The application will start with sample data

## 👤 Demo Accounts

Use these credentials to test different roles:

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Student | student1 | student123 |
| Faculty | faculty1 | faculty123 |
| Chef | chef1 | chef123 |
| Bus Coordinator | buscoord1 | bus123 |

## 📁 Project Structure

```
campus-management-system/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── campus.db             # SQLite database (created automatically)
├── templates/            # HTML templates
│   ├── base.html         # Base template with navigation
│   ├── index.html        # Landing page
│   ├── admin_dashboard.html
│   ├── student_dashboard.html
│   ├── faculty_dashboard.html
│   ├── chef_dashboard.html
│   ├── buscoordinator_dashboard.html
│   ├── book_room.html
│   ├── report_issue.html
│   ├── teacher_availability.html
│   ├── canteen_menu.html
│   ├── bus_routes.html
│   └── washroom_status.html
└── static/              # Static files (CSS, JS, images)
```

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite3
- **Frontend**: HTML5, CSS3, JavaScript
- **UI Framework**: Bootstrap 5
- **Icons**: Font Awesome
- **Authentication**: Werkzeug (password hashing)

## 🔧 Configuration

### Database
- The application uses SQLite3 database (`campus.db`)
- Database is automatically created with sample data on first run
- No additional configuration required

### Security
- Passwords are hashed using Werkzeug's `generate_password_hash`
- Session-based authentication
- Role-based access control

## 📱 Features by Role

### Students
- ✅ View available rooms
- ✅ Book rooms with conflict detection
- ✅ Report issues (washroom, water, food, etc.)
- ✅ View teacher availability
- ✅ Check bus schedules
- ✅ View canteen menus
- ✅ Check library status
- ✅ View washroom status
- ✅ Receive notifications

### Faculty
- ✅ Set teacher availability
- ✅ Book rooms for classes
- ✅ Report issues
- ✅ View notifications
- ✅ Check bus schedules
- ✅ Monitor classroom status
- ✅ Send system alerts

### Admin
- ✅ Manage all users
- ✅ View and resolve all issues
- ✅ Monitor room bookings
- ✅ System-wide notifications
- ✅ Complete system oversight
- ✅ View campus statistics

### Chef
- ✅ Manage canteen menus
- ✅ View inventory status
- ✅ Monitor kitchen equipment
- ✅ Track food safety
- ✅ View popular items
- ✅ Manage daily operations

### Bus Coordinator
- ✅ Manage bus routes
- ✅ View bus status and tracking
- ✅ Monitor canteen camera feed
- ✅ Handle bus-related issues
- ✅ Send bus alerts
- ✅ Update schedules

## 🎨 UI/UX Features

- **Modern Design**: Clean and professional interface
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Interactive Elements**: Hover effects, animations, modals
- **Color-coded Status**: Visual indicators for different states
- **Real-time Updates**: Live status updates and notifications
- **User-friendly Navigation**: Intuitive menu structure

## 🔒 Security Features

- **Password Hashing**: Secure password storage
- **Session Management**: Secure user sessions
- **Role-based Access**: Restricted access based on user role
- **Input Validation**: Form validation and sanitization
- **SQL Injection Protection**: Parameterized queries

## 🚀 Future Enhancements

- [ ] Email notifications
- [ ] Mobile app development
- [ ] Advanced analytics dashboard
- [ ] Integration with external systems
- [ ] Real-time chat functionality
- [ ] Advanced reporting features
- [ ] API endpoints for external access
- [ ] Multi-language support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

For support or questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 🎯 Quick Start

1. Install Python 3.7+
2. Download the project files
3. Run `pip install -r requirements.txt`
4. Run `python app.py`
5. Open `http://localhost:5000`
6. Login with demo credentials

---

**Happy Campus Management! 🎓** 