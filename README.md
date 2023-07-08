# AgentCode: GitHub Integrated Conversational Agent

AgentCode is a forward-thinking concept that integrates a web-based chat interface with a conversational agent (chatbot). This cutting-edge agent leverages data from a GitHub repository to respond intelligently to user queries. Its operational basis is the GPT-3.5-turbo model from OpenAI for language understanding and generation, coupled with the Pinecone vector search engine for efficient information retrieval and storage.

## How to Use

1. Enter your GitHub, OpenAI, and Pinecone API keys, and your GitHub repository name, in the `.env` file.
2. Install the required packages. Run `pip install -r requirements.txt` for Python dependencies and `npm install` for JavaScript dependencies.
3. Initiate the Flask API by running `python app.py`.
4. Start the React application by running `npm start`.
5. Navigate to localhost:3000 in your web browser.
6. Enter your query in the input field and click the 'Submit' button to get a response.

## Code Explanation

The AgentCode application consists of three main components:

### app.py (Flask API)

This part of the code sets up the Flask API server and outlines a single endpoint, /chat. The /chat endpoint accepts POST requests comprising a prompt field in the request body, signifying the user's question for the chatbot. The endpoint processes the prompt using the conversational agent derived from `agent_setup.py` and returns the agent's response.

### agent_setup.py (Setup Script)

This part of the code features the AgentSetup class, responsible for initializing the conversational agent. The main steps it undertakes are:

- Utilizing the GitHub API to fetch all relevant files from a specific GitHub repository. It focuses on particular file types (e.g., .md, .txt, .py).
- Creating a "knowledge base" by dividing the content of each fetched file into segments of five lines each. These segments are stored with their corresponding filename.
- Initializing the Pinecone vector search engine and storing each segment from the knowledge base in it.
- Setting up the agent with multiple tools, including a language model for conversation and a tool to retrieve information from the Pinecone knowledge base.

On instantiation of the AgentSetup class and calling its run method, these steps are executed, returning the initialized agent.

### app.js (React Frontend)

This script sets up the React frontend, which houses a text input field for user queries, a 'Submit' button to forward the query to the backend, and a text output field for displaying the agent's response.

On clicking the 'Submit' button, the current content of the input field is sent as a POST request to the Flask API's /chat endpoint. The Flask API processes the prompt using the conversational agent and sends back the response, which the frontend then presents in the output field.

## Contributing

Feel free to contribute!

# TODO

- [ ] Finish connecting front end and back end
- [ ] Adjust UI for a more attractive text output (code)
- [ ] Build input field on UI for GitHub repo input
- [ ] Build history on UI to switch between repo's
- [ ] Create ability to update vector db when repo changes

## License

This project is licensed under the MIT License. Enjoy using AgentCode and let us know of any cool improvements you make.
