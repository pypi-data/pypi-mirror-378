#!/usr/bin/env python3
import urllib.request
import json
from typing import Dict, List, Optional
from pathlib import Path
import base64

GITHUB_API_BASE = "https://api.github.com"
REPO_OWNER = "browserbase"
REPO_NAME = "stagehand-python"
EXAMPLES_PATH = "examples"

def get_available_templates() -> List[Dict[str, str]]:
    """Fetch list of available templates from GitHub repository."""
    try:
        url = f"{GITHUB_API_BASE}/repos/{REPO_OWNER}/{REPO_NAME}/contents/{EXAMPLES_PATH}"
        req = urllib.request.Request(url)
        req.add_header("Accept", "application/vnd.github.v3+json")
        req.add_header("User-Agent", "create-browser-app-py")

        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())

        templates = []
        for item in data:
            if item["type"] == "file" and item["name"].endswith(".py"):
                # Keep the original name without replacing underscores
                template_name = item["name"].replace(".py", "")
                templates.append({
                    "name": template_name,
                    "filename": item["name"],
                    "url": item["download_url"],
                    "api_url": item["url"]
                })

        return templates
    except Exception as e:
        print(f"Error fetching templates: {e}")
        return []

def fetch_template_content(template_info: Dict[str, str]) -> Optional[str]:
    """Fetch the content of a specific template from GitHub."""
    try:
        url = template_info.get("api_url", template_info.get("url"))
        req = urllib.request.Request(url)
        req.add_header("Accept", "application/vnd.github.v3+json")
        req.add_header("User-Agent", "create-browser-app-py")

        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())

        if "content" in data:
            content = base64.b64decode(data["content"]).decode("utf-8")
        else:
            # Fallback to direct download
            with urllib.request.urlopen(template_info["url"]) as response:
                content = response.read().decode("utf-8")

        return content
    except Exception as e:
        print(f"Error fetching template content: {e}")
        return None

def get_template_by_name(name: str) -> Optional[Dict[str, str]]:
    """Get a specific template by name."""
    templates = get_available_templates()
    for template in templates:
        if template["name"] == name:
            return template
    return None

def list_templates() -> List[str]:
    """Get a list of template names."""
    templates = get_available_templates()
    return [t["name"] for t in templates]