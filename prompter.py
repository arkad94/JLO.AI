import os
import json
import requests
import asyncio
import aiohttp
from openai import OpenAI

client = OpenAI()

# Initialize OpenAI client with your API key
api_key = os.getenv("OPENAI_API_KEY")


def create_prompt(CMD, tag, SPINS):
    cmd_templates = {
        "Word of The Day in Japanese": "Give 5 words in Japanese based on the tag given, Make sure you tabulate them as Japanese word, Furigana, English word, and example sentence in respective columns",
        "A Story": "Write a Japanese story in Japanese, with a summary in English following Japanese text separately listing difficult Japanese words used in the story in a tabulated format exactly as follows, no deviations tolerated: Japanese Word| English Translation, don't use brackets or empty space anywhere in your output",
        # Add more CMDs and their templates here
    }

    prompt_template = cmd_templates.get(CMD, "CMD not recognized. Please enter a valid CMD.")
    instructions = []

    if tag:
        instructions.append(f"Tag: {tag}")
    if SPINS.strip():
        instructions.append(f"SPINS: {SPINS.strip()}")

    instruction_str = ", ".join(instructions)
    final_prompt = f"{prompt_template} based on the following instructions: {instruction_str}." if instructions else prompt_template
    return final_prompt, CMD in cmd_templates


<<<<<<< HEAD
async def send_prompt_to_openai(CMD, tag, SPINS):
=======
def send_prompt_to_openai(CMD, tag, SPINS, stream=False):
>>>>>>> JLO.AIWebStreamA
    final_prompt, valid_cmd = create_prompt(CMD, tag, SPINS)
    if valid_cmd:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": final_prompt}],
            "stream": stream  # Enable streaming if required
        }

        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data) as response:
                if response.status == 200:
                    response_data = await response.json()
                    text_response = response_data['choices'][0]['message']['content'].strip()
                    difficult_words = extract_difficult_words(text_response)
                    return text_response, difficult_words
                else:
                    print("Error:", response.status, await response.text())
                    return "", []

<<<<<<< HEAD
# Example use
# asyncio.run(send_prompt_to_openai("Word of The Day in Japanese", "", ""))
=======
        if response.status_code == 200:
            if not stream:
                # For non-streaming responses
                response_data = response.json()
                text_response = response_data['choices'][0]['message']['content'].strip()
                difficult_words = extract_difficult_words(text_response)
                return text_response, difficult_words
            else:
                # Handling for streamed responses
                try:
                    for line in response.iter_lines():
                        if line:
                            line_str = line.decode('utf-8').strip()
                            print("Received line:", line_str)  # Debugging statement
                            # Check if the line starts with 'data: '
                            if line_str.startswith('data: '):
                                json_str = line_str[6:]  # Strip off 'data: ' to get the JSON part
                                try:
                                    streamed_response = json.loads(json_str)
                                    if 'choices' in streamed_response and 'delta' in streamed_response['choices'][0]:
                                        delta_content = streamed_response['choices'][0]['delta'].get('content', '')
                                        yield delta_content  # Yield the chunk for streaming
                                except json.JSONDecodeError as e:
                                    print("Error in decoding JSON after stripping 'data: ':", e)
                            else:
                                print("Line did not start with 'data: '", line_str)
                except json.JSONDecodeError as e:
                    print("JSON decoding failed. The line received was not valid JSON:", line_str)
                    print("Error message:", str(e))
        else:
            print("Error:", response.status_code, response.text)
            return "", []

    return "", []
>>>>>>> JLO.AIWebStreamA





def extract_difficult_words(response):
    difficult_words = []
    for line in response.split('\n'):
        if '|' in line:  # Adjusted to match the new delimiter
            parts = line.strip().split('|')
            if len(parts) == 2:
                japanese, english = parts
                difficult_words.append((japanese.strip(), english.strip()))
    return difficult_words