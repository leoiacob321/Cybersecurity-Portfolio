# Overview

In this setup I will be going through how to install SPGT (Shell-GPT) using ollama. This will be powered by llama3 LLM.

First you install ollama
~~~
curl -fsSL https://ollama.com/install.sh | sh
~~~

After this you tell ollama to pull in the "llama3" LLM.

~~~
ollama pull llama3
~~~

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/8e530def-8076-4a1e-907f-19546b7c6b21" />


New, install sgpt.

~~~
pipx install shell-gpt
~~~

We need to create a directory to store the shell-gpt configuration. The command below prompts you to enter a OpenAPI key as by default, it needs a chat gpt key to run properly. Our goal is to use sgpt with the ollama with the llama3 model to run. We below we can add any OpenAPI key, here I am using "ollama".

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/03c78039-d645-4957-9cfb-8d3822140ca5" />


We now need to configure the ".sgptrc" with the below options. We can see below that we changed the following options:
  - DEFAULT_MODEL=llama3 (your pulled LLM model)
  - API_BASE_URL=http://127.0.0.1:1143/v1 (use "ollama server" to see which port ollama is listening on"
  - OPENAI_API_KEY=ollama (same as the one we set earlier)

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/69a4d093-b989-4598-b09b-e0c79af3c0a8" />


