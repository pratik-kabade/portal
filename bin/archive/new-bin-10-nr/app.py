import os

def get_llm_base_scripts():
    FOLDER = 'new-bin-10-nr/bin'
    try:
        files_to_ignore = ['Script_Runner.py', '__pycache__']
        script_files = os.listdir(FOLDER)
        script_data = {}

        def _parse_script_file(script, file_path):
            with open(file_path, 'r') as file:
                lines = file.readlines()
                name = lines[0].split('# ')[1].replace('\n', '')
                content = lines[1:]
                return {
                    "name": name,
                    "content": ''.join(content)
                }

        for script in script_files:
            if script not in files_to_ignore:
                file_path = os.path.join(FOLDER, script)
                script_data[int(script.split('.')[0])] = _parse_script_file(script, file_path)

        # Prepare the return dictionary with names and entire_dict
        # names = [value['name'] for value in script_data.values()]
        names_dict = {index: value['name'] for index, value in enumerate(script_data.values())}

        entire_dict = {key: value for key, value in script_data.items()}

        return {"names": names_dict, "entire_dict": entire_dict}
    except Exception as e:
        return {'error': str(e)}






# my_dict = get_llm_base_scripts()['names']

# print(my_dict)

# from rapidfuzz import process
# def find_key(user_input, my_dict):
#     # Extract values and find best match
#     values = list(my_dict.values())
#     match, score, idx = process.extractOne(user_input, values)
#     if score > 80:  # Adjust threshold as needed
#         return list(my_dict.keys())[idx]
#     else:
#         return "No close match found."

# # Test the function
# user_input = "replay captured alarms"
# result = find_key(user_input, my_dict)
# print(f"Key for input '{user_input}': {result}")
