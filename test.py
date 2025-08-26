#!/usr/bin/env python3

"""
Simple test for you_are_not_right.py
"""

import re

# Import the patterns from the main script
TRIGGERING_PATTERNS = [
    r"you\s+(are\s+)?(right|correct)",
    r"absolutely\s+(right|correct)?",
    r"you'?re\s+(absolutely\s+)?(right|correct)",
    r"that'?s\s+(absolutely\s+)?(right|correct)",
    r"exactly\s+(right|correct)?",
    r"spot\s+on",
    r"good\s+point",
    r"valid\s+point",
    r"你\s+(是\s+)?(对的|正确的|没错)",
    r"完全\s+(正确|没错)",
    r"确实\s+(如此|这样)",
    r"说得\s+(对|不错)",
    r"你说的\s+(对|没错)",
    r"사용자가.*맞다",
    r"맞습니다",
    r"정확합니다",
    r"その通りです",
    r"正しいです", 
    r"そうですね",
]

def test_patterns():
    """Test that patterns correctly detect dismissive phrases"""
    compiled_patterns = [re.compile(p, re.IGNORECASE) for p in TRIGGERING_PATTERNS]
    
    # Test cases that should be detected
    should_detect = [
        "You are absolutely right!",
        "That's correct, great point.",
        "You're right about that.",
        "Absolutely right!",
        "Good point there.",
        "你是对的",
        "완全 정확합니다",
        "その通りです",
    ]
    
    # Test cases that should NOT be detected  
    should_not_detect = [
        "That approach has merit, but consider the edge case...",
        "The implementation looks solid, however...",
        "While that solves the immediate issue...",
        "That's a valid approach. Let me also suggest...",
        "I understand your reasoning. Another consideration is...",
    ]
    
    print("Testing dismissive pattern detection...")
    
    # Test positive cases
    for text in should_detect:
        detected = any(pattern.search(text) for pattern in compiled_patterns)
        status = "✅" if detected else "❌"
        print(f"{status} '{text}' -> {'DETECTED' if detected else 'NOT DETECTED'}")
    
    print()
    
    # Test negative cases
    for text in should_not_detect:
        detected = any(pattern.search(text) for pattern in compiled_patterns)
        status = "✅" if not detected else "❌"
        print(f"{status} '{text}' -> {'NOT DETECTED' if not detected else 'DETECTED'}")
    
    print("\nTest complete!")


if __name__ == "__main__":
    test_patterns()