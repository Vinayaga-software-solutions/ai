try:
    from app.config import settings
    print("✅ Settings loaded successfully")
    print(f"QDRANT_HOST: {settings.QDRANT_HOST}")
    print(f"EMBEDDING_STRATEGY: {settings.EMBEDDING_STRATEGY}")
except Exception as e:
    import traceback
    traceback.print_exc()
