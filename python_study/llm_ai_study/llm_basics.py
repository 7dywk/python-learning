# import random
# import os
# import json
# from pydantic import BaseModel
# from openai import OpenAI
#
#
# class BookingRequest(BaseModel):
#     name: str
#     date: str
#
# booking_tool = {
#     "type": "function",
#     "function": {
#         "name": "check-availability",
#         "description": "check if it is an available date for client booking",
#         "parameters": BookingRequest.model_json_schema(),
#     }
# }
#
# def check_availability(date: str) -> bool:
#     return random.choice([True, False])
#
#
# def build_prompt(request: str) -> str:
#     return (f"You are a manager for booking, help a client to make a reservation. "
#             f"Request: {request}")
#
# def ai_call(question: str) -> None:
#     provider = os.getenv("LLM_PROVIDER", "ollama")
#     provider_config: dict[str, dict[str, str | None]] = {
#         "ollama": {
#                 "api_key": "ollama",  # any non-empty string; local server ignores it
#                 "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
#                 "model": os.getenv("OLLAMA_CHAT_MODEL", "llama3.2"),
#             },
#     }
#     config = provider_config[provider]
#     client = OpenAI(api_key=config["api_key"], base_url=config["base_url"])
#     model = config["model"]
#     messages = [
#         {"role": "user", "content": build_prompt(question)},
#         {"role": "user", "content": question}]
#     response = client.chat.completions.create(
#         model=model,
#         messages=messages,
#         tools=[booking_tool]
#     )
#     ai_message = response.choices[0].message
#     messages.append(ai_message)
#
#     if ai_message.tool_calls:
#         for tool_call in ai_message.tool_calls:
#             args = json.loads(tool_call.function.arguments)
#             result = check_availability(args["date"])
#             messages.append({
#                 "role": "tool",
#                 "tool_call_id": tool_call.id,
#                 "name": tool_call.function.name,
#                 "content": str(result),
#             })
#         final_response = client.chat.completions.create(model=model,messages=messages)
#         print("Відповідь моделі:", final_response.choices[0].message.content)
#     else:
#         print("Відповідь моделі:", ai_message.content)
#
# def main():
#     question = "Hello can I make a booking on 15th of september?"
#     ai_call(question)
#
#
# if __name__ == "__main__":
#     main()

# import re
#
# TEMPLATES: dict[str, str] = {
#     "summarise": """Summarise the following text in {{max_sentences}} sentences or fewer.
# Be concise and capture only the key points.
#
# Text:
# {{text}}""",
#
#     "classify": """Classify the sentiment of the following text as exactly one of:
# positive, negative, or neutral.
# Respond with only the label — no punctuation, no explanation.
#
# Text: {{text}}""",
#
#     # TODO: add your own template here
#     "custom": "TODO: define your own template with at least one {{placeholder}}",
# }
#
#
# pattern = r"\{\{(.*)\}\}"
# for key, template in TEMPLATES.items():
#     print(re.findall(pattern, template))

lst = ["dog", "cat", "parrot", "cow"]
for i, item in enumerate(lst):
    print(i, item)



