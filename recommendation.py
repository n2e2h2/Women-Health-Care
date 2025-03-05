import numpy as np

def get_health_recommendation(age, activity_level, menstrual_cycle):
    # Example logic: Replace this with real clustering analysis
    if age < 30 and activity_level == "Active" and menstrual_cycle == "Regular":
        return "You have a healthy routine. Maintain a balanced diet and exercise!"
    elif age >= 30 and activity_level == "Sedentary":
        return "Consider a more active lifestyle with light exercises and a better diet."
    else:
        return "Consult a healthcare expert for personalized guidance."
