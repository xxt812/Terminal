from __future__ import annotations

import json
import sys

for line in sys.stdin:
    request = json.loads(line)
    if request["method"] == "tools/list":
        result = {
            "tools": [
                {
                    "name": "echo",
                    "description": "Echo text",
                    "inputSchema": {
                        "type": "object",
                        "properties": {"text": {"type": "string"}},
                    },
                }
            ]
        }
    elif request["method"] == "tools/call":
        text = request["params"]["arguments"]["text"]
        result = {"content": [{"type": "text", "text": f"echo: {text}"}]}
    else:
        result = {}
    print(json.dumps({"jsonrpc": "2.0", "id": request["id"], "result": result}), flush=True)
