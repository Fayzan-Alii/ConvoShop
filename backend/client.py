import requests

url = "http://localhost:8000/chat/invoke"

headers = {
    "Content-Type": "application/json"
}

data = {
    "input": {
        "messages": [
            {
                "content": "What is 2 + 3?",
                "type": "human"
            }
        ]
    },
    "config": {
        "configurable": {
            "checkpoint_id": "test_checkpoint",
            "checkpoint_ns": "",
            "thread_id": ""
        }
    },
    "kwargs": {}
}

response = requests.post(url, json=data, headers=headers)

print(response.json())
