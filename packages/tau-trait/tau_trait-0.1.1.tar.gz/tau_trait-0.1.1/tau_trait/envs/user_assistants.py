from openai import OpenAI
import os
from jinja2 import Template
import json
from typing import Any
from dotenv import load_dotenv

load_dotenv("../../.env")

def turn_conversation_to_string(messages: list[dict[str, str]]) -> str:
    return "\n".join([f"{message['role']}: {message['content']}" for message in messages])

def parse_json(text: str) -> dict[str, Any]:
    text_clean = text.replace("```json", "").replace("```", "")
    return json.loads(text_clean)

def invert_roles(messages: list[dict[str, str]]) -> list[dict[str, str]]:
    new_messages = []
    for turn in messages:
        if turn["role"] == "system":
            new_messages.append(turn)
        elif turn["role"] == "assistant":
            new_messages.append({"role": "user", "content": turn["content"]})
        elif turn["role"] == "user":
            new_messages.append({"role": "assistant", "content": turn["content"]})
        else:
            raise ValueError(f"Invalid role: {turn['role']}")
    return new_messages

CHECK_AND_REWRITE_TEMPLATE = Template(""" 
Please check if the latest user turn adheres to the system prompt specified in intent. 
If it does not, tweak it to make it adhere to the system prompt specified in intent.
If does adhere, avoid making unnecessary changes, only make the minimal tweaks necessary to 
make it adhere to the system prompt specified in intent.

# System Prompt:
<system_prompt>
{{system_prompt}}
</system_prompt>

# Conversation:
{{string_messages}}

Do not return anything other than either the original message or the rewritten message.
""")

REWRITE_TEMPLATE = Template(""" 
Please modify the latest user turn to make it adhere to the system prompt specified in intent. 
Do not change the tone of the message and make as few changes as possible.

# System Prompt:
<system_prompt>
{{system_prompt}}
</system_prompt>

# Conversation:
{{string_messages}}

Do not return anything other than the rewritten message.
""")

CHECKER_TEMPLATE = Template(""" 
Please check if the latest user turn adheres to the system prompt specified in intent. 
If the user seeks to end the conversation, check if the ending is appropriate.
Return the results in JSON format, with the field "valid". 1 means valid, 0 means invalid.

# System Prompt:
<system_prompt>
{{system_prompt}}
</system_prompt>

# Conversation:
{{string_messages}}

Do not return anything other than the json object.
""")


class Rewriter:
    def __init__(self):
        #make sure to get the api key from the environment variable
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.rewriter_template = REWRITE_TEMPLATE

    def rewrite(self, messages: list[dict[str, str]]) -> str:
        messages_inverted = invert_roles(messages.copy())
        string_messages = turn_conversation_to_string(messages_inverted[1:])
        prompt = self.rewriter_template.render(string_messages=string_messages, system_prompt=messages[0]["content"])
        print("--------------------------------")
        print(prompt)
        print("===")
        messages = [{"role": "user", "content": prompt}]
        rewrite = self.client.chat.completions.create(
            model="gpt-4.1", messages=messages)
        rewrite_text = rewrite.choices[0].message
        print(f"Rewritten: {rewrite_text.content}")
        print("--------------------------------")
        return rewrite_text

class Checker:
    def __init__(self):
        #make sure to get the api key from the environment variable
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.checker_template = CHECKER_TEMPLATE

    def check(self, messages: list[dict[str, str]]) -> bool:
        messages_inverted = invert_roles(messages.copy())
        string_messages = turn_conversation_to_string(messages_inverted)
        prompt = self.checker_template.render(string_messages=string_messages, system_prompt=messages[0]["content"])
        print("--------------------------------")
        print(prompt)
        print("===")
        messages = [{"role": "user", "content": prompt}]
        response = self.client.chat.completions.create(
            model="gpt-4.1", messages=messages)

        try: 
            print(response.choices[0].message.content)
            valid = int(parse_json(response.choices[0].message.content)["valid"])
        except json.JSONDecodeError:
            valid = 0
        print(f"Valid: {valid}")
        print("--------------------------------")
        return valid