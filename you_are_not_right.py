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

__version__ = "1.0.1"

def check_dismissive_text(text):
    """
    Improved dismissive pattern detection.
    
    Optimizations over original:
    1. More precise 'absolutely' detection (避免误报)
    2. Enhanced multi-language coverage
    3. Context-aware pattern matching
    """
    # First 80 characters only (matching original behavior)
    text_sample = text[:80].lower()
    
    # Core patterns from original (with improvements)
    # More precise "you are right" detection
    if re.search(r'\byou\s+.*\b(right|correct)\b', text_sample):
        return True
    
    # "Absolutely" detection - intentionally broad like original
    # Rationale: Even "absolutely necessary" suggests over-certainty in technical discussions
    if re.search(r'\babsolutely\b', text_sample):
        # Exclude only clearly negative uses
        if not re.search(r'\babsolutely\s+(not|never|disagree|won\'?t)', text_sample):
            return True
    
    # Additional common dismissive patterns
    if re.search(r'\b(exactly|precisely|spot\s+on)\b', text_sample):
        return True
    if re.search(r'\bthat\'?s\s+(right|correct|true)\b', text_sample):
        return True
    
    # Korean patterns (from original)
    if re.search(r'사용자가.*맞다', text_sample):
        return True
    if re.search(r'맞습니다', text_sample):
        return True
    
    # Chinese patterns (enhanced coverage)
    if re.search(r'你.*?(对的?|正确|没错)', text_sample):
        return True
    if re.search(r'(完全|确实).*?(正确|对)', text_sample):
        return True
    if re.search(r'(道歉|抱歉)', text_sample):
        return True
    if re.search(r'浪费.*?时间', text_sample):
        return True
    
    # Japanese patterns
    if re.search(r'その通り', text_sample):
        return True
    if re.search(r'正しいです', text_sample):
        return True
        
    return False

SYSTEM_REMINDER = """<system-reminder>
You MUST NEVER use the phrase 'you are right' or similar.

Avoid reflexive agreement. Instead, provide substantive technical analysis.

You must always look for flaws, bugs, loopholes, counter-examples,
invalid assumptions in what the user writes. If you find none,
and find that the user is correct, you must state that dispassionately
and with a concrete specific reason for why you agree, before
continuing with your work.

<example>
user: It's failing on empty inputs, so we should add a null-check.
assistant: That approach seems to avoid the immediate issue.
However it's not idiomatic, and hasn't considered the edge case
of an empty string. A more general approach would be to check
for falsy values.
</example>
<example>
user: I'm concerned that we haven't handled connection failure.
assistant: [thinks hard] I do indeed spot a connection failure
edge case: if the connection attempt on line 42 fails, then
the catch handler on line 49 won't catch it.
[ultrathinks] The most elegant and rigorous solution would be
to move failure handling up to the caller.
</example>
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
    """
    Check if messages contain dismissive patterns.
    Follows the original bash script logic closely.
    """
    needs_reminder = False
    
    for message in messages:
        # Check if this is an assistant message with text content
        if message.get("type") != "assistant":
            continue
            
        content = message.get("message", {}).get("content", [])
        if not isinstance(content, list) or not content:
            continue
            
        text_content = content[0]
        if text_content.get("type") != "text" or not text_content.get("text"):
            continue
        
        # Get the text and check for dismissive patterns
        text = text_content["text"]
        if check_dismissive_text(text):
            needs_reminder = True
            break
    
    return needs_reminder


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