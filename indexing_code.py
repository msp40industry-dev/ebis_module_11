import json
from pinecone.grpc import PineconeGRPC, GRPCClientConfig
from pinecone import ServerlessSpec


host = "http://localhost:5080"

pc_grpc = PineconeGRPC(api_key="pclocal", host=host)
index_name = "dense-index"

if pc_grpc.has_index(index_name):
    pc_grpc.delete_index(name=index_name)

pc_grpc.create_index(
    name=index_name,
    dimension=1536,
    metric="cosine",
    spec=ServerlessSpec(
        cloud="aws",
        region="us-east-1",
    ),
    vector_type="dense"
)

index_host = pc_grpc.describe_index(name=index_name).host
index_grpc = pc_grpc.Index(host=index_host, grpc_config=GRPCClientConfig(secure=False))

with open("faq_pairs.json", encoding="utf-8") as file:
    faq_pairs = json.load(file)

index_grpc.upsert(vectors=faq_pairs, namespace='example')

print("Upsert complete")
