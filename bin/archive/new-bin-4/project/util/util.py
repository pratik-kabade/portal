import os
import json

'''
def authenticate(user, password):

    try:
       response = DBUtil.getDocumentByKeyValue(os.getenv("MONGODB_NAME"), "users", "username", user)
       _password = response[0].get("password")
       if password == _password:
           return True
       else:
           false
    except Exception as e:
         print(e)
         raise e

authenticate("anurag", "anurag")
'''

def text_to_json(text):
  """
  Converts input text to a JSON with an array of test cases.

  Args:
      text: The input text string with test cases.

  Returns:
      A JSON string representing the data.
  """
  # Split the text into lines
  lines = text.splitlines()

  # Initialize an empty list for test cases
  test_cases = []

  # Loop through lines, building test case objects
  current_test_case = ""
  for line in lines:
    if line.startswith("Testcase-"):
      # New test case detected, add previous one if it exists
      if current_test_case.strip():
        test_cases.append(current_test_case.strip())
      current_test_case = line + "\n"
    else:
      # Append line to current test case
      if line.strip():
        current_test_case += line + "\n"

  # Add the last test case if it exists
  if current_test_case.strip():
    test_cases.append(current_test_case.strip())

  # Build the JSON object
  #data = {"Test cases": test_cases}
  data = test_cases

  # Convert the data to JSON string
  json_string = json.dumps(data, indent=4)  # Add indentation for readability

  return json_string

# Sample input text
text = """

Testcase-01:
Preconditions:
1. User is logged in as a system admin
2. Anurag's account exists in Octobox CPE
Test Steps:
1. Navigate to the user management section
2. Locate Anurag's account and click on it
3. Click on the "Configure" button
Expected Output:
1. The "Configure" page for Anurag's account is displayed
 
Testcase-02:
Preconditions:
1. User is logged in as a system admin
2. Anurag's account does not exist in Octobox CPE
Test Steps:
1. Navigate to the user management section
2. Click on "Add New User" button
3. Enter Anurag's details and click on "Save"
4. Locate the newly created account and click on it
5. Click on the "Configure" button
Expected Output:
1. The "Configure" page for Anurag's new account is displayed"""

# Convert text to JSON
#json_data = text_to_json(text)

# Print the JSON string
#print(json_data)


def load_env_from_txt(file_path): 
    with open(file_path) as f: 
        for line in f:
             if line.strip() and not line.startswith('#'):
                 key, value = line.strip().split('=', 1)
                 os.environ[key] = value

load_env_from_txt('./cfg/config.txt')
