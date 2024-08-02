import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from slackeventsapi import SlackEventAdapter
from assistant import AssistantManager

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'], '/slack/events', app)

client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
BOT_ID = client.api_call('auth.test')['user_id']
manager  = AssistantManager()
manager.create_thread()

processed_event_ids = set()

@slack_event_adapter.on('message')
def message(payload):
    # print(payload)
    event = payload.get('event', {})
    event_id = payload.get('event_id')
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')
    
    if event_id in processed_event_ids:
        return  # Skip already processed events
    
    processed_event_ids.add(event_id)
    
    print("USER_ID: ", user_id)
    print("BOT_ID: ", BOT_ID)
    print("USER_MESSAGE\n", text)
    
    if user_id != BOT_ID:     
        manager.add_message_to_thread(
                    role = "user",
                    content =  text
                )
        manager.run_assistant(instructions="Answer to this question politly")  
                
        # Wait for completion and process messages
        response = manager._wait_for_run_completion()
    
        client.chat_postMessage(channel=channel_id , text=response)

if __name__ == '__main__':
    app.run(debug=True) 