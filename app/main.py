from fastapi import FastAPI

# Create our FastAPI application
app = FastAPI(
    title="Enterprise AI Operations Agent",
    version="1.0.0"
)


# Basic route to check whether the backend is running
@app.get("/")
def home():
    return {
        "message": "Enterprise AI Operations Agent is running"
    }


# Health-check route
@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }