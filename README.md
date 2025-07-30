# AI Website Builder

A powerful web application that uses AI to generate professional websites automatically. Built with Flask, MongoDB, and Google's Gemini AI.

![AI Website Builder](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)
![MongoDB](https://img.shields.io/badge/MongoDB-Latest-green.svg)

## Features

- **AI-Powered Content Generation** - Uses Google Gemini AI to create professional website content
- **Role-Based Access Control** - Admin, Editor, and Viewer roles with different permissions
- **Real-time Website Preview** - Preview your websites before publishing
- **Multiple Business Types** - Support for restaurants, retail, consulting, and more
- **Responsive Templates** - Modern, mobile-friendly website templates
- **User Management** - Admin panel for managing users and roles
- **Website Management** - Create, edit, publish, and delete websites
- **Content Regeneration** - Re-generate AI content with a single click

## Quick Start

### Prerequisites

- Python 3.8 or higher
- MongoDB (local installation or MongoDB Atlas)
- Google Gemini API key (optional, fallback content provided)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai_website_builder
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.tx
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file with your configuration:
   ```env
   SECRET_KEY=your-secret-key-here
   MONGODB_URI=mongodb://localhost:27017/ai_website_builder
   JWT_SECRET_KEY=your-jwt-secret-key
   GEMINI_API_KEY=your-google-gemini-api-key
   ```

5. **Start MongoDB**
   
   **Local MongoDB:**
   ```bash
   mongod
   ```
   
   **Or use MongoDB Atlas** (cloud):
   - Create account at [MongoDB Atlas](https://www.mongodb.com/atlas)
   - Create cluster and get connection string
   - Update `MONGODB_URI` in `.env`

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Access the application**
   - Open browser and go to `http://localhost:5000`
   - Use default admin credentials: `admin@admin.com` / `admin123`

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SECRET_KEY` | Flask secret key for sessions | Yes | - |
| `MONGODB_URI` | MongoDB connection string | Yes | `mongodb://localhost:27017/ai_website_builder` |
| `JWT_SECRET_KEY` | JWT token signing key | Yes | - |
| `GEMINI_API_KEY` | Google Gemini API key | No | Falls back to default content |

### Getting Google Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file as `GEMINI_API_KEY`

*Note: The application works without Gemini API key using fallback content generation.*

## Default Users & Roles

### Default Admin Account
- **Email:** `admin@admin.com`
- **Password:** `admin123`
- **Role:** Admin (full access)

### Roles & Permissions

| Role | Create Websites | Edit Websites | Delete Websites | Admin Panel | View All |
|------|----------------|---------------|-----------------|-------------|----------|
| **Admin** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Editor** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Viewer** | ❌ | ❌ | ❌ | ❌ | ❌ |

## Project Structure

```
ai_website_builder/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── api/                     # API routes
│   │   ├── __init__.py
│   │   ├── admin.py             # Admin management
│   │   ├── ai_generator.py      # AI content generation
│   │   └── websites.py          # Website CRUD operations
│   ├── auth/                    # Authentication
│   │   ├── __init__.py
│   │   ├── routes.py            # Login/register routes
│   │   └── utils.py             # JWT utilities
│   ├── middleware/              # Custom middleware
│   │   ├── auth_middleware.py   # Authentication checks
│   │   └── permission_middleware.py # Role-based permissions
│   ├── models/                  # Database models
│   │   ├── role.py              # Role model
│   │   ├── user.py              # User model
│   │   └── website.py           # Website model
│   └── services/                # Business logic
│       ├── gemini_service.py    # AI content generation
│       └── template_service.py  # Template management
├── templates/                   # HTML templates
│   ├── base.html               # Base template
│   ├── dashboard.html          # Main dashboard
│   ├── login.html              # Login page
│   ├── register.html           # Registration page
│   ├── create_website.html     # Website creation
│   ├── my_websites.html        # Website management
│   └── admin.html              # Admin panel
├── app.py                      # Application entry point
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration

### Websites
- `GET /api/websites` - Get user's websites
- `GET /api/websites/<id>` - Get specific website
- `PUT /api/websites/<id>` - Update website
- `DELETE /api/websites/<id>` - Delete website
- `POST /api/generate-website` - Generate new website with AI
- `POST /api/regenerate-content/<id>` - Regenerate website content

### Admin (Admin role required)
- `GET /api/admin/users` - Get all users
- `PUT /api/admin/users/<id>/role` - Update user role
- `DELETE /api/admin/users/<id>` - Delete user
- `GET /api/admin/roles` - Get all roles
- `POST /api/admin/roles` - Create new role
- `GET /api/admin/dashboard` - Get admin statistics

### Public
- `GET /api/preview/<website_id>` - Preview published website
- `GET /health` - Health check

## Usage Guide

### Creating Your First Website

1. **Login** with admin credentials or register new account
2. **Go to Dashboard** and click "Create New Website"
3. **Fill in details:**
   - Company/Business name
   - Business type (restaurant, retail, etc.)
   - Industry category
   - Optional description
4. **Click "Generate My Website"** - AI will create content
5. **Manage your website** from "My Websites" page
6. **Publish** when ready to make it live
7. **Preview** your published website

### Managing Users (Admin Only)

1. **Go to Admin Panel** from dashboard
2. **Users tab** - View all registered users
3. **Edit roles** - Change user permissions
4. **Create roles** - Define custom roles with specific permissions
5. **View statistics** - Monitor system usage

## Troubleshooting

### Common Issues

**1. MongoDB Connection Error**
```bash
# Check if MongoDB is running
mongod --version

# Start MongoDB service
sudo systemctl start mongod  # Linux
brew services start mongodb  # macOS
```

**2. Module Import Errors**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

**3. AI Content Generation Not Working**
- Check if `GEMINI_API_KEY` is set in `.env`
- Verify API key is valid at Google AI Studio
- Application will use fallback content if API fails

**4. Permission Denied Errors**
- Ensure you're logged in with appropriate role
- Admin role required for user management
- Editor role required for website creation

**5. Website Not Updating**
- Clear browser cache and reload
- Check browser console for JavaScript errors
- Verify API endpoints are accessible

### Debug Mode

Enable debug mode for detailed error messages:

```python
# In app.py, change:
app.run(debug=True, host='0.0.0.0', port=5000)
```
