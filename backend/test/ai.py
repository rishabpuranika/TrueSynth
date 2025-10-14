from crewai import Crew, Agent, Task
from crewai_tools import SerperDevTool
from langchain_ibm import WatsonxLLM
from langchain_openai import ChatOpenAI
import os
import dotenv

dotenv.load_dotenv()
watsonapi = os.getenv("WATSONX_API_KEY")
serperapi=os.getenv("SERPER_API_KEY")
openrouterapi=os.getenv("OPENROUTER_API_KEY")

parameters={"decoding_method":"greedy","max_new_tokens":500}

# llm = WatsonxLLM(model_id="meta-llama/llama-3-3-70b-instruct",
#                  url="https://eu-de.ml.cloud.ibm.com",
#                  params=parameters,
#                  project_id="eb621ac3-3923-45fa-a285-8d2eb9eda8a9",
#                  apikey=watsonapi)

# functioncalling_llm = WatsonxLLM(
#     model_id="ibm/granite-3-3-8b-instruct",
#     url="https://eu-de.ml.cloud.ibm.com",
#     params=parameters,
#     project_id="eb621ac3-3923-45fa-a285-8d2eb9eda8a9",
#     apikey=watsonapi)

from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=openrouterapi,
)

completion = client.chat.completions.create(
  model="nvidia/nemotron-nano-9b-v2:free",
  messages=[
    {
      "role": "user",
      "content": "Who is Nikola Tesla?"
    }
  ]
)
#print(completion.choices[0].message.content)

# print(test_llm.invoke("Who is nikola tesla?"))

task1=Task(
    description="Search and give 5 examples on promising f1 racers",
    expected_output="A detailes bullet point summary on each topic in bullet point should cover the topic,background and why the innovation is there",
    agent=completion,
)

crew=Crew(agents=[completion],tasks=[task1],verbose=1)
print(crew.kickoff())