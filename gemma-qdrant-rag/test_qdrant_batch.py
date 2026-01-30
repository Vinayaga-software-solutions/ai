from qdrant_client import QdrantClient
from qdrant_client.http import models
import logging

logging.basicConfig(level=logging.INFO)

try:
    print("Initializing client...")
    client = QdrantClient(host="localhost", port=6333)
    
    print("Creating collection if needed...")
    try:
        client.get_collection("test_debug_collection")
    except:
        client.create_collection(
            collection_name="test_debug_collection",
            vectors_config=models.VectorParams(size=4, distance=models.Distance.COSINE)
        )
    
    print("Preparing batch...")
    ids = [1, 2]
    vectors = [[0.1, 0.2, 0.3, 0.4], [0.5, 0.6, 0.7, 0.8]]
    payloads = [{"a": 1}, {"b": 2}]
    
    print(f"Vectors type: {type(vectors)}")
    print(f"Vectors[0] type: {type(vectors[0])}")
    
    batch = models.Batch(
        ids=ids,
        vectors=vectors,
        payloads=payloads
    )
    print("Batch created successfully")
    
    print("Upserting...")
    client.upsert(
        collection_name="test_debug_collection",
        points=batch
    )
    print("✅ Upsert successful")

except Exception as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()
