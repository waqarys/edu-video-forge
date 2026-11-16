# Microservices Architecture Deep Dive

## Scene: slides
**Narration:** For experienced engineers, we use clean professional slides instead of chalkboard.
**Content:**
Key Principles of Microservices

- Single Responsibility
- Independent Deployability
- Decentralized Data

## Scene: diagram
**Narration:** Here is a typical request flow through an API gateway to backend services and a database.
**Content:**
Client -> API Gateway -> Service -> Database

## Scene: terminal
**Narration:** Deploying with a modern CLI workflow.
**Content:**
$ kubectl apply -f deployment.yaml
$ kubectl get pods
NAME                     READY   STATUS
api-gateway-7d9f8        1/1     Running

## Scene: diff
**Narration:** Refactoring from a monolith endpoint to a dedicated service.
**Content:**
Before vs After code comparison

## Scene: code
**Narration:** The actual service implementation using FastAPI.
**Content:**
```python
from fastapi import FastAPI
app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}
```

## Scene: whiteboard
**Narration:** Trade-offs to consider when splitting this further.
**Content:**
Consistency vs Availability
Latency cost of network hops
Observability requirements
