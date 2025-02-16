import base64
import glob
import json
import os
import subprocess
from typing import List
from itertools import combinations
import sqlite3

import numpy as np
import requests
from dateutil import parser

AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")

url = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
header = {
    "Content-type": "application/json",
    "Authentication": f"Bearer {AIPROXY_TOKEN}",
}


def dataset(url, email="23f1003133@ds.study.iitm.ac.in"):
    script_path = "datagen.py"
    subprocess.run(["curl", "-o", script_path, url])
    subprocess.run(["uv", "run", script_path, email])


def format_with_prettier(file_path):
    subprocess.run(["prettier", "--write", file_path])


def count_days(file_path: str, day: str, file_dest: str):
    count = 0

    with open(file_path, "r") as f:
        content = f.readlines()
        weekday = parser.parse(content.strip()).strftime("%A")

        if weekday.toLowerCase()[:3] == day.toLowerCase()[:3]:
            count += 1

    with open(file_dest, "w") as f:
        f.write(str(count))


def sort_json(file_path, key: List[str], file_dest):
    subprocess.run(["jq", f"sort_by(.{',.'.join(key)})", file_path], ">", file_dest)


def recent_logs(dir_path, n, file_dest):
    log_files = sorted(
        glob.glob(os.path.join(dir_path, "*.log")), key=os.path.getmtime, reverse=True
    )[:n]

    first_lines = []
    for log_file in log_files:
        with open(log_file, "r") as f:
            first_lines.append(f.readline())

    with open(file_dest, "w") as f:
        f.write("\n".join(first_lines) + "\n")


def markdown_titles(dir_path, file_dest):
    md_files = glob.glob(os.path.join(dir_path, "**/*.md"), recursive=True)

    index = {}

    for md_file in md_files:
        with open(md_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

            for line in lines:
                line = line.strip()
                if line.startswith("# "):
                    filename = os.path.relpath(md_file, dir_path)
                    title = line[2:].strip()
                    index[filename] = title
                    break

    with open(file_dest, "w") as f:
        json.dump(index, f, indent=2)


def email_address(file_path, file_dest):
    with open(file_path, "r") as f:
        content = f.read()

    body = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": f"extract the senders email address from this email content `{content}`. Response should only be the senders email address. no other information.",
            }
        ],
    }

    response = requests.post(url, json=body, headers=header)
    response.raise_for_status()

    email = response.json()["choices"][0]["message"]

    with open(file_dest, "w") as f:
        f.write("\n".join(email) + "\n")


def from_image(image_path, extract, file_dest):
    ext = image_path.split(".")[-1]
    with open(image_path, "rb") as f:
        image = base64.b64encode(f.read())

    body = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "contents": [
                    {"type": "text", "text": f"extract the {extract} from this image"},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/{ext};base64,{image}"},
                    },
                ],
            }
        ],
    }

    response = requests.post(url, json=body, headers=header)
    response.raise_for_status()

    extracted = response.json()["choices"][0]["message"]

    with open(file_dest, "w") as f:
        f.write("\n".join(extracted) + "\n")


def similar_texts(file_path, file_dest):
    url = "https://aiproxy.sanand.workers.dev/openai/v1/embeddings"

    def get_embedding(text):
        body = {
            "model": "text-embedding-3-small",
            "input": text,
        }

        response = requests.post(url, json=body, headers=header)
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]

    with open(file_path, "r") as f:
        comments = [line.strip() for line in f if line.strip()]

    embeddings = {comment: get_embedding(comment) for comment in comments}

    most_similar_pair = None
    highest_similarity = -1

    for comment1, comment2 in combinations(comments, 2):
        vec1, vec2 = np.array(embeddings[comment1]), np.array(embeddings[comment2])
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    if similarity > highest_similarity:
        highest_similarity = similarity
        most_similar_pair = (comment1, comment2)

    if most_similar_pair:
        with open(file_dest, "w") as f:
            f.write(most_similar_pair[0] + "\n")
            f.write(most_similar_pair[1] + "\n")


def database_query(db_path, query, file_dest):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(query)
    results = cursor.fetchall()

    with open(file_dest, "w") as f:
        f.write("\n".join(results) + "\n")

    conn.close()
