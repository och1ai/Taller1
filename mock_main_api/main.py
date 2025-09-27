from fastapi import FastAPI

app = FastAPI()

@app.get("/discounts/{user_id}")
def get_discounts(user_id: str):
    return {"user_id": user_id, "discounts": []}
