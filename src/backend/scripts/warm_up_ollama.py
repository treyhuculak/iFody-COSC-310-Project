import urllib.request
import json
import time

OLLAMA_URL = "http://ollama:11434"

print("Warming up model in background...")

# Wait a bit for FastAPI to fully start
time.sleep(3)

# Send dummy request to load model into memory to initialize the model, speed up the response time for the first prompt
# an except to handle if the model is not ready yet
retried_num = 5
for attempt in range(retried_num):
    try:
        data = json.dumps({
            "model": "llama3.2:3b",
            "prompt": "You are a food assistant. what food do you recommend",
            "stream": False
        }).encode()

        req = urllib.request.Request(
            f"{OLLAMA_URL}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen(req, timeout=120) as response:
            print("Model warmed up and ready!")
            break  # success, exit the loop

    except urllib.error.URLError as e:
        print(f"Attempt {attempt + 1}/{retried_num} failed: {e}")
        if attempt < retried_num - 1:
            print("Retrying in 5 seconds...")
            time.sleep(5)
        else:
            print("Could not warm up model, but server is still running.")

    except Exception as e:
        print(f"Unexpected error during warmup: {e}")
        break