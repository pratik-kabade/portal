python -m venv venv
source venv/bin/activate
deactivate


sudo apt update
sudo apt install python3.11

curl -X POST -H "Content-Type: application/json" -d '{"question" : "As a system admin, I shall be able to fetch value of parameter Device.X_CISCO_COM_DeviceControl.SSHEnable using dmcli command", "user" : "admin", "project" : "10391", "userstory_id" : "4333716"}' http://localhost:3000/api/ask/tm/testcases
 






    combined_prompt = f"""
    Step 1: Retrieve the project name using projectID: {projectID}.
    - Store this result as 'projectname'.
    - Return the 'projectname'.

    Step 2: Create or update the user story for the project:
    - Use the following details:
    * projectID: {projectID}
    * projectname: (use the 'projectname' from Step 1)
    * question: {question}
    * createdBy: {createdBy}
    - Return the 'userstory_id' after creating or updating the user story.

    Step 3: Generate the main prompt for querying test cases:
    - Use the following:
    * userstory_id: (from Step 2)
    * question: {question}
    - Return the generated 'mainPrompt'.

    Step 4: Query the test cases:
    - Use the following:
    * projectname: (from Step 1)
    * mainPrompt: (from Step 3)
    - Return the 'tc_result' after querying the test cases.

    Step 5: Process and save the test case results:
    - Use the following:
    * projectID: {projectID}
    * userstory_id: (from Step 2)
    * createdBy: {createdBy}
    * tc_result: (from Step 4)
    
    - Return the saved test cases in a JSON format.
    """



    # Step 1: Retrieve the project name
    projectname = read_db(projectID)
    # Step 2: Create or update the user story in the database
    new_userstory = create_db(userstory_id, projectID, projectname, question, createdBy)
    # Step 3: Create the prompt for the language model
    mainPrompt = create_prompt(question)
    # Step 4: Generate the response from the language model
    tc_result = llm_resp(projectname, mainPrompt)
    # Step 5: Convert the response to JSON and store it in the database
    response_json = return_json(tc_result, projectID, userstory_id, new_userstory, createdBy)





    combined_prompt = f"""
    1. Retrieve the project name using projectID: {projectID}. Store this result as `projectname` and return it
    2. Create or update the user story for projectID: {projectID}, with projectname based on the previous step, question: {question}, and createdBy: {createdBy}
    3. Generate the main prompt for querying test cases based on the user story for question: {question}
    4. Query test cases for the project and main prompt generated
    5. Process and save the test case results, with projectID: {projectID}, userstory_id: {userstory_id}, and createdBy: {createdBy}
    """




    combined_prompt = f'Retrieve the project name using projectID: {projectID}'
    Use agent.chat only once to perform all tasks
    response = agent.chat(combined_prompt)







        Please perform the following steps:

        1. Retrieve the project name from the database using the provided project ID.
        2. Create or update the user story in the database with the given details.
        3. Create a prompt for the language model using the user story question.
        4. Generate a response from the language model based on the project name and the created prompt.
        5. Convert the response to JSON format and store it in the database.

        Here are the details:

        - Question: {question}
        - Created By: {createdBy}
        - Project ID: {projectID}
        - User Story ID: {userstory_id}

        Please execute these steps and provide the final JSON response.








    first_prompt = f"""
Step 1: Create the prompt for the language model.
mainPrompt = create_prompt({question})

get mainPrompt as string
"""
    mainPrompt = agent.chat(first_prompt)



    # Combine all tasks into a single prompt
    combined_prompt = f"""
Step 1: Retrieve the project name using the project ID.
projectname = read_db({projectID})

Step 2: Create or update the user story in the database.
new_userstory = create_db({userstory_id}, {projectID}, projectname, {question}, {createdBy})

Step 3: Generate the response from the language model.
tc_result = llm_resp(projectname, {mainPrompt})

Step 4: Convert the response to JSON and store it in the database.
response_json = return_json(tc_result, {projectID}, {userstory_id}, new_userstory, {createdBy})
        """





            combined_prompt = f"""
Step 3: Create the prompt for the language model by using the question received and just simply return it as it is dont make any more requests.
mainPrompt = create_prompt({question})
    """


    combined_prompt = f"""
Step 1: Retrieve the project name using the project ID.
projectname = read_db({projectID})

Step 2: Create or update the user story in the database using the details and also use project name retrieved earlier.
new_userstory = create_jira_db({userstory_id}, {projectID}, projectname, {question}, {createdBy})

Step 3: Generate the response from the language model by using the question.
tc_result = llm_resp(projectname, question)

Step 4: Convert the response to JSON and store it in the database and return the end JSON only.
response_json = return_json(tc_result, {projectID}, {userstory_id}, new_userstory, {createdBy})
    """




curl -X POST -H "Content-Type: application/json" -d '{"question" : "As a system admin, I shall be able to fetch value of parameter Device.X_CISCO_COM_DeviceControl.SSHEnable using dmcli command", "user" : "admin", "project" : "10391", "userstory_id" : "4333716"}' http://localhost:5000/api/ask/tm/testcases
 

