import json
import os

import requests
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

import scripts

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_headers=["*"], allow_origins=["*"])

AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")

url = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
header = {
    "Content-type": "application/json",
    "Authentication": f"Bearer {AIPROXY_TOKEN}",
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "dataset",
            "description": "with given url of a python script to generate dataset with user email as argument",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "url of the python script to generate dataset",
                    },
                    "email": {
                        "type": "string",
                        "description": "email of the user",
                    },
                },
                "required": ["url"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "format_with_prettier",
            "description": "give a file format it with prettier@3.4.2 and save it",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "path of the file to format",
                    },
                },
                "required": ["file_path"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "count_days",
            "description": "give a file with one date per line count a specific weekday and save it",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "path of the file with dates",
                    },
                    "day": {
                        "type": "string",
                        "description": "the specific weekday to count",
                    },
                    "file_dest": {
                        "type": "string",
                        "description": "path to save the count",
                    },
                },
                "required": ["file_path", "day", "file_dest"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "sort_json",
            "description": "given a json file sort it by the given key and save it",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "path of the json file to sort",
                    },
                    "key": {
                        "type": "List[str]",
                        "description": "key to sort the json file in order",
                    },
                    "file_dest": {
                        "type": "string",
                        "description": "path to save the sorted json file",
                    },
                },
                "required": ["file_path", "key", "file_dest"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "recent_logs",
            "description": "given a directory path get the first line of n recent log files and save it",
            "parameters": {
                "type": "object",
                "properties": {
                    "dir_path": {
                        "type": "string",
                        "description": "directory path to get the log files",
                    },
                    "n": {
                        "type": "number",
                        "description": "number of recent log files to get",
                    },
                    "file_dest": {
                        "type": "string",
                        "description": "path to save the first line of recent log files",
                    },
                },
                "required": ["dir_path", "n", "file_dest"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "markdown_titles",
            "description": "given a directory path get the titles of markdown files and save it",
            "parameters": {
                "type": "object",
                "properties": {
                    "dir_path": {
                        "type": "string",
                        "description": "directory path to get the markdown files",
                    },
                    "file_dest": {
                        "type": "string",
                        "description": "path to save the titles of markdown files",
                    },
                },
                "required": ["dir_path", "file_dest"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "email_address",
            "description": "given a file which contains email message extract senders email and save it",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "path of file which contains email message",
                    },
                    "file_dest": {
                        "type": "string",
                        "description": "path to save the senders email",
                    },
                },
                "required": ["file_path", "extract", "file_dest"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "from_image",
            "description": "given an image extract text from it and save it",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "path of the image file",
                    },
                    "extract": {
                        "type": "string",
                        "description": "text to extract from the image",
                    },
                    "file_dest": {
                        "type": "string",
                        "description": "path to save the senders email",
                    },
                },
                "required": ["file_path", "file_dest"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "similar_texts",
            "description": "given a file with texts find the most similar text pair and save it",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "path of the file with texts",
                    },
                    "file_dest": {
                        "type": "string",
                        "description": "path to save the most similar text pair",
                    },
                },
                "required": ["file_path", "file_dest"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "database_query",
            "description": "given a sqlite3 database connection string and query execute the query and save the result",
            "parameters": {
                "type": "object",
                "properties": {
                    "db_path": {
                        "type": "string",
                        "description": "path of the database file",
                    },
                    "query": {
                        "type": "string",
                        "description": "sqlite3 query to execute",
                    },
                    "file_dest": {
                        "type": "string",
                        "description": "path to save the results",
                    },
                },
                "required": ["db_path", "query", "file_dest"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
]


def call_function(name, args):
    if name == "dataset":
        return scripts.dataset(**args)
    if name == "format_with_prettier":
        return scripts.format_with_prettier(**args)
    if name == "count_days":
        return scripts.count_days(**args)
    if name == "sort_json":
        return scripts.sort_json(**args)
    if name == "recent_logs":
        return scripts.recent_logs(**args)
    if name == "markdown_titles":
        return scripts.markdown_titles(**args)
    if name == "email_address":
        return scripts.email_address(**args)
    if name == "from_image":
        return scripts.from_image(**args)
    if name == "similar_texts":
        return scripts.similar_texts(**args)
    if name == "database_query":
        return scripts.database_query(**args)


@app.post("/run")
def post_run(task: str):
    body = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": task}],
        "tools": tools,
        "tool-choice": "auto",
    }

    if task.__contains__("delete"):
        return Response(status_code=400)

    response = requests.post(url, json=body, headers=header)
    response.raise_for_status()

    tool_calls = response.json()["choices"][0]["message"]["tool_calls"]

    for tool_call in tool_calls:
        fn_name = tool_call.function.name
        fn_args = json.loads(tool_call.function.arguments)

        call_function(fn_name, fn_args)

    return {"task": "completed"}


@app.get("/read")
def get_read(path: str):
    if not path.begins_with("/data/"):
        return Response(status_code=404)

    try:
        with open(path, "r") as file:
            return file.read()
    except FileNotFoundError:
        return Response(status_code=404)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("hello:app", host="0.0.0.0", port=8000)
