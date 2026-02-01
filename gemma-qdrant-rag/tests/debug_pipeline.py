import logging
logging.basicConfig(level=logging.INFO)

try:
    from app.ingestion import IngestionPipeline
    print("✅ Module imported")
    pipeline = IngestionPipeline()
    print("✅ Pipeline instantiated")
except Exception as e:
    import traceback
    with open("error.log", "w") as f:
        traceback.print_exc(file=f)
    traceback.print_exc()
