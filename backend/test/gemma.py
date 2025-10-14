from openai import OpenAI
import os
import dotenv

dotenv.load_dotenv()
openrouterapi=os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=openrouterapi,
)

prompt="F1 standings 2025"

generator_llm = client.chat.completions.create(\
  model="meta-llama/llama-3.2-3b-instruct:free",
  messages=[
    {
      "role": "user",
      "content": prompt,
    }
  ]
)

print(generator_llm.choices[0].message.content)