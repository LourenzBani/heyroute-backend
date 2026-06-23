from fastapi import FastAPI

app = FastAPI(title="HeyRoute API")

@app.get("/health")
async def health_check():
	return {"status": "online", "message": "The HeyRoute FastAPI server is running!"}
