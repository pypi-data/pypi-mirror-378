# 🧠 leo-prompt-optimizer

**leo-prompt-optimizer** is a Python library that helps developers **optimize raw prompt drafts** into structured, high-performance prompts for large language models (LLMs).

It leverages **open-source models via [Groq API](https://console.groq.com/)** (like LLaMA 3 or Mixtral), making it fast, affordable, and production-ready.

---

## 🚀 Features

- 🛠️ Refines messy or vague prompts into structured, effective ones
- 🧠 Follows a 9-step prompt engineering framework
- 📦 Supports contextual optimization (with user input & LLM output)
- ⚡ Uses blazing-fast open-source LLMs via Groq
- 🔐 Secure API key handling with `.env`

---

## 📦 Installation

```bash
pip install leo-prompt-optimizer
````

---

## 🔧 Setup

1. Create a `.env` file at the root of your project:

```env
GROQ_API_KEY=your_groq_api_key_here
```

2. Install dependencies:

```bash
pip install leo-prompt-optimizer
```

---

## ✍️ Usage Example

```python
from leo_prompt_optimizer.optimizer import optimize_prompt

draft = "I want to understand user feedback better. Can you help me ask the right questions?"

user_input = "Users say the interface feels confusing. I want to understand what they mean exactly."

llm_output = "You could ask: 'Which parts feel confusing?' or 'How could it be more intuitive?'"

optimized = optimize_prompt(draft, user_input, llm_output)

print(optimized)
```

---

## 📘 Output Format

The optimized prompt follows a structured format like:

```text
Role:
[Define the LLM's persona]

Task:
[Clearly state the specific objective]

Instructions:
* Step-by-step subtasks

Context:
[Any relevant background, constraints, domain]

Output Format:
[e.g., bullet list, JSON, summary]

User Input:
[Original user input or example]
```

---

## 💡 Why Use It?

Prompt quality is critical when building with LLMs.
**leo-prompt-optimizer** helps you:

* Make prompts explicit and usable across apps
* Reduce hallucination
* Increase repeatability and reliability

---

## 📄 License

MIT © 2025 \[Leonard Baesen]

````
