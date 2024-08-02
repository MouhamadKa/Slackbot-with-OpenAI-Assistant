import json
import os
import openai
from dotenv import load_dotenv
import logging
import time
from datetime import datetime

load_dotenv()
client = openai.OpenAI()
model = "gpt-4o"
        
        
class AssistantManager:
    assistant_id = os.getenv("ASSISTANT_ID")
    thread_id = os.getenv("THREAD_ID")
    
    
    def __init__(self, model : str = model):
        self.client = client
        self.model = model
        self.assistant = None
        self.thread = None
        self.run = None
        self.summary = None
        
        
        # Retrieve existing assistant and thread if IDs are already exists
        if self.assistant_id:
            self.assistant = self.client.beta.assistants.retrieve(
                assistant_id = self.assistant_id
            )
        if self.thread_id:
            self.thread = self.client.beta.threads.retrieve(
                thread_id = self.thread_id
            )
    
    def create_assistant(self, name, instructions, tools):
        if not self.assistant:
            self.assistant = self.client.beta.assistants.create(
                name = name,
                model = self.model,
                instructions= instructions,
                tools = tools
            )
            self.assistant_id = self.assistant.id
            # print(f"Assistant ID: {self.assistant_id}")

    def create_thread(self):
        if not self.thread:
            self.thread = self.client.beta.threads.create()
            self.thread_id = self.thread.id 
            # print(f"Thread ID: {self.thread_id}")           
            
    def add_message_to_thread(self, role, content):
        if self.thread:
            self.client.beta.threads.messages.create(
                thread_id = self.thread_id,
                role = role,
                content = content
            )
            
    def run_assistant(self, instructions):
        if self.assistant and self.thread:
            self.run = self.client.beta.threads.runs.create(
                assistant_id = self.assistant_id,
                thread_id = self.thread_id,
                instructions = instructions
            )
            
    def process_messages(self):
        if self.thread:
            messages = self.client.beta.threads.messages.list(thread_id= self.thread_id)
            summary = []
            
            last_message = messages.data[0]
            role = last_message.role
            response = last_message.content[0].text.value
            summary.append(response)
            
            self.summary = "\n".join(summary)
            print(f"SUMMARY ------> {role.capitalize()}: ====> {response}")

                
    def _wait_for_run_completion(self, sleep_interval=3):
        run_id = self.run.id
        counter = 1
        while True:
            try:
                run = self.client.beta.threads.runs.retrieve(thread_id=self.thread_id, run_id=run_id)
                if run.completed_at:
                    messages = self.client.beta.threads.messages.list(thread_id=self.thread_id)
                    last_message = messages.data[0]
                    response = last_message.content[0].text.value
                    
                    index = response.find('【')
                    if index != -1:
                        response = response[:index]
                    # print(f'hello {counter}')
                    return response
            except Exception as e:
                raise RuntimeError(f"An error occurred while retrieving answer: {e}")
            counter += 1
            time.sleep(sleep_interval)             

    def run_steps(self):
        run_steps = self.client.beta.threads.runs.steps.list(
            thread_id= self.thread_id,
            run_id= self.run.id
        )
        # print(f"Run Steps ===> {run_steps}")
        return run_steps
    
