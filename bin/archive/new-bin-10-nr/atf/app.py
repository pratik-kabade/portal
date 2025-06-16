from llm import LLM
import os
from util import get_llm_base_scripts, extract_number

GENERATED_FILE = 'bin/generated_file.txt'

# MOVE THIS
def convert_to_steps(text):
    steps = text.split(", ")
    return ", ".join([f"step_{i}" for i in range(len(steps))])


def generate_test_cases(test_case_string):
    """Generates test cases using an LLM instance and saves the result to a file."""

    # Initialize LLM instance
    llm_instance = LLM(llm_model='llama2', debug_mode=False)

    # Retrieve necessary data from scripts
    base_scripts = get_llm_base_scripts()
    script_dict = base_scripts.get('entire_dict', {})
    question_names = base_scripts.get('names', {})
    script_header = base_scripts.get('script_header', '')
    script_footer = base_scripts.get('script_footer', '')

    # [HARDCODE] Replacements
    script_header = script_header.replace('SCRIPT_NAME', 'AI GENERATED SCRIPT')
    script_header = script_header.replace('TEST_STEPS', test_case_string)
    script_header = script_header.replace('APP_NAME', 'ai-dev')
    script_header = script_header.replace('APP_NAME', 'ai-dev')
    script_footer = script_footer.replace('LIST_OF_STEPS', convert_to_steps(test_case_string))
    

    # Split input test cases string into a list
    test_cases = [test_case.strip() for test_case in test_case_string.split(',')]

    key_sequence = []
    for test_case in test_cases:
        query = f"""
Given the following dictionary:
{question_names}
I want to find the key corresponding to the value that best matches the input: "{test_case}". 

Respond in the format: "key:#" where "#" is the single key number. Do not include any other text or explanation.
And if there is no best match dont forcefully match it, keep the value as 999
"""

        response = llm_instance.fetch_entire_response(query)
        key = extract_number(response)
        key_sequence.append(key)

    print('key_sequence', key_sequence)

    # Build the content for the output file
    final_content = [script_header]
    for step_index, key in enumerate(key_sequence):
        final_content.append(f'def step_{step_index}():')
        if key in script_dict:
            final_content.append(script_dict[key].get('content', ''))
        # else:
    final_content.append(script_footer)

    # Write to file with error handling
    try:
        os.makedirs(os.path.dirname(GENERATED_FILE), exist_ok=True)
        with open(GENERATED_FILE, 'w') as file:
            file.write("\n".join(final_content))
    except IOError as e:
        print(f"Error writing to file: {e}")
        return ""

    return "\n".join(final_content)



if __name__ == '__main__':
    # test_case_string = 'replay captured alarms, set the captured condition, Free m, replay captured alarms'
    test_case_string = 'Open the Event Viewer, Replay the Captured alarms'
    generate_test_cases(test_case_string)
