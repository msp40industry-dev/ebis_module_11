from pinecone.grpc import PineconeGRPC, GRPCClientConfig
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def start_pinecone_index_grpc_client(host, index_name):

    pc_grpc = PineconeGRPC(api_key="pclocal", host=host)

    index_host = pc_grpc.describe_index(name=index_name).host
    index_grpc = pc_grpc.Index(host=index_host, grpc_config=GRPCClientConfig(secure=False))
    return index_grpc


def start_openai_client():
    client = OpenAI()
    return client


def generate_embedding(user_query, openai_client):

    response = openai_client.embeddings.create(
        input=user_query,
        model="text-embedding-3-small"
    )
    embedding = response.data[0].embedding
    return embedding


def retrieval_step(user_query, index_grpc_client, openai_client):
    embedding = generate_embedding(user_query, openai_client)
    combined_results = index_grpc_client.query(
        vector=embedding,
        namespace='example',
        top_k=3,
        include_values=False,
        include_metadata=True,
        show_progress=False,
        alpha=0.5
    )
    retrieved_qa = [
        f"Pregunta: {match['metadata']['pregunta']}\nRespuesta:{match['metadata']['respuesta']}\n\n" 
        for match in combined_results.matches
    ]
    return retrieved_qa


def chat_openai_with_history(openai_client, messages, system_content=None):
    if system_content:
        messages.insert(0, {"role": "system", "content": system_content})

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )
    return response.choices[0].message.content


def replace_user_prompt(new_user_prompt, historical_messages):
    user_content = historical_messages[-1]["content"]
    if historical_messages[-1]["role"] == "user":
        if isinstance(user_content, str):
            historical_messages[-1]["content"] = new_user_prompt
        elif isinstance(user_content, list):
            historical_messages[-1]["content"][0]["text"] = new_user_prompt
    else:
        raise ValueError("Last message in history must be from the user")
    return historical_messages


def generation_step(retrieved_qa, user_query, historical_messages, system_prompt):

    openai_client = start_openai_client()
    
    user_prompt = f"""
        Contexto:
        <<<{retrieved_qa}>>>

        Pregunta:
        <<<{user_query}>>>

        Respuesta:"""

    messages = replace_user_prompt(user_prompt, historical_messages)
    response = chat_openai_with_history(openai_client, messages, system_content=system_prompt)

    return response


def generation_main_workflow(user_query, host, index_name, historical_messages, system_prompt):
    index_grpc_client = start_pinecone_index_grpc_client(host, index_name)
    openai_client = start_openai_client()

    retrieved_qa = retrieval_step(user_query, index_grpc_client, openai_client)
    response = generation_step(retrieved_qa, user_query, historical_messages, system_prompt)
    return response

