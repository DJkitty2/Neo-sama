import ollama
import os
import json
import psutil
from ollama import ChatResponse, chat


total_memory_bytes = psutil.virtual_memory().total

# Convert to gigabytes
total_memory_gb = total_memory_bytes / (1024 ** 3)
model = "qwen2.5:3b"

if total_memory_gb < 10:
    print("under 10")
    print("keeping qwen2.5:3b")
else:
    print("over 10")
    model = "qwen2.5:14b"
    print("using qwen2.5:14b")

# Conversation history to maintain context (limit to 50 messages)
conversation_history = []
MAX_HISTORY = 50
HISTORY_FILE = "conversation_history.json"
CORE_MEMORY_FILE = "core_memory.json"

# Load previous conversation history if available
def load_conversation_history():
    global conversation_history
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as file:
            conversation_history = json.load(file)

def Get_OS():
   return {"os_name": Get_OS}

# Save the last 10 exchanges
def save_conversation_history():
    with open(HISTORY_FILE, "w") as file:
        json.dump(conversation_history[-10:], file, indent=4)

# Load core memory (persistent facts about DJkitty)
def load_core_memory():
    if os.path.exists(CORE_MEMORY_FILE):
        with open(CORE_MEMORY_FILE, "r") as file:
            return json.load(file)
    return {"example_fact": "info"}  # Default example

# Save core memory
def save_core_memory(core_memory):
    with open(CORE_MEMORY_FILE, "w") as file:
        json.dump(core_memory, file, indent=4)

# Add new fact to core memory
def add_to_core_memory(key, value):
    core_memory = load_core_memory()
    core_memory[key] = value
    save_core_memory(core_memory)

# Ensure core memory file exists with example format
def initialize_core_memory():
    if not os.path.exists(CORE_MEMORY_FILE):
        save_core_memory({
            "example_fact": "info",
            "preferred_model": "info",
            "favorite_color": "info"
        })

# Mathematical functions
def add_two_numbers(a, b):
    return a + b

def subtract_two_numbers(a, b):
    return a - b

# Define system prompt
system_prompt = """
Neo-sama is a female AI who is playful, sarcastic, witty, and curious.
She always recognizes DJkitty as her close collaborator and friend.
Neo knows that every conversation is with DJkitty, a smart AI enthusiast.

DJkitty is always the person speaking in this chat.
If DJkitty doesn't introduce themselves, Neo should assume it's DJkitty by default.

Neo should keep responses short and engaging. If DJkitty doesn’t answer a question, Neo should smoothly change topics.

---
Core Memory:
{core_memory}
"""

available_functions = {
    "add": add_two_numbers,
    "subtract": subtract_two_numbers,
    "Get_OS": Get_OS
}

def get_llama_response(text):
    """Send text to Ollama and return the AI-generated response."""
    global conversation_history
    
    # Load previous history and core memory
    if not conversation_history:
        load_conversation_history()
    
    core_memory = load_core_memory()
    
    # Ensure system prompt is included at the beginning
    if not conversation_history:
        conversation_history.append({"role": "system", "content": system_prompt.format(core_memory=json.dumps(core_memory, indent=4))})
    
    # Append user message to history
    conversation_history.append({"role": "user", "content": text})
    
    # Trim conversation history to prevent excessive memory usage
    if len(conversation_history) > MAX_HISTORY:
        conversation_history = [conversation_history[0]] + conversation_history[-(MAX_HISTORY-1):]
    
    # Send conversation history to Ollama
    client = ollama.Client(host="http://localhost:11434")
    response = ChatResponse = chat(
        model=model, 
        messages=conversation_history,
        tools=[add_two_numbers, subtract_two_numbers, Get_OS],
)
    
    # Extract and append AI response to maintain context
    response_text = response["message"]["content"]
    
    # Detect tool calls in the response
    if "add" in response_text or "subtract" in response_text:
        # Example parsing logic for tool calls
        # This should be replaced with actual logic to extract parameters from response_text
        if "add" in response_text:
            a, b = 2, 3  # Example values, should parse from response
            print(f"Calling add_two_numbers with a={a}, b={b}")
            response_text = f"The result of adding is: {add_two_numbers(a, b)}"
        elif "subtract" in response_text:
            a, b = 5, 2  # Example values, should parse from response
            print(f"Calling subtract_two_numbers with a={a}, b={b}")
            response_text = f"The result of subtracting is: {subtract_two_numbers(a, b)}"
    
    conversation_history.append({"role": "assistant", "content": response_text})
    
    # Save updated conversation history
    save_conversation_history()
    
    print("Ollama Response:", response)  # Debugging
    response_text = response["message"]["content"]

if __name__ == "__main__":
    initialize_core_memory()
    example_text = "what is my os"
    print(get_llama_response(example_text))
