from flask import Flask, request
from flask_cors import CORS, cross_origin
from agent_setup import AgentSetup
from langchain.schema import HumanMessage

app = Flask(__name__)
CORS(app, resources={r"/chat": {"origins": "http://localhost:3000"}})
agent = AgentSetup().run()

@app.route('/chat', methods=['POST'])
def chat():
    print(f"request: {request}")
    print(f"request.data: {request.data}")
    print(f"request.json: {request.json}")

    if request.json is not None:
        prompt = str(request.json['prompt'])  # Extract the string from the 'prompt' key
        print(f"request.json['prompt']: {request.json['prompt']}")
        print(f"type(prompt): {type(prompt)}, prompt: {prompt}")
    else:
        print("No JSON data received")
        return {'response': 'No JSON data received'}

    print(f'Passing user input to agent: {prompt}, type: {type(prompt)}')
    response = agent({'input': prompt})
    print(f"Response: {response}")
    return {'response': response.content}  # or some other key if .content doesn't exist

if __name__ == "__main__":
    app.run(debug=True)
