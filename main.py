from flask import Flask, render_template, jsonify, request
from flask_pymongo import PyMongo
import google.generativeai as genai

GOOGLE_API_KEY = "AIzaSyCPtSR4Bk7sSIvoOEPiRywsYt2UkJ0Y5oc"
genai.configure(api_key = GOOGLE_API_KEY)
model =  genai.GenerativeModel(model_name = "gemini-pro")

def parse_steps(input_string):
    steps = []
    lines = input_string.split("\n")
    for line in lines:
        if "->" in line:
            step = line.split("->")[1].strip()
            steps.append(step)
    return steps

import re

def extract_steps(input_string):
    steps = []
    pattern = r'Step \d+:\s*(.*?)\n'
    matches = re.findall(pattern, input_string)
    for match in matches:
        steps.append(match.strip())
    return steps

app = Flask(__name__)
# app.config["MONGO_URI"] = "mongodb+srv://ravi:12345@cluster0.hpw4hsi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# mongo = PyMongo(app)

@app.route("/")
def home():
    # try:
        # chats = mongo.db.chats.find({})
        # myChats = [chat for chat in chats]
        # print(myChats)
    return render_template("index.html")

@app.route("/api", methods=["GET", "POST"])
def qa():
    if request.method == "POST":
        print(request.json)
        question = request.json.get("question")
        prompt1 = f'''
          Act as an expert in the automation task. You have very deep understanding of automation in the filed of information technology. Give
          the step by step guide to achieve any automation task. Give only steps and not other information. One example for your understanding is
          user query: Whenever an SQL query returns a blank result, send an email via Gmail based
          on certain parameters. Whenever the user replies to the email, trigger a webhook to
          parse and insert gmail response data into the SQL table again.
          Response: Step 1-> Run SQL query
                    Setp 2-> Send the mail if the output of the SQL query is None or empty
                    Step 3 -> User will reply to that mail and now parse the resposne of that mail
                    Step 4-> Store the paresed response into database
          Now with the same way how can i do below task
          task: {question}


'''

        response = model.generate_content(prompt1)
        print(response.text)
        next_iter = parse_steps(response.text)
        if len(next_iter)==0:
            next_iter = extract_steps(response.text)
        print("next iter",next_iter)
        result_string = response.text + "  "
        for item in next_iter:
            prompt2 = f'''
          Give python code to do below task. Just give the code only. No need to give explanation about anything.
          task: {item}
'''
            print("item",item)
            print(type(item))
            print("prompt2",prompt2)
            response = model.generate_content(prompt2)
            result_string = result_string + "  " +response.text
        data = {"question": question, "answer": result_string}
        print("main thing------->",data)
        return jsonify(data)
    data = {"result": "Thank you! I'm just a machine learning model designed to respond to questions and generate text based on my training data. Is there anything specific you'd like to ask or discuss? "}
        
    return jsonify(data)


app.run(debug=True, port=5001)
