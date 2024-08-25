from flask import Flask, request, render_template
import json
from firecrawl import FirecrawlApp
import google.generativeai as genai
import markdown
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize Firecrawl
firecrawl = FirecrawlApp(api_key=os.getenv('FIRECRAWL_API_KEY'))

def get_summary_and_points(page_content):
    summary = model.generate_content(f'give the summary of the page content within 300 words , the page content is: {page_content}').text
    important_points = model.generate_content(f'give the list of important points (described) at most 30 points at least 5 points for the page content : {page_content}').text
    print("Summary is:",summary)
    print("Important points is;",important_points)
    important_points_html = markdown.markdown(important_points)
    return summary,important_points_html

@app.route('/', methods=['GET', 'POST'])
def index():
    summary = None
    important_points = None
    url = None

    if request.method == 'POST':
        url = request.form['url']
        print("URL GOT:",url)
        try:
            page_content = firecrawl.scrape_url(url=url, params={"pageOptions": {"onlyMainContent": True}})
            summary, important_points = get_summary_and_points(page_content)
            print("Sumary is:",summary)
        except Exception as e:
            summary = "An error occurred: " + str(e)

    return render_template('index.html', summary=summary, important_points=important_points, url=url)

if __name__ == '__main__':
    app.run(debug=True)
