#!/bin/bash
echo "Waiting for Ollama to start..."
sleep 5
python3 -c "
import urllib.request
import json

data = json.dumps({'name': 'llama3.2:3b'}).encode()
req = urllib.request.Request('http://ollama:11434/api/pull', data=data, headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as response:
    print(response.read().decode())
"
echo "Model ready!"