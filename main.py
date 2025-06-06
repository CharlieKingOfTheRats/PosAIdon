# Copyright © 2025 PantheonAI. All rights reserved.
import os
import openai
import tiktoken
import requests
import sqlite3
from bs4 import BeautifulSoup
from datetime import datetime

# Azure OpenAI Config
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = "2023-05-15"
AZURE_DEPLOYMENT_NAME_GPT4O = "gpt-4o"
AZURE_DEPLOYMENT_NAME_GPT35 = "gpt-35-turbo"

openai.api_type = "azure"
openai.api_key = AZURE_OPENAI_KEY
openai.api_base = AZURE_OPENAI_ENDPOINT
openai.api_version = AZURE_OPENAI_API_VERSION

# SQLite setup
DB_PATH = "engineering_logs.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS analysis_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    user_problem TEXT,
                    complexity_score REAL,
                    consistency_score REAL
                )''')
    conn.commit()
    conn.close()

def log_metrics(user_problem, complexity_score, consistency_score):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO analysis_log (timestamp, user_problem, complexity_score, consistency_score)
                 VALUES (?, ?, ?, ?)''', (datetime.now(), user_problem, complexity_score, consistency_score))
    conn.commit()
    conn.close()

def estimate_tokens(text, model="gpt-4o"):
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))

def extract_subject(problem_statement, model=AZURE_DEPLOYMENT_NAME_GPT35):
    messages = [
        {"role": "system", "content": "Summarize this engineering issue into a short title (3-5 words)."},
        {"role": "user", "content": f"{problem_statement}"}
    ]
    response = openai.ChatCompletion.create(
        engine=model,
        messages=messages,
        temperature=0,
        max_tokens=30
    )
    return response.choices[0].message["content"].strip()

def get_website_text(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text()
    except Exception as e:
        return f"[ERROR] Failed to load content from {url}: {e}"

def web_search(query, max_results=2):
    print(f"[INFO] Simulating web search for: {query}")
    # You could plug in SerpAPI or local PDF retrieval here
    return [
        "https://www.engineering.com/",
        "https://www.nasa.gov/"
    ][:max_results]

def estimate_complexity(problem_text, model=AZURE_DEPLOYMENT_NAME_GPT35):
    messages = [
        {"role": "system", "content": "You are a senior systems engineer. Estimate the technical complexity of this problem on a scale of 0 to 10."},
        {"role": "user", "content": problem_text}
    ]
    response = openai.ChatCompletion.create(
        engine=model,
        messages=messages,
        temperature=0.3,
        max_tokens=50
    )
    try:
        return float("".join(c for c in response.choices[0].message["content"] if c.isdigit() or c == '.'))
    except:
        return 0.0

def check_consistency(user_problem, model=AZURE_DEPLOYMENT_NAME_GPT35):
    messages = [
        {"role": "system", "content": "Generate a brief engineering mitigation plan based on the user's stated problem."},
        {"role": "user", "content": user_problem}
    ]
    plans = []
    for _ in range(3):
        response = openai.ChatCompletion.create(
            engine=model,
            messages=messages,
            temperature=0.7,
            max_tokens=400
        )
        plans.append(response.choices[0].message["content"])
    unique_plans = set(plans)
    consistency_score = 1.0 - (len(unique_plans) - 1) / 2.0
    return round(consistency_score, 2)

def draft_documentation(problem_text, retrieved_context, model=AZURE_DEPLOYMENT_NAME_GPT4O):
    messages = [
        {"role": "system", "content": "You are a senior engineer writing a technical analysis memo based on a user’s problem and supporting context."},
        {"role": "user", "content": f"Problem: {problem_text}\n\nContext:\n{retrieved_context}\n\nPlease write a short engineering analysis."}
    ]
    response = openai.ChatCompletion.create(
        engine=model,
        messages=messages,
        temperature=0.5,
        max_tokens=800
    )
    return response.choices[0].message["content"]

def auto_engineering_assistant(user_problem):
    print(f"\n[INFO] Starting engineering document generation for: {user_problem}")

    subject = extract_subject(user_problem)
    print(f"[INFO] Extracted subject: {subject}")

    urls = web_search(user_problem)
    aggregated_text = ""
    for url in urls:
        text = get_website_text(url)
        if "[ERROR]" not in text:
            aggregated_text += text[:2000] + "\n\n"

    complexity = estimate_complexity(user_problem)
    consistency = check_consistency(user_problem)
    documentation = draft_documentation(user_problem, aggregated_text)

    log_metrics(user_problem, complexity, consistency)

    print("\n📘 Engineering Memo:")
    print(documentation)
    print(f"\n📊 Complexity Score: {complexity}")
    print(f"🔁 Consistency Score: {consistency}")