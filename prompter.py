import os



def create_prompt(CMD, tag, SPINS):
    cmd_templates = {
        "Word of The Day in Japanese": "Template for command 1",
        "A Story": "Template for command 2",
        # Add more CMDs and their templates here
    }
    prompt_template = cmd_templates.get(CMD, "Default template if CMD not found")
    final_prompt = f"{prompt_template} with Tag: {tag} and Additional Instructions: {SPINS}"
    return final_prompt


class MockOpenAIClient:
    def chat(self):
        return self

    def completions(self):
        return self

    def create_prompt(self, messages, model):
        # Define mock responses here
        mock_responses = {
            "Word of The Day in Japanese": "Mock response for Word of The Day in Japanese",
            "A Story": "Mock response for A Story"
        }
        prompt = messages[0]["content"]
        for key, value in mock_responses.items():
            if key in prompt:
                return {'choices': [{'message': {'content': value}}]}
        return {'choices': [{'message': {'content': "Default mock response"}}]}

# Rest of your script remains as is. 
# Just ensure that you use the 'create' method of MockOpenAIClient in your CLI script 
# when generating mock responses.

#With this change, when you call create_prompt with "A Story", it will match the key 