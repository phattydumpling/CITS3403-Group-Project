from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def base():
    return render_template('base.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/study_session')
def study_session():
    return render_template('study_session.html')

@app.route('/task_overview')
def task_overview():
    return render_template('task_overview.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/lecture_log')
def lecture_log():
    return render_template('lecture_log.html')

@app.route('/assessments')
def assessments():
    return render_template('assessments.html')

@app.route('/resources')
def resources():
    return render_template('resources.html')

@app.route('/health_carer')
def health_carer():
    return render_template('health_carer.html')

@app.route('/mental_health')
def mental_health():
    return render_template('mental_health.html')

@app.route('/wellness_check')
def wellness_check():
    return render_template('wellness_check.html')

@app.route('/study_break')
def study_break():
    return render_template('study_break.html')

@app.route('/study_tips')
def study_tips():
    return render_template('study_tips.html')

@app.route('/share_data')
def share_data():
    return render_template('share_data.html')

@app.route('/study_area')
def study_area():
    return render_template('study_area.html')

if __name__ == '__main__':
    app.run(debug=True)