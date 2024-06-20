from openai import OpenAI
import json
 
client = OpenAI()
print("hello")
print (client)


assistantList = client.beta.assistants.list()


assistant = client.beta.assistants.retrieve("asst_MptmDGLUuHUQf9dEvfsFfWg3")

#ask a question

thread = client.beta.threads.create()

message = client.beta.threads.messages.create(
  thread_id=thread.id,
  role="user",
  content="Who are competitors of Soilmate?"
)

run = client.beta.threads.runs.create_and_poll(
  thread_id=thread.id,
  assistant_id=assistant.id,
  instructions="Only use information from the files provided to you through file search tool"
)

messages = client.beta.threads.messages.list(
  thread_id=thread.id
)


messages = str(messages)

print(messages)



print ("HELLO \n\n\n\n\n\n")
#data type of messages
print(type(messages))


