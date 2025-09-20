from optimizer import optimize_prompt

draft = "I want to generate a structured planning for a formation on GenAI with an adaptated communication for enrolled members."
user_input = None
llm_output = None

optimized = optimize_prompt(draft, user_input, llm_output)

print("\n--- Optimized Prompt ---\n")
print(optimized)
