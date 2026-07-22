import sqlite3
import json

class DataBase:
    def __init__(self) -> None:
        self.db_name = "Contacts_DB"
        self.table_name = "contacts"
        self.connection = sqlite3.connect(self.db_name)

        cursor = self.connection.cursor()
        cursor.execute(
            f"CREATE TABLE IF NOT EXISTS {self.table_name} (id INTEGER, name TEXT, email TEXT)"
        )
        self.connection.commit()

    def add_contact(self, email, name="unknown"):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                        f"INSERT INTO {self.table_name} (name, email) VALUES (?, ?)",
                        (name, email)
                    )
            self.connection.commit()
            return "Ok"
        except Exception as e:
            return "not inserted"


def record_unknown_question(question):
    with open("unknown_questions.txt", "a", unicode="utf-8") as f:
        f.write(question + " /n")
    return "Ok"
   

db = DataBase()

tools_add_contact_json = {
    "name": "add_contact",
    "description": "Use this tool to record an email of the user if it provided",
    "parameters": {
        "type": "object",
        "properties":{
            "name": {"type": "string", "description": "The name of the user if provided"},
            "email": {"type": "string", "description": "The email address of the user"}
        }
    },
    "required": "email",
    "additionalProperties": False
}

tools_record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Use this tool to record a question that you dob't know about it",
    "parameters": {
        "type": "object",
        "properties":{
            "question": {"type": "string", "description": "The question you can not answer it"},
        }
    },
    "required": "question",
    "additionalProperties": False
}

tools = [{"type": "function", "function": tools_add_contact_json},
         {"type": "function", "function": tools_record_unknown_question_json}]

tools_map = {
    "add_contact": db.add_contact,
    "record_unknown_question": record_unknown_question
}

def handle_tool_calls(tool_calls):
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        tool = tools_map.get(tool_name)
        result = tool(**arguments) if tool else f"unknown tool: {tool_name}"
        results.append([{"role": "tool", "content": json.dumps(result), "tool_call_id": tool_call.id}])
    return results
