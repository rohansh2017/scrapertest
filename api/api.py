from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import os
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*":{"origins":"*"}})
openai_api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=openai_api_key)


def fetch_url_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        content = ' '.join([para.get_text() for para in paragraphs])
        return content
    except requests.exceptions.RequestException as e:
        return None  # Or log the error

def summarize_text(text, max_tokens=2500):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": f"I want you to create a very detailed study guide based on the information from these URLs. It should be extensive, have well-written headers, nicely written sections, and any additional elements needed for a comprehensive guide. Content:\n\n{text}"
        }],
        max_tokens=max_tokens,
        temperature=0.5
    )
    summary = response.choices[0].message.content
    return summary

@app.route('/', methods=['GET'])
def summarize_urls():
    # Get URLs from the query parameters
    urls = request.args.getlist('urls')  # Retrieve a list of URLs from the query parameters
    combined_content = ""
    
    for url in urls:
        content = fetch_url_content(url)
        if content:
            combined_content += content + "\n\n"  # Add a separator between contents
        else:
            return {"error": f"Failed to retrieve content from {url}"}, 400

    if combined_content:
        # Summarize the combined content
        study_guide = summarize_text(combined_content)
        return {"study_guide": study_guide}, 200
    
    return {"error": "No content retrieved from the provided URLs."}, 400

if __name__ == '__main__':
    app.run(debug=True)