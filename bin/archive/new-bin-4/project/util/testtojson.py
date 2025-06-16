import json

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
  tcDone = 0
  tcNotStarted = 1
  for line in lines:
    #print(line)
    if "START OF TEST" in line.strip():
        tcNotStarted = 0
        continue
    if tcNotStarted == 1:
        continue
    if "END OF TEST CASES" in line.strip():
        tcDone = 1
        continue
    if tcDone == 1:
        continue
    if "Testcases" in line.strip():
        continue
    if line.strip().startswith("Testcase-"):
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
  #print (json_string)

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

testcase = """
Hello there, how are you....
###FORMAT###

 ####START OF TESTCASES###
 Testcase-01: Configure SSID Profile for Employee using GUI
 Precondition:
 1. The user is logged in as a system admin.
 2. The Aruba Instant AP has been configured with the required software version (12.0).
 3. The employee's WLAN profile does not already exist.

                      Test Steps:
 1. Log in to the WebUI of the Aruba Instant AP as a system admin.
 2. Navigate to Configuration > Wireless > SSID Profiles.
 3. Click + next to "SSID Profiles" and enter a name for the new profile (e.g., "Employee").
 4. Set the SSID to "anurag".
 5. Select the band as "5Ghz".
 6. Save the changes.

                        Expected Output:
 1. The new employee WLAN profile is created with the specified settings.
 2. The SSID "anurag" is set for the employee profile.

 Testcase-02: Configure SSID Profile for Employee using CLI
 Precondition:
 1. The user is logged in as a system admin.
 2. The Aruba Instant AP has been configured with the required software version (12.0).
 3. The employee's WLAN profile does not already exist.

                      Test Steps:
 1. Log in to the CLI of the Aruba Instant AP as a system admin.
 2. Enter the command `(Instant AP)(config)# wlan ssid-profile anurag` and press Enter.
 3. Set the band to "5Ghz" using the command `(Instant AP)(config)# wlan ssid-profile anurag 5Ghz`.
 4. Save the changes.

                        Expected Output:
 1. The new employee WLAN profile is created with the specified settings.
 2. The SSID "anurag" is set for the employee profile.

 ####END OF TEST CASES###

"""
#json_data = text_to_json(testcase)

# Print the JSON string
#print (json_data)
#
