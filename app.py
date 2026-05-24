from flask import Flask, render_template, request
import os
import pdfplumber
import re

app = Flask(__name__)

# ---------------- UPLOAD FOLDER ---------------- #

UPLOAD_FOLDER = "resumes"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ---------------- SKILLS DATABASE ---------------- #

skills_list = [

    "python", "java", "sql", "html",
    "css", "javascript", "react",
    "flask", "django", "mysql",
    "machine learning", "tensorflow",
    "deep learning", "aws",
    "docker", "linux", "flutter",
    "android", "figma", "power bi",
    "excel", "c++", "nodejs"
]

# ---------------- JOB ROLES ---------------- #

job_roles = {

    "Python Developer":
        ["python", "flask", "sql"],

    "Frontend Developer":
        ["html", "css",
         "javascript", "react"],

    "Backend Developer":
        ["python", "java",
         "sql", "nodejs"],

    "Full Stack Developer":
        ["html", "css", "javascript",
         "react", "python", "sql"],

    "Data Scientist":
        ["python",
         "machine learning", "sql"],

    "AI Engineer":
        ["python",
         "tensorflow",
         "deep learning"],

    "Cloud Engineer":
        ["aws", "docker", "linux"],

    "Mobile App Developer":
        ["flutter", "android", "java"],

    "UI UX Designer":
        ["figma", "html", "css"]
}

# ---------------- RELATED SKILLS ---------------- #

related_skills = {

    "python": ["django", "flask"],

    "sql": ["mysql"],

    "javascript": ["react", "nodejs"],

    "machine learning":
        ["tensorflow", "deep learning"]
}

# ---------------- HOME ---------------- #

@app.route('/')
def home():

    return render_template('index.html')

# ---------------- CANDIDATE ---------------- #

@app.route('/candidate')
def candidate():

    return render_template('candidate.html')

# ---------------- LOGIN ---------------- #

@app.route('/login')
def login():

    return render_template('login.html')

# ---------------- SIGNUP ---------------- #

@app.route('/signup')
def signup():

    return render_template('signup.html')

# ---------------- ANALYSIS ---------------- #

@app.route('/upload', methods=['POST'])
def upload_resume():

    try:

        files = request.files.getlist('resume')

        selected_role = request.form.get('job_role')

        if not selected_role:

            return "Please select job role"

        job_skills = job_roles.get(
            selected_role, []
        )

        all_candidates = []

        for file in files:

            if file.filename == "":
                continue

            filepath = os.path.join(
                app.config['UPLOAD_FOLDER'],
                file.filename
            )

            file.save(filepath)

            extracted_text = ""

            with pdfplumber.open(filepath) as pdf:

                for page in pdf.pages:

                    text = page.extract_text()

                    if text:
                        extracted_text += text

            text_lower = extracted_text.lower()

            # ---------------- SKILLS ---------------- #

            found_skills = []

            for skill in skills_list:

                if skill in text_lower:
                    found_skills.append(skill)

            # ---------------- MATCH SCORE ---------------- #

            matched = 0

            missing_skills = []

            for skill in job_skills:

                if skill in found_skills:

                    matched += 1

                elif skill in related_skills:

                    related_found = False

                    for related in related_skills[skill]:

                        if related in text_lower:

                            matched += 1
                            related_found = True
                            break

                    if not related_found:
                        missing_skills.append(skill)

                else:
                    missing_skills.append(skill)

            if len(job_skills) > 0:

                score = int(
                    (matched / len(job_skills)) * 100
                )

            else:
                score = 0

            # ---------------- ATS BOOST ---------------- #

            if "project" in text_lower:
                score += 10

            if "internship" in text_lower:
                score += 10

            if score > 100:
                score = 100

            # ---------------- EDUCATION ---------------- #

            education = []

            education_keywords = [

                "b.tech", "m.tech",
                "bca", "mca",
                "mba", "b.sc"
            ]

            for edu in education_keywords:

                if edu in text_lower:
                    education.append(edu.upper())

            # ---------------- EMAIL ---------------- #

            emails = re.findall(

                r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',

                extracted_text
            )

            # ---------------- PHONE ---------------- #

            phones = re.findall(

                r'\b\d{10}\b',

                extracted_text
            )

            # ---------------- FAKE DETECTION ---------------- #

            fake_status = "Low"

            repeated = 0

            for skill in found_skills:

                if text_lower.count(skill) > 10:
                    repeated += 1

            if repeated >= 3:
                fake_status = "High"

            elif repeated >= 1:
                fake_status = "Medium"

            # ---------------- AI SUGGESTIONS ---------------- #

            suggestions = []

            # Missing Skills
            for skill in missing_skills:

                suggestions.append(
                    f"Improve your knowledge in {skill}"
                )

            # Projects
            if "project" not in text_lower:

                suggestions.append(
                    "Add strong real-time projects"
                )

            else:

                suggestions.append(
                    "Good project section detected"
                )

            # Internship
            if "internship" not in text_lower \
               and "experience" not in text_lower:

                suggestions.append(
                    "Add internship or practical experience"
                )

            else:

                suggestions.append(
                    "Experience section improves your resume strength"
                )

            # Resume Strength
            if score >= 85:

                suggestions.append(
                    "Excellent resume profile for this role"
                )

            elif score >= 70:

                suggestions.append(
                    "Your resume is strong but can improve with certifications"
                )

            elif score >= 50:

                suggestions.append(
                    "Moderate profile detected. Improve technical depth."
                )

            else:

                suggestions.append(
                    "Resume needs major improvements for this role"
                )

            # Certifications
            if "python" in found_skills:

                suggestions.append(
                    "Recommended Certification: Python for Everybody"
                )

            if "aws" in found_skills:

                suggestions.append(
                    "Recommended Certification: AWS Cloud Practitioner"
                )

            if "machine learning" in found_skills:

                suggestions.append(
                    "Recommended Certification: Google ML Certification"
                )

            # Resume Length
            if len(extracted_text.split()) > 350:

                suggestions.append(
                    "Good resume content length detected"
                )

            else:

                suggestions.append(
                    "Resume content is short. Add detailed descriptions."
                )

            # Formatting
            if "objective" not in text_lower:

                suggestions.append(
                    "Add career objective section"
                )

            if "skills" not in text_lower:

                suggestions.append(
                    "Add dedicated skills section"
                )

            # Best Role Detection
            best_role = ""

            highest_match = 0

            for role, role_skills in job_roles.items():

                temp_match = 0

                for rs in role_skills:

                    if rs in found_skills:
                        temp_match += 1

                if temp_match > highest_match:

                    highest_match = temp_match
                    best_role = role

            suggestions.append(
                f"Best suitable role detected: {best_role}"
            )

            # Interview Readiness
            if score >= 80:

                suggestions.append(
                    "Interview readiness level: High"
                )

            elif score >= 60:

                suggestions.append(
                    "Interview readiness level: Medium"
                )

            else:

                suggestions.append(
                    "Interview readiness level: Low"
                )

            # ---------------- STORE ---------------- #

            candidate_name = file.filename.replace(
                ".pdf", ""
            )

            all_candidates.append({

                "name": candidate_name,
                "score": score,
                "skills": found_skills,
                "education": education,
                "emails": emails,
                "phones": phones,
                "fake": fake_status,
                "suggestions": suggestions
            })

        # ---------------- SORT ---------------- #

        all_candidates = sorted(

            all_candidates,

            key=lambda x: x['score'],

            reverse=True
        )

        # ---------------- UI ---------------- #

        candidate_cards = ""

        rank = 1

        for candidate in all_candidates:

            if candidate['score'] >= 80:
                color = "success"

            elif candidate['score'] >= 50:
                color = "warning"

            else:
                color = "danger"

            candidate_cards += f"""

<div class="card shadow-lg p-4 mb-5 border-0 rounded-4">

<div class="d-flex justify-content-between">

<h2 class="text-info">
{candidate['name']}
</h2>

<span class="badge bg-dark fs-5">
Rank #{rank}
</span>

</div>

<hr>

<h5>Email</h5>

<p>
{', '.join(candidate['emails'])}
</p>

<h5>Phone</h5>

<p>
{', '.join(candidate['phones'])}
</p>

<hr>

<h5>ATS Score</h5>

<div class="progress mb-4"
     style="height:35px;">

<div class="progress-bar bg-{color}
            progress-bar-striped
            progress-bar-animated"

     style="width:{candidate['score']}%">

{candidate['score']}%

</div>

</div>

<hr>

<h5>Detected Skills</h5>

<div>

{
''.join(
f'<span class="badge bg-success m-1 p-2">{skill}</span>'
for skill in candidate['skills']
)
}

</div>

<hr>

<h5>Education</h5>

<ul>

{
''.join(
f'<li>{edu}</li>'
for edu in candidate['education']
)
}

</ul>

<hr>

<h5>Fake Resume Detection</h5>

<p>

<b>Status:</b>

<span class="text-danger">
{candidate['fake']}
</span>

</p>

<hr>

<h5>AI Suggestions</h5>

<div class="bg-light text-dark p-3 rounded">

<ul>

{
''.join(
f'<li>{suggestion}</li>'
for suggestion in candidate['suggestions']
)
}

</ul>

</div>

<br>

<button class="btn btn-primary">
Download Report
</button>

</div>

"""

            rank += 1

        # ---------------- FINAL PAGE ---------------- #

        return f"""

<!DOCTYPE html>
<html>

<head>

<title>SmartHire AI Dashboard</title>

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
      rel="stylesheet">

<style>

body {{
    background:#121212;
    color:white;
}}

.card {{
    background:#1f1f1f;
    color:white;
}}

</style>

</head>

<body>

<div class="container mt-5">

<h1 class="text-center text-info">
SmartHire AI
</h1>

<h4 class="text-center mb-5">
Advanced AI Resume Screening Dashboard
</h4>

<h3 class="text-center mb-5">

Selected Role:
<span class="text-warning">
{selected_role}
</span>

</h3>

{candidate_cards}

</div>

</body>

</html>

"""

    except Exception as e:

        return f"Error: {str(e)}"

# ---------------- RUN ---------------- #

if __name__ == "__main__":

    app.run(debug=True)