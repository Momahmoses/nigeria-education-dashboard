"""
Generates synthetic Nigerian education data: WAEC results, school census, budget allocations.
"""
import pandas as pd
import numpy as np
import os
from datetime import datetime

np.random.seed(42)

STATES = [
    "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa", "Benue",
    "Borno", "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti", "Enugu",
    "FCT Abuja", "Gombe", "Imo", "Jigawa", "Kaduna", "Kano", "Katsina",
    "Kebbi", "Kogi", "Kwara", "Lagos", "Nasarawa", "Niger", "Ogun",
    "Ondo", "Osun", "Oyo", "Plateau", "Rivers", "Sokoto", "Taraba",
    "Yobe", "Zamfara",
]

GEOPOLITICAL_ZONES = {
    "North West": ["Jigawa", "Kaduna", "Kano", "Katsina", "Kebbi", "Sokoto", "Zamfara"],
    "North East": ["Adamawa", "Bauchi", "Borno", "Gombe", "Taraba", "Yobe"],
    "North Central": ["Benue", "FCT Abuja", "Kogi", "Kwara", "Nasarawa", "Niger", "Plateau"],
    "South West": ["Ekiti", "Lagos", "Ogun", "Ondo", "Osun", "Oyo"],
    "South East": ["Abia", "Anambra", "Ebonyi", "Enugu", "Imo"],
    "South South": ["Akwa Ibom", "Bayelsa", "Cross River", "Delta", "Edo", "Rivers"],
}

STATE_ZONE = {state: zone for zone, states in GEOPOLITICAL_ZONES.items() for state in states}

ZONE_BASELINE_PASS_RATE = {
    "South West": 68, "South South": 62, "South East": 65,
    "North Central": 55, "North East": 42, "North West": 38,
}


def generate_education_data(n_schools_per_state: int = 50) -> pd.DataFrame:
    records = []
    school_id = 1
    for year in range(2015, 2025):
        for state in STATES:
            zone = STATE_ZONE.get(state, "North Central")
            baseline = ZONE_BASELINE_PASS_RATE[zone]
            state_trend = (year - 2015) * np.random.uniform(0.3, 1.2)
            state_budget_tier = np.random.choice(["low", "medium", "high"], p=[0.4, 0.4, 0.2])
            budget_multiplier = {"low": 0.7, "medium": 1.0, "high": 1.4}[state_budget_tier]

            n_schools = n_schools_per_state
            for _ in range(n_schools):
                teacher_qual = np.random.beta(3, 2) * 100
                infrastructure = np.random.beta(2.5, 2) * 100
                student_teacher_ratio = np.random.normal(35, 10).clip(10, 70)
                budget_per_student = np.random.lognormal(10, 0.4) * budget_multiplier

                pass_rate = (
                    baseline +
                    state_trend +
                    teacher_qual * 0.25 -
                    student_teacher_ratio * 0.3 +
                    infrastructure * 0.1 +
                    np.random.normal(0, 8)
                )
                pass_rate = np.clip(pass_rate, 5, 98)
                student_count = int(np.random.lognormal(5.5, 0.6))

                records.append({
                    "school_id": f"SCH-{school_id:06d}",
                    "state": state,
                    "geopolitical_zone": zone,
                    "year": year,
                    "waec_pass_rate": round(pass_rate, 1),
                    "student_count": student_count,
                    "teacher_qualification_score": round(teacher_qual, 1),
                    "infrastructure_score": round(infrastructure, 1),
                    "student_teacher_ratio": round(student_teacher_ratio, 1),
                    "budget_per_student_NGN": round(budget_per_student),
                    "budget_tier": state_budget_tier,
                    "school_type": np.random.choice(["public_day", "public_boarding", "private"], p=[0.6, 0.2, 0.2]),
                    "lga": f"{state}_LGA_{np.random.randint(1, 20)}",
                })
                school_id += 1

    df = pd.DataFrame(records)
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/education_data.csv", index=False)
    print(f"Generated {len(df):,} school-year records → data/education_data.csv")
    return df


if __name__ == "__main__":
    df = generate_education_data()
    print("\nAverage WAEC pass rate by state (2024):")
    print(df[df["year"] == 2024].groupby("state")["waec_pass_rate"].mean()
          .sort_values(ascending=False).round(1).to_string())
