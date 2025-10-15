from flask import Flask, render_template, request, jsonify
#from flask import Flask, render_template, jsonify, request, send_file, redirect, session, url_for
import whisper
import whisper
import os
#import templates
import google.generativeai as genai
import json
import re

# 🔑 Set your Gemini API key
genai.configure(api_key="Replace with your key")


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/process_audio', methods=['POST'])
def process_audio():
    
    try:
        # ✅ Get uploaded audio file
        audio = request.files['audio']
        os.makedirs("uploads", exist_ok=True)
        file_path = os.path.join("uploads", audio.filename)
        audio.save(file_path)

        print(f"✅ File received and saved: {file_path}")

        # ✅ Transcribe using Whisper
        model = whisper.load_model("tiny")
        result = model.transcribe(file_path)
        transcript = result["text"]

        print("✅ Transcription complete")



        # this model for summary 

        
        prompt = prompt = f"""
        You are an AI meeting assistant.
        Summarize the following meeting transcript into a concise and coherent summary, capturing the main points and discussions.
        Keep it clear and easy to read.
        Transcript:
        {transcript}  """


        # Initialize model (you can use gemini-1.5-flash or gemini-1.5-pro)
        model = genai.GenerativeModel("gemini-2.5-pro")

        response = model.generate_content(prompt)

        summary_output = response.text


        

        # ✅ Extract decisions and action items in structured JSON
        prompt_analysis = f"""
You are an AI meeting assistant.
Analyze the following meeting transcript and extract three things clearly:


1. *Key Decisions* – List of decisions finalized.
2. *Action Items* – List of actionable tasks with responsible persons and deadlines (if mentioned).

Return the output in structured JSON format like this:

{{

  "decisions": ["..."],
  "action_items": [
    {{"task": "...", "assigned_to": "...", "deadline": "..."}}
  ]
}}

Transcript:
{transcript
 }
"""

        response_analysis = model.generate_content(prompt_analysis)
        output_text = response_analysis.text
        clean_output = re.sub(r"^```json\s*|```$", "", output_text, flags=re.MULTILINE).strip()

        try:
            summary_output1 = json.loads(clean_output)
        except json.JSONDecodeError as e:
            print("❌ JSON parsing error:", e)
            print("Raw output:", output_text)
            summary_output1 = {"decisions": [], "action_items": []}

        

        # ✅ Send response back to frontend
        return jsonify({
            "transcript": transcript,
            "summary": summary_output,
            "decisions": summary_output1.get("decisions", []),
            "action_items": summary_output1.get("action_items", [])
        })

    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host -"0.0.0.0",debug=True)
