from flask import Flask, request, jsonify
import PyPDF2
import pytesseract
from PIL import Image
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

stored_text = ""

# ---------- READ PDF ----------
@app.route("/pdf", methods=["POST"])
def read_pdf():
    global stored_text
    file = request.files["file"]
    reader = PyPDF2.PdfReader(file)

    stored_text = ""
    for page in reader.pages:
        stored_text += page.extract_text()

    return jsonify({"status": "PDF loaded successfully"})

# ---------- READ IMAGE ----------
@app.route("/image", methods=["POST"])
def read_image():
    global stored_text
    image = Image.open(request.files["file"])
    stored_text = pytesseract.image_to_string(image)

    return jsonify({"status": "Image processed successfully"})

# ---------- SUMMARY ----------
@app.route("/summary")
def summary():
    level = request.args.get("level", "short")
    sentences = stored_text.split(".")

    if level == "short":
        result = sentences[:3]
    elif level == "medium":
        result = sentences[:7]
    else:
        result = sentences[:12]

    return jsonify({"summary": result})

# ---------- QUESTION ANSWER ----------
@app.route("/ask", methods=["POST"])
def ask():
    question = request.json["question"].lower()
    keywords = question.split()

    for sentence in stored_text.split("."):
        for word in keywords:
            if word in sentence.lower():
                return jsonify({"answer": sentence.strip()})

    return jsonify({"answer": "Answer not found in document"})

# ---------- WORD CHART ----------
@app.route("/chart")
def chart():
    freq = {}
    for word in stored_text.lower().split():
        if word.isalpha():
            freq[word] = freq.get(word, 0) + 1

    top = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:6]
    labels = [x[0] for x in top]
    values = [x[1] for x in top]

    plt.figure()
    plt.bar(labels, values)
    plt.title("Word Frequency Chart")

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)

    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close()

    return jsonify({"image": image_base64})

if __name__ == "__main__":
    app.run()
