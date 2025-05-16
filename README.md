# 2025 Semester 1 CITS3403 Agile Web Development Project

| UWA Student Number | Student Name    | GitHub Username |
| ------------------ | --------------- | --------------- |
| 24270779           | Sarah Ann       | sxhann          |
| 23901817           | Angela Vu       | mypvu           |
| 23789621           | Kevin Tan       | phattydumpling  |
| 24149422           | Ilakkia Valavan | Ilakkia-Valavan |

# StudyNest - Study Tracker


## Application Overview

### Purpose
StudyNest is a comprehensive web application designed to support students in managing their academic and personal well-being. It combines study management tools for scheduling and task management, with health and wellness tracking in a single, integrated platform.

### Design & Functionality
The Study Tracker contains the following:

**1. Study Management**:
- Study Area: A dedicated space for students to organise and track their study sessions
- Assessment Tracking: Tools to manage and monitor academic assessments and deadlines
- Study Break Timer: Integrated timer system to encourage regular breaks during study sessions
- Study Break Ideas: Suggestions for productive breaks to maintain focus and well-being
  
**2. Health & Wellness**:
- Health Carer: A feature to set and track personal wellness goals
- Goal Setting: Customisable goal categories for physical, mental, and academic well-being
- Progress Tracking: Visual representation of goal completion and progress
- Wellness Monitoring: Tools to track various aspects of student health and well-being
  
**3. Social Features**:
- Friend System: Connect with other students
- Data Sharing: Share study and wellness data with friends
- Leaderboard: Competitive element to encourage engagement
- Notifications: System for friend requests and shared data
  
**4. Personal Dashboard**:
- Overview Cards: Quick access to key metrics and information
- Progress Visualisation: Charts and graphs showing study and wellness progress
- Customisable Interface: Personalisable dashboard layout
- Profile Management: User profile customisation with profile pictures


### Architecture
**Frontend(Client-Side)**:
- HTML for structure, with Tailwind CSS for styling and responsive design. JavaScript for client-side interactivity
- Flask Templates (jinja2): Allows dynamic interaction with the backend.
  
**Backend(Server-Side)**:
**Built using Python with Flask framework**
- Flask 3.1.0 as the web framework
- SQLAlchemy for database
- Flask-Login for user authentication
- Flask-WTF for form handling and CSRF protection
- Flask-Migrate for database migrations

**Database**:
- SQLite database (configurable for production)
- Database migrations managed through Alembic
  
**Security Features**:
- CSRF protection
- User authentication
- Secure password handling

# Getting Started

## Prerequisites
- Python 3.13
- pip 25.1.1
  
### Deployment/Launch
1. **Clone the Repository**: 
   ```bash
   git clone https://github.com/phattydumpling/CITS3403-Group-Project/
   cd CITS3403-Group-Project
   ```
2. **Set Up Virtual Environment**:
   ```bash
   # For macOS/Linux
   python -m venv venv
   source venv/bin/activate

   # For Windows
   python -m venv venv
   venv\Scripts\activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Set up environment variables**
   Create a `.env` file in the project root directory
   ```python
   import secrets
   print(secrets.token_hex(16))
   ```
   Replace with generate secret keys
   ```bash
   # Flask application secret key
   SECRET_KEY=your_generated_secret_key

   # CSRF protection secret key
   WTF_CSRF_SECRET_KEY=your_generated_csrf_secret_key
   ```
5. **Run the Application**:
   ```bash
   python app.py
   ```
6. **Access the Application**:
   Open a web browser and navigate to `http://127.0.0.1:5000`.


### Running Tests
- To run the tests for the application, execute the following command:
   ```bash
   python3 -m unittest tests/unit.py # For Unittests
   python3 -m unittest tests/selenium.py # For Selenium Tests
   ```
- Ensure that the application is running and the database is initialised before running tests to verify functionality.

### References
This project includes code and implementation generated with the assistance of GitHub Copilot, OpenAI's ChatGPT, Cursor and Stack Overflow.
