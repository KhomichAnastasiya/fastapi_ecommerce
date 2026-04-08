from fastapi import FastAPI
from app.routers import categories, products, users, reviews

app = FastAPI(
    title="FastAPI Интернет-магазин",
    version="0.1.0",
)

# Connecting routes for categories and products
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(users.router)
app.include_router(reviews.router)


@app.get("/")
async def root():
    """
    The root route confirming that the API is working.
    """
    return {"message": "Добро пожаловать в API интернет-магазина!"}