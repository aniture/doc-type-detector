import os
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import PyPDF2
import docx

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def extract_text_from_pdf(path):
    text = ""
    try:
        with open(path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted
    except Exception as e:
        print("PDF extraction error:", e)
    return text

def extract_text_from_docx(path):
    try:
        doc = docx.Document(path)
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception as e:
        print("DOCX extraction error:", e)
        return ""

def classify_document(text):
    text = text.lower()

    categories = {
        "Stock Purchase Agreement": [
            "stock purchase agreement",
            "preferred stock purchase",
            "series a preferred stock",
            "closing conditions for the transaction",
            "purchase and sale of the preferred stock"
        ],
        "Certificate of Incorporation": [
            "certificate of incorporation",
            "amended and restated certificate",
            "delaware general corporation law",
            "common stock and preferred stock",
            "powers, preferences and special rights"
        ],
        "Investors’ Rights Agreement": [
            "investors’ rights agreement",
            "registration rights",
            "information rights",
            "right of first offer",
            "post-closing covenants"
        ]
    }

    scores = {category: 0 for category in categories}

    for category, keywords in categories.items():
        for kw in keywords:
            scores[category] += text.count(kw)

    print("Keyword Match Scores:", scores)  # Debug

    best_match = max(scores, key=scores.get)
    if scores[best_match] > 0:
        return best_match
    else:
        return "Unknown Document Type"


@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        file = request.files['document']
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            if filename.endswith('.pdf'):
                text = extract_text_from_pdf(filepath)
            elif filename.endswith('.docx'):
                text = extract_text_from_docx(filepath)
            else:
                result = "Unsupported file type."
                return render_template('index.html', result=result)

            result = classify_document(text)
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
