#!/usr/bin/env python3
"""
GitHub Stars Categorizer - Auto-update script
Usage: python update_stars.py [--commit] [--dry-run]

--commit: Auto-commit and push changes
--dry-run: Only show what would change without writing
"""

import subprocess
import json
import argparse
from datetime import datetime
from pathlib import Path

# Category definitions with keywords
CATEGORIES = {
    "Claude Code & Anthropic": {
        "emoji": "🤖",
        "keywords": ["claude-code", "claude code", "claudecode", "anthropic", "claude-", "claude "]
    },
    "OpenClaw Ecosystem": {
        "emoji": "🦞",
        "keywords": ["openclaw", "clawx", "claw", "lightclaw", "nullclaw"]
    },
    "AI Agents & Frameworks": {
        "emoji": "🧠",
        "keywords": ["agent", "agentic", "manus", "deer-flow", "agency", "flowise", "lobster"]
    },
    "MCP (Model Context Protocol)": {
        "emoji": "🔧",
        "keywords": ["mcp", "mcp-", "-mcp"]
    },
    "LLMs & ML Models": {
        "emoji": "🤖",
        "keywords": ["transformers", "llm", "foundation model", "qwen", "kimi", "moonshot", "deepseek", "hunyuan", "megatron", "litellm"]
    },
    "RAG & Vector Databases": {
        "emoji": "🔍",
        "keywords": ["vector", "rag", "embed", "retrieval", "lmcach", "mooncake", "pageindex"]
    },
    "Memory & Context Engineering": {
        "emoji": "💾",
        "keywords": ["memory", "context", "memU", "supermemory"]
    },
    "Finance & Trading": {
        "emoji": "💰",
        "keywords": ["financial", "trading", "quant", "stock", "fintech", "lean", "openbb", "money printer", "dexter", "maverick"]
    },
    "Browser Automation & Scraping": {
        "emoji": "🌐",
        "keywords": ["puppeteer", "playwright", "browser", "scraping", "scrape", "chrome", "nightmare", "singlefile", "headless"]
    },
    "Media Generation": {
        "emoji": "🎨",
        "keywords": ["stable diffusion", "video", "audio", "tts", "voice", "image generation", "moneyprinter", "stremio", "animation"]
    },
    "Security & OSINT": {
        "emoji": "🔐",
        "keywords": ["security", "osint", "hack", "exploit", "pentest", "prompt-guard", "injection"]
    },
    "System Prompts & Prompt Engineering": {
        "emoji": "📝",
        "keywords": ["prompt", "system prompt", "heretic"]
    },
    "Learning & Courses": {
        "emoji": "📚",
        "keywords": ["course", "bootcamp", "tutorial", "learning", "certification", "udemy", "ibm", "training"]
    },
    "APIs & Public Data": {
        "emoji": "🔌",
        "keywords": ["public-api", "public apis", "api wrapper"]
    },
    "Operating Systems & Infrastructure": {
        "emoji": "🖥️",
        "keywords": ["stereos", "operating system", "daemon", "sandbox", "ladybird"]
    },
    "Developer Tools": {
        "emoji": "⚡",
        "keywords": ["cli", "tool", "utility", "markdown", "summarize", "markitdown", "gogcli", "qmd"]
    },
    "Discord & Chat": {
        "emoji": "🎮",
        "keywords": ["discord", "socket.io", "chat"]
    },
    "Mobile & UI": {
        "emoji": "📱",
        "keywords": ["android", "mobile", "ui", "desktop app", "gui"]
    },
    "Data & Databases": {
        "emoji": "🗄️",
        "keywords": ["pandas", "data", "database", "jupyter"]
    },
    "Awesome Lists": {
        "emoji": "📦",
        "keywords": ["awesome-", "awesome "]
    },
    "Skills & Plugins": {
        "emoji": "⚡",
        "keywords": ["skill", "plugin"]
    }
}


def fetch_starred_repos():
    """Fetch all starred repos using GitHub CLI"""
    print("📥 Fetching starred repos from GitHub...")

    cmd = ["gh", "api", "user/starred", "--paginate", "-q",
           '.[] | "\(.full_name)|||\(.description)//"']

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ Error fetching repos: {result.stderr}")
        return []

    repos = []
    for line in result.stdout.strip().split('\n'):
        if '|||' in line:
            parts = line.split('|||')
            name = parts[0]
            desc = parts[1].replace('//', '').strip() if len(parts) > 1 else ''
            repos.append({"name": name, "desc": desc})

    print(f"✅ Found {len(repos)} starred repos")
    return repos


def categorize_repo(repo):
    """Categorize a single repo based on keywords"""
    name_lower = repo['name'].lower()
    desc_lower = repo['desc'].lower()
    combined = f"{name_lower} {desc_lower}"

    for cat_name, cat_info in CATEGORIES.items():
        for keyword in cat_info['keywords']:
            if keyword.lower() in combined:
                return cat_name

    return "Other"


def generate_readme(repos, categorized):
    """Generate the README.md content"""
    sorted_cats = sorted(categorized.items(), key=lambda x: len(x[1]), reverse=True)

    md = f"""# ⭐ GitHub Stars - Categorized

> **Total Repositories:** {len(repos)}
> **Categories:** {len(sorted_cats)}
> **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 🚀 Quick Update

```bash
# Update the list
python update_stars.py --commit

# Or just preview changes
python update_stars.py --dry-run
```

---

## 📊 Visual Summary

```
"""

    for cat, repos_list in sorted_cats:
        count = len(repos_list)
        bar = '█' * min(count, 30) + ('...' if count > 30 else '')
        emoji = CATEGORIES.get(cat, {}).get('emoji', '📁')
        md += f"{emoji} {cat[:25]:25} | {bar} {count}\n"

    md += """```

---

"""

    # Add each category
    for cat, repos_list in sorted_cats:
        emoji = CATEGORIES.get(cat, {}).get('emoji', '📁')
        md += f"## {emoji} {cat}\n\n"
        md += f"> {len(repos_list)} repositories\n\n"

        for repo in sorted(repos_list, key=lambda x: x['name'].lower()):
            md += f"- **[{repo['name']}**](https://github.com/{repo['name']})\n"
            if repo['desc']:
                md += f"  - {repo['desc']}\n"
            md += "\n"

        md += "---\n\n"

    md += """## 🔗 Links

- [My GitHub Profile](https://github.com/MMIndustries)
- [Original Starred List](https://github.com/stars/MMIndustries)

---

*Auto-generated with [GitHub Stars Categorizer](https://github.com/MMIndustries/github-stars-categorized)*
"""

    return md


def main():
    parser = argparse.ArgumentParser(description='Update GitHub Stars categorization')
    parser.add_argument('--commit', action='store_true', help='Auto-commit and push changes')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without writing')
    args = parser.parse_args()

    # Fetch repos
    repos = fetch_starred_repos()
    if not repos:
        return

    # Categorize
    print("🏷️ Categorizing repos...")
    categorized = {cat: [] for cat in CATEGORIES}
    categorized["Other"] = []

    for repo in repos:
        cat = categorize_repo(repo)
        categorized[cat].append(repo)

    # Remove empty categories
    categorized = {k: v for k, v in categorized.items() if v}

    # Generate README
    print("📝 Generating README...")
    readme_content = generate_readme(repos, categorized)

    if args.dry_run:
        print("\n" + "="*50)
        print("DRY RUN - Preview of changes:")
        print("="*50)
        print(f"\nTotal repos: {len(repos)}")
        print(f"Categories: {len(categorized)}")
        for cat, repos_list in sorted(categorized.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"  {cat}: {len(repos_list)}")
        return

    # Write README
    readme_path = Path(__file__).parent / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print(f"✅ README updated: {readme_path}")

    # Also save raw data
    data_path = Path(__file__).parent / "stars_data.json"
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump({
            "last_updated": datetime.now().isoformat(),
            "total": len(repos),
            "categories": {k: [r['name'] for r in v] for k, v in categorized.items()}
        }, f, indent=2)

    if args.commit:
        print("📦 Committing changes...")
        subprocess.run(["git", "add", "."], cwd=Path(__file__).parent)
        subprocess.run([
            "git", "commit", "-m",
            f"Update stars - {datetime.now().strftime('%Y-%m-%d')} ({len(repos)} repos)"
        ], cwd=Path(__file__).parent)
        subprocess.run(["git", "push"], cwd=Path(__file__).parent)
        print("✅ Changes pushed to GitHub!")


if __name__ == "__main__":
    main()
