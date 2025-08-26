# AI Assistant Accountability

A simple hook to prevent AI assistants from giving dismissive "you are right" responses. Encourages substantive technical analysis instead of reflexive agreement.

> 💡 **Inspired by**: This project is forked and enhanced from [ljw1004's original concept](https://gist.github.com/ljw1004/34b58090c16ee6d5e6f13fce07463a31)

## Quick Start

1. **Download the script:**
   ```bash
   curl -O https://raw.githubusercontent.com/DrayChou/ai-assistant-accountability/main/you_are_not_right.py
   ```

2. **Use as Claude Code hook:**
   Set up a hook that runs: `python you_are_not_right.py`

## What it does

Detects phrases like:
- "You are absolutely right!"
- "That's correct!"  
- "你是对的" (Chinese)
- "맞습니다" (Korean)
- "正しいです" (Japanese)

When found, it reminds the AI to provide detailed technical analysis instead.

## Example

**❌ Bad:**
> "You are absolutely right about that!"

**✅ Good:**  
> "That addresses the immediate crash risk. However, consider empty strings would still pass through unchecked. A more robust approach might be validating input ranges."

## Requirements

- Python 3.6+
- No external dependencies

## Credits

This project is inspired by and enhanced from the original work by [ljw1004](https://gist.github.com/ljw1004/34b58090c16ee6d5e6f13fce07463a31).

**Enhancements added:**
- Multi-language support (Chinese, Korean, Japanese)
- Cross-platform compatibility improvements
- Enhanced error handling and robustness
- Cleaner code structure and documentation

## License

MIT - Single file, simple tool for better AI interactions.