import os
import requests
from bs4 import BeautifulSoup
import openai

REPLIT_API_PASSWORD = os.getenv("REPLIT_API_PASSWORD")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

def fetch_website_content(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to fetch the website content")
    return response.content

def optimize_seo(content):
    prompt = f"Analyze and provide SEO suggestions for the following HTML content:

{content}"
    response = openai.Completion.create(
        engine="davinci-codex",
        prompt=prompt,
        max_tokens=150
    )
    suggestions = response.choices[0].text.strip()
    return suggestions

def main():
    url = input("Enter the URL of the website to optimize: ")
    try:
        content = fetch_website_content(url)
        soup = BeautifulSoup(content, 'html.parser')
        optimized_suggestions = optimize_seo(soup.prettify())
        print("SEO Optimization Suggestions:")
        print(optimized_suggestions)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
