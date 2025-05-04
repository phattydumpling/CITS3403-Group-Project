# 2025 Semester 1 CITS3403 Agile Web Development Project

| UWA Student Number | Student Name    | GitHub Username |
| ------------------ | --------------- | --------------- |
| 24270779           | Sarah Ann       | sxhann          |
| 23901817           | Angela Vu       | mypvu           |
| 23789621           | Kevin Tan       | phattydumpling  |
| 24149422           | Ilakkia Valavan | Ilakkia-Valavan |

# App Name
**Smart Study Scheduler**

## Application Overview

### Purpose
- The Smart Study Scheduler is designed to help students manage their study sessions, track their academic progress, and maintain their mental and physical well-being. 
- It provides tools for scheduling, task management, and health reminders, creating a holistic approach to student life.

### Design & Functionality
- **User  Interface**: The application features a clean and intuitive interface with light and dark mode options to enhance user experience.
- **Dashboard**: Users can view key insights, including study hours, task completion rates, and health scores through interactive graphs.
- **Study Area**: Users can log individual and group study sessions, track performance, and receive recommendations based on their study habits.
- **Health Carer**: The app includes reminders for hydration, breaks, and physical activity, along with mental health resources.
- **Data Sharing**: Users can share their study habits and achievements with peers, fostering a sense of community and competition.

### Architecture
- **Frontend**: Built using HTML, CSS (Tailwind), and JavaScript, ensuring a responsive and user-friendly design.
- **Backend**: Developed with Flask, utilising SQLAlchemy for database interactions and Flask-WTF for form handling.
- **Database**: SQLite is used to store user data, study sessions, tasks, and wellness checks, allowing for efficient data management.
- **APIs**: Integration with calendar APIs for scheduling and reminders, and potential weather APIs for outdoor activity suggestions.

## Getting Started

### Deployment/Launch
1. **Clone the Repository**: 
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```
2. **Set Up Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Initialise the Database**:
   ```bash
   python create_db.py
   ```
5. **Run the Application**:
   ```bash
   python app.py
   ```
6. **Access the Application**: Open a web browser and navigate to `http://127.0.0.1:5000`.

### How to Use on Mac
- Follow the same steps as outlined above for deployment and launch.
- Ensure that you have Python installed on your Mac. You can check this by running:
   ```bash
   python3 --version
   ```
- If Python is not installed, you can download it from the [official Python website](https://www.python.org/downloads/).
- Use `python3` instead of `python` in the commands if your system defaults to Python 2.x.

### Running Tests
- To run the tests for the application, execute the following command:
   ```bash
   python test_db.py
   ```
- Ensure that the application is running and the database is initialised before running tests to verify functionality.

