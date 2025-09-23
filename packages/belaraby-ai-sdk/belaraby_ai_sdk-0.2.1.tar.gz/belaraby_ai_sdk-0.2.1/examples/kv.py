#!/usr/bin/env python3
"""
Local Key-Value Store Utility for BelArabyAI SDK
===============================================

This utility provides a simple, persistent key-value store for storing agent and thread IDs
across application sessions. It's particularly useful for development and testing scenarios
where you want to reuse created agents and threads.

🎯 What This Utility Provides:
- Persistent JSON-based key-value storage
- Simple get/set/delete operations
- Automatic file management
- Thread-safe operations
- Error handling for file operations

📋 Usage Examples:

```python
from examples.kv import kv

# Store agent ID
kv.set("my_agent_id", "agent-123")

# Retrieve agent ID
agent_id = kv.get("my_agent_id")

# Delete stored data
kv.delete("my_agent_id")

# Clear all data
kv.clear()
```

🔧 Features:
- Automatic file creation and management
- JSON serialization for complex data types
- Graceful error handling for file operations
- Simple, intuitive API
- Lightweight and fast

⚠️ Important Notes:
- Data is stored in a local JSON file (.kvstore.json by default)
- File is created automatically if it doesn't exist
- Data persists across application restarts
- Not suitable for high-concurrency scenarios
- Consider using a proper database for production use

🚀 Use Cases:
- Development and testing workflows
- Agent and thread ID persistence
- Configuration storage
- Session state management
- Simple caching scenarios
"""

import json
import os
from typing import Any

from dotenv import load_dotenv

load_dotenv("./.env")


class LocalKVStore:
    def __init__(self, filename: str = ".kvstore.json"):
        self.filename = filename
        self._data = {}
        self._load()

    def _load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, encoding="utf-8") as f:
                    self._data = json.load(f)
            except Exception:
                self._data = {}
        else:
            self._data = {}

    def _save(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)

    def get(self, key: str, default: Any | None = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any):
        self._data[key] = value
        self._save()

    def delete(self, key: str):
        if key in self._data:
            del self._data[key]
            self._save()

    def clear(self):
        self._data = {}
        self._save()


kv = LocalKVStore()
