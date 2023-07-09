from github import Github
from dotenv import load_dotenv
import os
import requests
import json
from tqdm import tqdm
from langchain.schema import (
    HumanMessage,
    SystemMessage
)
import time
import openai
from langchain.chat_models.openai import ChatOpenAI
from pathlib import Path
import pandas as pd
import pinecone
from langchain.vectorstores import Pinecone
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.chains import RetrievalQA
from langchain.agents import Tool, initialize_agent
from langchain.embeddings import OpenAIEmbeddings
import datetime


class AgentSetup:
    def __init__(self):
        load_dotenv()
        self.github_api_key = os.getenv("GITHUB_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.repo_name = "spartanhaden/CaseConnect"  # add your repository name here
        self.chat = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            n=1,
            frequency_penalty=0,
            temperature=0.2,
            max_tokens=500
        )
        self.index_name = 'github-chatbot-agent'
        self.embeddings_dir = Path('embeddings')
        self.embeddings_dir.mkdir(exist_ok=True)

    def fetch_all_files(self):
        def recursive_fetch_files(repo, contents, path=""):
            files_data = []
            for content_file in contents:
                if content_file.type == "dir":
                    files_data += recursive_fetch_files(repo, repo.get_contents(content_file.path), content_file.path)
                elif content_file.name.endswith((".md", ".txt", ".py", ".js", ".html", ".env", ".json", ".css", ".java", ".c", ".cpp", ".cs", ".go", ".r", ".php", ".swift")):
                    file_content = ""
                    file_content += f"\n--- {content_file.name} ---\n"
                    try:
                        file_content += content_file.decoded_content.decode("utf-8")
                    except:  # catch any decoding errors
                        file_content += "[Content not decodable]"
                    files_data.append((content_file.name, file_content))
            return files_data

        github_instance = Github(self.github_api_key)
        repo = github_instance.get_repo(self.repo_name)
        contents = repo.get_contents("")
        files_data = recursive_fetch_files(repo, contents)
        return files_data

    def build_knowledge_base(self, files_data):
        all_chunks = []
        for filename, file_content in files_data:
            lines = file_content.splitlines()
            chunks = [' '.join(lines[i:i+5]) for i in range(0, len(lines), 5)]
            all_chunks += [(chunk, filename) for chunk in chunks]
        data = pd.DataFrame(all_chunks, columns=['context', 'filename'])
        data['name'] = 'github'
        data.drop_duplicates(subset='context', keep='first', inplace=True)
        return data

    def init_pinecone(self, data):
        pinecone.init(api_key=self.pinecone_api_key, environment="us-west4-gcp-free")
        if self.index_name not in pinecone.list_indexes():
            pinecone.create_index(
                name=self.index_name,
                metric='dotproduct',
                dimension=1536  # 1536 dim of text-embedding-ada-002
            )
        index = pinecone.Index(self.index_name)
        batch_size = 100
        embeddings_model = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
        all_vectors = {"vectors": []}
        for i in tqdm(range(0, len(data), batch_size), desc="Indexing"):
            i_end = min(len(data), i+batch_size)
            batch = data.iloc[i:i_end]
            documents = batch['context'].tolist()
            embeds = embeddings_model.embed_documents(documents)
            ids = batch.index.astype(str).tolist()
            metadatas = batch['filename'].tolist()
            for id, embed, metadata in zip(ids, embeds, metadatas):
                all_vectors["vectors"].append({
                "id": id,
                "values": embed,
                "metadata": {
                    "filename": metadata
                }
            })

        # Save to JSON
        date_str = datetime.date.today().strftime("%Y%m%d")
        embeddings_file = self.embeddings_dir / f"{self.repo_name.replace('/', '_')}_{date_str}_embeddings.json"
        with open(embeddings_file, 'w') as f:
            json.dump(all_vectors, f)

        # Upsert vectors to Pinecone
        vectors_to_upsert = [{"id": vector['id'], "values": vector['values'], "metadata": vector['metadata']} for vector in all_vectors['vectors']]
        index.upsert(vectors_to_upsert)

        text_field = 'context'
        vectorstore = Pinecone(index, embeddings_model.embed_query, text_field)
        return vectorstore

    def setup_agent(self, vectorstore):
        llm = ChatOpenAI(
            model_name='gpt-3.5-turbo',
            n=1,
            frequency_penalty=0,
            temperature=0.0
        )
        conversational_memory = ConversationBufferWindowMemory(memory_key='chat_history',k=5,return_messages=True)
        qa = RetrievalQA.from_chain_type(llm=llm,chain_type="stuff",retriever=vectorstore.as_retriever())
        tools = [
            Tool(
                name='Knowledge Base',
                func=qa.run,
                description=(
                    'use this tool for every query to get '
                    'more information on the topic'
                )
            )
        ]
        agent = initialize_agent(
            agent='chat-conversational-react-description',
            tools=tools,
            llm=llm,
            verbose=True,
            max_iterations=3,
            early_stopping_method='generate',
            memory=conversational_memory
        )
        return agent

    def run(self):
        print("Fetching all files...")
        files_data = self.fetch_all_files()

        print("Building knowledge base...")
        data = self.build_knowledge_base(files_data)

        print("Initializing Pinecone...")
        vectorstore = self.init_pinecone(data)

        print("Setting up agent...")
        agent = self.setup_agent(vectorstore)

        print("Agent setup complete.")
        return agent

if __name__ == "__main__":
    setup = AgentSetup()
    agent = setup.run()
