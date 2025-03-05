from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

app = Flask(__name__)
CORS(app)
Secret_key = "neha123@444"
app.secret_key = os.getenv("SECRET_KEY", Secret_key)  # Use environment variables for security

# Database Configuration (SQLite)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///healthcareData.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Google Sheets Authentication
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Admin Credentials
ADMIN_CREDENTIALS = {"username": "admin", "password": "admin123"}

# Database Model for Storing User Health Data
class HealthData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer, nullable=False)
    activity_level = db.Column(db.String(50), nullable=False)
    menstrual_cycle = db.Column(db.String(50), nullable=False)
    medical_conditions = db.Column(db.String(255), nullable=True)
    stress_level = db.Column(db.String(50), nullable=False)
    home_cooked_meals = db.Column(db.String(50), nullable=False)
    healthcare_access = db.Column(db.String(50), nullable=False)
    healthcare_challenges = db.Column(db.Text, nullable=True)
    comments = db.Column(db.Text, nullable=True)
    recommendation = db.Column(db.Text, nullable=True)  # Store recommendations

# Function to Generate Health Recommendations
def generate_recommendation(age, activity_level, menstrual_cycle, medical_conditions, stress_level, home_cooked_meals, healthcare_access, healthcare_challenges):
    recs = []
    print(age, activity_level,medical_conditions, stress_level, home_cooked_meals,healthcare_access ,healthcare_challenges)
    # ✅ Age-based Recommendations
    if age < 18:
        recs.append("Consult a pediatrician for specialized healthcare and growth monitoring.")
    elif 18 <= age <= 30:
        recs.append("Maintain a balanced diet, exercise regularly, and stay hydrated.")
    elif 30 < age <= 40:
        recs.append("Monitor vitamin and mineral intake, and schedule routine medical checkups.")
    elif age > 40:
        recs.append("Consider regular screenings for heart health, bone density, and metabolic conditions.")

    # ✅ Activity Level Recommendations
    if activity_level == "Sedentary":
        recs.append("Increase physical activity with at least 30 minutes of exercise daily.")
    elif activity_level == "Moderate":
        recs.append("Continue moderate physical activity, and include stretching exercises.")
    elif activity_level == "Active":
        recs.append("Maintain your active routine, and ensure proper hydration and nutrition.")

    # ✅ Menstrual Health
    if menstrual_cycle == "Irregular":
        recs.append("Consider tracking your cycle using an app and consulting a gynecologist.")
    elif menstrual_cycle == "Regular":
        recs.append("Maintain a healthy diet and stay hydrated to support hormonal balance.")

    # ✅ Medical Conditions Management
    if "Asthma" in medical_conditions:
        recs.append("Avoid allergens, maintain good air quality, and always carry an inhaler if needed.")
    if "Diabetes" in medical_conditions:
        recs.append("Monitor blood sugar levels, follow a low-sugar diet, and engage in regular exercise.")
    if "PCOS" in medical_conditions:
        recs.append("Follow a diet rich in fiber and protein, exercise regularly, and manage stress levels.")
    if "Hypertension" in medical_conditions:
        recs.append("Reduce salt intake, manage stress, and engage in regular physical activity.")
    if "Thyroid" in medical_conditions:
        recs.append("Monitor thyroid levels, maintain a balanced diet, and avoid excessive caffeine intake.")

    # ✅ Stress Management
    if stress_level == "Often" or stress_level == "Always":
        recs.append("Practice relaxation techniques like meditation, yoga, and breathing exercises.")
    elif stress_level == "Occasionally":
        recs.append("Maintain a healthy work-life balance and engage in hobbies.")
    elif stress_level == "Never":
        recs.append("Continue maintaining a stress-free lifestyle through positive habits.")

    # ✅ Diet & Nutrition
    if home_cooked_meals == "Rarely":
        recs.append("Increase home-cooked meals for better nutrition and reduced processed food intake.")
    elif home_cooked_meals == "Few times a week":
        recs.append("Maintain a balance between home-cooked and outside meals while ensuring proper nutrition.")
    elif home_cooked_meals == "Daily":
        recs.append("Keep a nutritious and varied diet to ensure balanced nutrient intake.")

    # ✅ Healthcare Access
    if healthcare_access == "No":
        recs.append("Try accessing online consultations or local community healthcare services.")
    elif healthcare_access == "Yes":
        recs.append("Continue regular checkups and screenings for overall well-being.")

    # ✅ Healthcare Challenges
    if healthcare_challenges and healthcare_challenges != "None":
        recs.append(f"Consider solutions to overcome healthcare challenges: {healthcare_challenges}")

    return " ".join(recs) if recs else "Maintain a healthy lifestyle with regular checkups, exercise, and a balanced diet."

# Fetch Data from Google Sheets and Store in Database
def fetch_google_sheet_data():
    try:
        print("Fetching data from Google Sheets...")
        spreadsheet_id = "1Pqp70Q1VbtCk432aGE0xH54gzFiXERagIQdBVVL2uTA"
        print("check 1")
        sheet = client.open_by_key(spreadsheet_id).sheet1  
        print("check 2")
        data = sheet.get_all_records()
        print("check 3")
        df = pd.DataFrame(data)
        print("check 4")
        df.columns = df.columns.str.strip()
        print("check 5")
        df = df.drop(columns=["Timestamp"], errors="ignore")
        df.columns = df.columns.str.strip().str.replace(r'[^\w\s]', '', regex=True)
        column_mapping = {
            "What is your age?": "age",
            "How would you describe your daily activity level?": "activity_level",
            "Are your menstrual cycles regular?": "menstrual_cycle",
            "Do you have any medical conditions?": "medical_conditions",
            "How often do you feel stressed?": "stress_level",
            "How often do you eat home-cooked meals?": "home_cooked_meals",
            "Do you have access to primary healthcare?": "healthcare_access",
            "What challenges do you face in accessing healthcare?": "healthcare_challenges",
            "Comments:": "comments"
            "Health_Data.Recommendation :" "recommendation",  # Fix column name
        }
        df.rename(columns=column_mapping, inplace=True)
        print("check 6")
        with app.app_context():
            print("check 7")
            db.create_all()
            print("check 8")
            for _, row in df.iterrows():
               print("Row type:", type(row))  # Debugging
            if isinstance(row, pd.Series):  # Convert Series to Dictionary if needed
               row = row.to_dict()
               print("check 9 ")
            existing = HealthData.query.filter_by(age=row.get("age",0), activity_level=row.get("activity_level","Unknown")).first()
            print("Row data:", row)
            print("Existing data found:", existing)
            if not existing:
                    print("check 11")
            recommendation = generate_recommendation(
                       row.get("age", 0), 
                       row.get("activity_level", "Unknown"), 
                       row.get("menstrual_cycle", "Unknown"), 
                       row.get("medical_conditions", "None"), 
                       row.get("stress_level", "Occasionally"),
                       row.get("home_cooked_meals", "Few times a week"), 
                       row.get("healthcare_access", "Yes"), 
                       row.get("healthcare_challenges", ""))
            print(recommendation)
            print("check 12")
            row_dict = row.to_dict() if isinstance(row, pd.Series) else row
            row_dict["recommendation"] = recommendation  # Add recommendation manually

            new_entry = HealthData(**row_dict)
            print("check 13")
            db.session.add(new_entry)
            db.session.commit()
            print("✅ Google Sheets data successfully saved to the database!")
    except Exception as e:
        print(f"❌ Error fetching Google Sheets data: {e}")

# Admin Login Route
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_CREDENTIALS['username'] and password == ADMIN_CREDENTIALS['password']:
            session['admin_logged_in'] = True
            return redirect(url_for('dashboard'))
        return render_template('admin_login.html', error="Invalid credentials. Try again.")
    return render_template('admin_login.html')

# Admin Dashboard
@app.route('/dashboard')
def dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))  # Redirect to login if not authenticated

    users = HealthData.query.all()  # Fetch all user health data from DB
    return render_template('dashboard.html', users=users)


# Admin Logout Route
@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

# Health Recommendation API
@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        data = request.form
        age = int(data.get("age"))
        activity_level = data.get("activity_level")
        menstrual_cycle = data.get("menstrual_cycle")
        medical_conditions = data.get("medical_conditions", "None")
        stress_level = data.get("stress_level", "Occasionally")
        home_cooked_meals = data.get("home_cooked_meals", "Yes")
        healthcare_access = data.get("healthcare_access", "No")
        healthcare_challenges = data.get("healthcare_challenges", "Poor quality of university dispensary")
        comments = data.get("comments", "")

        # Generate health recommendation
        recommendation = generate_recommendation(age, activity_level, menstrual_cycle, medical_conditions, stress_level, home_cooked_meals, healthcare_access, healthcare_challenges
        )
        
     # Save the submitted data into the database
        new_entry = HealthData(
            age=age,
            activity_level=activity_level,
            menstrual_cycle=menstrual_cycle,
            medical_conditions=medical_conditions,
            stress_level=stress_level,
            home_cooked_meals=home_cooked_meals,
            healthcare_access=healthcare_access,
            healthcare_challenges=healthcare_challenges,
            comments=comments,
            recommendation=recommendation  # Store recommendation
        )
        db.session.add(new_entry)
        db.session.commit()

        return jsonify({"recommendation": recommendation})
    except Exception as e:
        return jsonify({"error": str(e)})

# Flask Routes
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/services")
def services():
    return render_template("services.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("db file created successfully")
        fetch_google_sheet_data()
    app.run(debug=True)
