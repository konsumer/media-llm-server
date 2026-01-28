#!/usr/bin/env python3
"""
Download qBittorrent search plugins from official and unofficial sources.
Usage: python3 install-search-plugins.py [--official] [--unofficial] [--all]
"""

import argparse
import json
import os
import re
import sys
import urllib.request
from pathlib import Path
from urllib.error import URLError, HTTPError

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: BeautifulSoup4 is required. Install with: pip install beautifulsoup4")
    sys.exit(1)

# Configuration
PLUGINS_DIR = Path("./config/qbittorrent/qBittorrent/nova3/engines")
OFFICIAL_REPO = "https://api.github.com/repos/qbittorrent/search-plugins/contents/nova3/engines"
OFFICIAL_RAW = "https://raw.githubusercontent.com/qbittorrent/search-plugins/master/nova3/engines"
UNOFFICIAL_WIKI = "https://raw.githubusercontent.com/wiki/qbittorrent/search-plugins/Unofficial-search-plugins.md"

# Skip these files (helpers, not actual plugins)
SKIP_FILES = {"__init__.py", "example.py"}


def download_file(url, dest):
    """Download a file from URL to destination."""
    try:
        print(f"  Downloading {dest.name}...", end=" ")
        with urllib.request.urlopen(url, timeout=10) as response:
            content = response.read()
            dest.write_bytes(content)
        print("✓")
        return True
    except (URLError, HTTPError) as e:
        print(f"✗ ({e})")
        return False


def get_official_plugins():
    """Get list of official plugins from GitHub API."""
    print("\n📦 Fetching official plugins...")
    try:
        with urllib.request.urlopen(OFFICIAL_REPO, timeout=10) as response:
            data = json.loads(response.read())
            plugins = [
                item["name"]
                for item in data
                if item["name"].endswith(".py") and item["name"] not in SKIP_FILES
            ]
        print(f"Found {len(plugins)} official plugins")
        return plugins
    except Exception as e:
        print(f"Error fetching official plugins: {e}")
        return []


def get_unofficial_plugins(include_private=False):
    """Get list of unofficial plugins by scraping the wiki page."""
    print("\n📦 Fetching unofficial plugins from wiki...")
    try:
        # Fetch the wiki HTML page
        req = urllib.request.Request(
            "https://github.com/qbittorrent/search-plugins/wiki/Unofficial-search-plugins",
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html_content = response.read().decode("utf-8")

        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        public_plugins = set()
        private_plugins = set()

        # Find the sections by looking for specific heading patterns
        current_section = None

        # Iterate through all elements in order
        for element in soup.find_all(['h1', 'h2', 'h3', 'tr']):
            # Update section based on headings
            if element.name in ['h1', 'h2', 'h3']:
                text = element.get_text().strip().lower()
                if 'public' in text and 'site' in text:
                    current_section = "public"
                elif 'private' in text and 'site' in text:
                    current_section = "private"

            # Extract plugin links from table rows
            elif element.name == 'tr' and current_section:
                # Find all links in this row
                links = element.find_all('a', href=True)
                for link in links:
                    href = link.get('href', '')
                    if href.endswith('.py'):
                        filename = href.split('/')[-1]
                        if filename not in SKIP_FILES:
                            if current_section == "public":
                                public_plugins.add(filename)
                            elif current_section == "private":
                                private_plugins.add(filename)

        # Convert to sorted lists
        public_plugins = sorted(public_plugins)
        private_plugins = sorted(private_plugins)

        if not public_plugins and not private_plugins:
            raise Exception("No plugins found in wiki")

        # Return based on include_private flag
        if include_private:
            print(f"Found {len(public_plugins)} public + {len(private_plugins)} private plugins")
            return public_plugins, private_plugins
        else:
            print(f"Found {len(public_plugins)} public plugins (use --private to include private trackers)")
            return public_plugins

    except Exception as e:
        print(f"Error fetching unofficial plugins: {e}")
        print("Falling back to minimal list...")
        # Minimal fallback list
        fallback = ["torrentgalaxy.py", "btdig.py", "magnetdl.py", "bitsearch.py"]
        if include_private:
            return fallback, []
        return fallback


def download_official_plugin(plugin_name):
    """Download an official plugin."""
    url = f"{OFFICIAL_RAW}/{plugin_name}"
    dest = PLUGINS_DIR / plugin_name
    return download_file(url, dest)


def download_unofficial_plugin(plugin_name):
    """Try to download an unofficial plugin from common sources."""
    # Try common unofficial sources
    sources = [
        f"https://raw.githubusercontent.com/qbittorrent/search-plugins/master/nova3/engines/{plugin_name}",
        f"https://raw.githubusercontent.com/MadeOfMagicAndWires/qBit-plugins/master/{plugin_name}",
    ]

    dest = PLUGINS_DIR / plugin_name

    for url in sources:
        try:
            print(f"  Trying {plugin_name}...", end=" ")
            with urllib.request.urlopen(url, timeout=10) as response:
                content = response.read()
                dest.write_bytes(content)
            print("✓")
            return True
        except (URLError, HTTPError):
            continue

    print(f"✗ (not found)")
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Download qBittorrent search plugins"
    )
    parser.add_argument(
        "--official",
        action="store_true",
        help="Download official plugins only",
    )
    parser.add_argument(
        "--unofficial",
        action="store_true",
        help="Download unofficial plugins only",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Download both official and unofficial plugins",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available plugins without downloading",
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="Include private trackers (requires login/account)",
    )

    args = parser.parse_args()

    # Default to --all if no flags specified (or if only --list is specified)
    if not (args.official or args.unofficial or args.all):
        args.all = True

    # Create plugins directory if it doesn't exist
    PLUGINS_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("qBittorrent Search Plugin Installer")
    print("=" * 60)
    print(f"Target directory: {PLUGINS_DIR}")

    # Track statistics
    stats = {"official": 0, "unofficial": 0, "failed": 0}

    # Handle official plugins
    if args.official or args.all:
        plugins = get_official_plugins()
        if args.list:
            print("\nOfficial plugins:")
            for p in sorted(plugins):
                print(f"  - {p}")
        else:
            print("\n📥 Downloading official plugins...")
            for plugin in plugins:
                if download_official_plugin(plugin):
                    stats["official"] += 1
                else:
                    stats["failed"] += 1

    # Handle unofficial plugins
    if args.unofficial or args.all:
        if args.private:
            result = get_unofficial_plugins(include_private=True)
            public_plugins, private_plugins = result
            all_plugins = public_plugins + private_plugins
        else:
            all_plugins = get_unofficial_plugins(include_private=False)
            public_plugins = all_plugins
            private_plugins = []

        if args.list:
            print("\nUnofficial PUBLIC plugins:")
            for p in sorted(public_plugins):
                print(f"  - {p}")
            if private_plugins:
                print("\nUnofficial PRIVATE plugins (require login):")
                for p in sorted(private_plugins):
                    print(f"  - {p}")
        else:
            print("\n📥 Downloading unofficial plugins...")
            for plugin in all_plugins:
                if download_unofficial_plugin(plugin):
                    stats["unofficial"] += 1
                else:
                    stats["failed"] += 1

    # Print summary
    if not args.list:
        print("\n" + "=" * 60)
        print("Summary:")
        print(f"  ✓ Official plugins: {stats['official']}")
        print(f"  ✓ Unofficial plugins: {stats['unofficial']}")
        if stats["failed"] > 0:
            print(f"  ✗ Failed: {stats['failed']}")
        print("=" * 60)
        print("\n💡 Next step: docker compose restart qbittorrent")

    return 0 if stats["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
