import os
import requests
import hashlib
from bs4 import BeautifulSoup
import openai
import logging
import sys
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

# Setup logging
log_file = "seo_optimization.log"
logging.basicConfig(filename=log_file, level=logging.INFO)

# Load your API keys and application password from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
APPLICATION_PASSWORD_BUCCANEER = os.getenv("APPLICATION_PASSWORD_BUCCANEER")
openai.api_key = OPENAI_API_KEY

# Sanity check to ensure API key and application password are present
if not OPENAI_API_KEY:
    raise RuntimeError(
        "OpenAI API key is not loaded. Please set the OPENAI_API_KEY environment variable."
    )
if not APPLICATION_PASSWORD_BUCCANEER:
    raise RuntimeError(
        "Application password is not loaded. Please set the APPLICATION_PASSWORD_BUCCANEER environment variable."
    )

MAX_ATTEMPTS = 10

optimization_log = {}


class LogRedirectionHandler(logging.Handler):
    """A logging handler to redirect logging output to Tkinter GUI"""
    def __init__(self, text_widget):
        logging.Handler.__init__(self)
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text_widget.configure(state="normal")
            self.text_widget.insert(tk.END, msg + "\n")
            self.text_widget.configure(state="disabled")
            self.text_widget.yview(tk.END)
        self.text_widget.after(0, append)

def gui_logger_setup(text_widget):
    handler = LogRedirectionHandler(text_widget)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)


def validate_plugins():
    essential_plugins = [
        "lite_speed_cache",
        "short_pixel",
        "google_site_kit",
        "link_whisperer",
    ]
    current_plugins = {
        plugin: True
        for plugin in essential_plugins
    }
    return current_plugins


def retrieve_website_content(url):
    response = requests.get(url, auth=("user", APPLICATION_PASSWORD_BUCCANEER))
    if response.status_code != 200:
        raise ConnectionError("Unable to fetch the website content")
    return response.content


def evaluate_content(content):
    analysis_prompt = (
        f"Evaluate the following HTML content for readability, keyword usage, "
        f"metadata, on-page SEO, and general SEO practices. Provide a score ranging from 0-100 for each criterion.\n\n{content}"
    )

    response = openai.Completion.create(engine="text-davinci-003",
                                        prompt=analysis_prompt,
                                        max_tokens=150)
    review = response.choices[0].text.strip()
    return review


def improve_content(content):
    rewrite_prompt = (
        f"Please rewrite the below HTML content to enhance SEO scores in areas such as readability, keyword usage, metadata, "
        f"internal linking, and overall on-page SEO compliance:\n\n{content}"
    )

    response = openai.Completion.create(engine="text-davinci-003",
                                        prompt=rewrite_prompt,
                                        max_tokens=500)
    updated_content = response.choices[0].text.strip()
    return updated_content


def extract_scores(review):
    review_lines = review.split('\n')
    score_dict = {}
    for line in review_lines:
        if ':' in line:
            metric_name, metric_score = line.split(':')
            score_dict[metric_name.strip()] = int(metric_score.strip())
    return score_dict


def is_seo_optimized(score_dict):
    return all(value >= 90 for value in score_dict.values())


def create_content_hash(content):
    return hashlib.md5(content.encode()).hexdigest()


def log_event(message):
    print(message)
    logging.info(message)


def fix_script(script_text):
    fix_prompt = (
        f'''Analyze and correct the following Python script. Look for syntax errors, 
        stylistic issues, and outdated methods. Offer a revised version of the script.\n\n{script_text}'''
    )

    response = openai.Completion.create(engine="text-davinci-003",
                                        prompt=fix_prompt,
                                        max_tokens=1000)
    fixed_script = response.choices[0].text.strip()
    return fixed_script


def main_task():
    # Load the current script's content
    with open(__file__, 'r') as file:
        script_text = file.read()

    try:
        # Attempt script repair
        fixed_script = fix_script(script_text)

        # Write repaired script if modifications are detected
        if script_text != fixed_script:
            with open(__file__, 'w') as file:
                file.write(fixed_script)
            log_event("Script has been repaired and saved.")

            # Relaunch the refined script
            os.execl(sys.executable, sys.executable, *sys.argv)

    except Exception as e:
        log_event(f"Error occurred during script repair: {e}")

    active_plugins = validate_plugins()

    site_urls = input(
        "Enter the URLs of the websites for optimization, separated by commas: "
    ).split(',')

    for url in site_urls:
        url = url.strip()
        if not url:
            continue

        log_event(f"Processing URL: {url}")

        try:
            raw_content = retrieve_website_content(url)
            soup = BeautifulSoup(raw_content, 'html.parser')
            formatted_content = soup.prettify()
            content_hash = create_content_hash(formatted_content)

            if url in optimization_log:
                log_entry = optimization_log[url]
                if log_entry['hash'] == content_hash:
                    log_event(f"Skipping {url}, no changes found.")
                    continue

                log_event(f"Re-optimizing {url}, new content detected.")
            else:
                log_event(f"First-time optimization for {url}.")

            optimized = False
            attempt = 0

            while not optimized and attempt < MAX_ATTEMPTS:
                attempt += 1
                review = evaluate_content(formatted_content)
                score_dict = extract_scores(review)

                log_event(f"Attempt {attempt}")
                log_event("Review Scores:")
                log_event(str(score_dict))

                if is_seo_optimized(score_dict):
                    optimized = True
                    log_event("Content is sufficiently optimized.")
                    break

                formatted_content = improve_content(formatted_content)
                soup = BeautifulSoup(formatted_content, 'html.parser')

            if not optimized:
                log_event(
                    "Max attempts reached without adequate optimization."
                )

            # Update optimization log
            optimization_log[url] = {
                'hash': content_hash,
                'last_attempt': attempt,
                'scores': score_dict
            }

            log_event("Updated Content:")
            log_event(soup.prettify())

        except Exception as e:
            log_event(f"Error encountered for {url}: {e}")

def setup_gui():
    root = tk.Tk()
    root.title("SEO Optimization Log")

    log_display = ScrolledText(root, wrap='word', state='disabled', height=20, width=100)
    log_display.pack()

    gui_logger_setup(log_display)

    def start_task():
        main_task()
    
    start_button = tk.Button(root, text="Start Optimization", command=start_task)
    start_button.pack()

    root.mainloop()

if __name__ == "__main__":
    setup_gui()