import os
import json
import requests
import re
from openai import OpenAI

client = OpenAI()

# Initialize OpenAI client with your API key
api_key = os.getenv("OPENAI_API_KEY")


def create_prompt(CMD, tag, SPINS):
    cmd_templates = {
        "Word of The Day in Japanese": "Give 5 words in Japanese based on the tag given, Make sure you tabulate them as Japanese word, Furigana, English word, and example sentence in respective columns",
        "A Story": "Write a story in japanese length of which is between 3000-4000 characters, followed with a summary in English and in the end give a list of difficult words. Japanese Story has heading as title, the english summary which follows the Japanese story has title English Summary, and the difficult words are under the header difficult words as (日本語（ふりがな・English Meaning) make sure difficult words are numbered, Make sure the format is exactly as on this prompt any devation from the format would be harmful",
        # Add more CMDs and their templates here
    }

    prompt_template = cmd_templates.get(CMD, "CMD not recognized. Please enter a valid CMD, Please refer to the table above and enter exact CMD case sensitive..")
    instructions = []

    if tag:
        instructions.append(f"Tag: {tag}")
    if SPINS.strip():
        instructions.append(f"SPINS: {SPINS.strip()}")

    instruction_str = ", ".join(instructions)
    final_prompt = f"{prompt_template} based on the following instructions: {instruction_str}." if instructions else prompt_template
    return final_prompt, CMD in cmd_templates
    

def generate_image_with_dalle(story):
    # Initialize OpenAI client
    client = OpenAI()

    # Truncate the story to the first 4000 characters
    truncated_story = story[:4000]

    # Prepare the prompt for DALL-E
    dalle_prompt = "Generate an image based on: " + truncated_story

    # Make the API request to DALL-E
    response = client.images.generate(
        model="dall-e-3",
        prompt=dalle_prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )

    # Check if the response contains the image data
    if response.data and len(response.data) > 0:
        image_url = response.data[0].url
        return image_url
    else:
        print(f"Error in image generation: {response.error}")
        return ""



def process_text(text):
    # Regular expression patterns to extract Japanese and English text
    japanese_pattern = r'[\u3000-\u303F\u3040-\u309F\u30A0-\u30FF\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]+'
    english_pattern = r'[A-Za-z0-9\s,.;\'"-]+'
    
    # Extract Japanese and English text
    japanese_story = ' '.join(re.findall(japanese_pattern, text))
    english_summary = ' '.join(re.findall(english_pattern, text))

    return japanese_story, english_summary

def extract_difficult_words(text):
    # Initialize an empty list to store formatted difficult words
    formatted_difficult_words = []

    # Find the difficult words section
    start_index = text.find('Difficult Words')
    if start_index != -1:
        # Slice the text from the start of the difficult words section to the end
        difficult_words_text = text[start_index:]
        
        # Use a regex to find all instances of the difficult word pattern
        difficult_words_pattern = re.compile(
    r'\n?(\d+)\.\s*([\u3000-\u303F\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]+)\s*（([^）]*)）?\s*・\s*([^\n]+)'
)


        matches = difficult_words_pattern.findall(difficult_words_text)
        
        for match in matches:
            # Each 'match' is a tuple with the following structure: (number, Japanese word, reading, English translation)
            formatted_difficult_words.append({
                'japanese': match[1].strip(), 
                'reading': match[2].strip(), 
                'english': match[3].strip()
            })
    print("Extracted Difficult Words:", formatted_difficult_words)
    return formatted_difficult_words

    
    



def send_prompt_to_openai(CMD, tag, SPINS):
    final_prompt, valid_cmd = create_prompt(CMD, tag, SPINS)
    if valid_cmd:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": final_prompt}]
        }
        response = requests.post("https://api.openai.com/v1/chat/completions", 
                                 headers=headers, 
                                 data=json.dumps(data))
        if response.status_code == 200:
            response_data = response.json()
            text_response = response_data['choices'][0]['message']['content'].strip()
            return text_response
        else:
            print("Error:", response.status_code, response.text)
            return ""

    return ""



