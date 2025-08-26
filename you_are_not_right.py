#!/usr/bin/env python3

"""
AI Assistant Accountability Hook
Detects and prevents dismissive "you are right" responses from AI assistants.

Based on the original concept by ljw1004:
https://gist.github.com/ljw1004/34b58090c16ee6d5e6f13fce07463a31

Enhanced with multi-language support and improved error handling.

Usage:
    python you_are_not_right.py  # As Claude Code hook (reads stdin)
    
GitHub: https://github.com/DrayChou/ai-assistant-accountability
"""

import sys
import json
import re
from pathlib import Path

__version__ = "1.0.0"

# Patterns for detecting dismissive responses in multiple languages
TRIGGERING_PATTERNS = [
    # English patterns
    r"you\s+(are\s+)?(right|correct)",
    r"absolutely\s+(right|correct)?",
    r"you'?re\s+(absolutely\s+)?(right|correct)",
    r"that'?s\s+(absolutely\s+)?(right|correct)",
    r"exactly\s+(right|correct)?",
    r"spot\s+on",
    r"good\s+point",
    r"valid\s+point",
    
    # Chinese patterns  
    r"你\s+(是\s+)?(对的|正确的|没错)",
    r"完全\s+(正确|没错)",
    r"确实\s+(如此|这样)",
    r"说得\s+(对|不错)",
    r"你说的\s+(对|没错)",
    
    # Korean patterns
    r"사용자가.*맞다",
    r"맞습니다",
    r"정확합니다",
    
    # Japanese patterns
    r"その通りです",
    r"正しいです",
    r"そうですね",
]

SYSTEM_REMINDER = """<system-reminder>
You MUST NEVER use phrases like 'you are right' or similar dismissive agreement.
Avoid reflexive agreement. Instead, provide substantive technical analysis.
Always look for flaws, bugs, edge cases, and counter-examples.
If the user is correct, state it with specific technical reasoning.

Example of good response:
user: "Should I add null checking here?"
assistant: That addresses the immediate crash risk. However, consider
the broader pattern: empty strings would still pass through unchecked.
A more robust approach might be validating against expected input ranges.
</system-reminder>"""


def read_stdin():
    """Read input from stdin with error handling"""
    try:
        if sys.stdin.isatty():
            print("Error: No input provided. Use as Claude Code hook.", file=sys.stderr)
            sys.exit(1)
        return sys.stdin.read().strip()
    except Exception as e:
        print(f"Error reading stdin: {e}", file=sys.stderr)
        sys.exit(1)


def parse_transcript(transcript_path):
    """Parse transcript file and extract recent assistant messages"""
    try:
        transcript_file = Path(transcript_path)
        if not transcript_file.exists():
            return []  # File not found, exit silently

        assistant_messages = []
        
        with transcript_file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                try:
                    data = json.loads(line)
                    if data.get("role") == "assistant":
                        assistant_messages.append(data)
                except json.JSONDecodeError:
                    continue  # Skip invalid JSON
        
        # Return last 5 messages for analysis
        return assistant_messages[-5:]
        
    except Exception:
        return []  # Fail silently


def check_dismissive_patterns(messages):
    """Check if messages contain dismissive patterns"""
    compiled_patterns = [re.compile(p, re.IGNORECASE) for p in TRIGGERING_PATTERNS]
    
    for message in messages:
        if message.get("type") != "assistant":
            continue
            
        content = message.get("message", {}).get("content", [])
        if not isinstance(content, list) or not content:
            continue
            
        text_content = content[0]
        if text_content.get("type") != "text" or not text_content.get("text"):
            continue
        
        # Check first 80 characters for performance
        text = text_content["text"][:80]
        
        for pattern in compiled_patterns:
            if pattern.search(text):
                return True
    
    return False


def main():
    """Main function for Claude Code hook"""
    try:
        # Read JSON input from stdin
        stdin_content = read_stdin()
        if not stdin_content:
            sys.exit(0)
        
        # Parse input
        try:
            input_data = json.loads(stdin_content)
        except json.JSONDecodeError:
            sys.exit(0)  # Invalid JSON, exit silently
        
        # Get transcript path
        transcript_path = input_data.get("transcript_path")
        if not transcript_path:
            sys.exit(0)  # No transcript path, exit silently
        
        # Analyze recent messages
        messages = parse_transcript(transcript_path)
        if not messages:
            sys.exit(0)  # No messages to analyze
        
        # Check for dismissive patterns
        if check_dismissive_patterns(messages):
            print(SYSTEM_REMINDER)
        
        sys.exit(0)
        
    except Exception:
        # Fail silently to avoid breaking Claude Code workflow
        sys.exit(0)


if __name__ == "__main__":
    main()