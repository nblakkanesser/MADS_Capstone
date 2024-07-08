import subprocess
import sys

# Use sys.executable to ensure the script runs in the current Python environment
subprocess.run([sys.executable, "-m", "chainlit", "run", "chatbot.py", "-w", "--port", "8000"])