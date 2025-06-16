from db import DBUtil

db = os.getenv("MONGODB_NAME")
collection = "testbed"

def engine(script):
    devicetype = request.json['devicetype']
    result = DBUtilt.getDocumnetByKeyValue(db, collection, "devicetype", devicetype)
    hostname = result[0]['hostname']
    password = result[0]['password']

    patterns = {
                   r'hostname\s*=\s*"[^"]*"': f'hostname = "{new_hostname}"',
                   r'hostname\s*=\s*"[^"]*"': f'hostname = "{new_hostname}"',
                   # r'port\s*=\s*"[^"]*"': f'port = "{new_port}"',
               }

    for pattern, replacement in patterns.items():
        script = re.sub(pattern, replacement, script)

    return script
