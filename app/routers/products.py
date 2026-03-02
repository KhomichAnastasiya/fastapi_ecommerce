from fastapi import APIRouter

#The router
router = APIRouter(
    prefix="/products",
    tags=["products"]
)


@router.get("/")
async def get_all_products():
    """
    Returns a list of all products.
    """
    return {"message": "Список всех товаров (заглушка)"}


@router.post("/")
async def create_product():
    """
    Creates a new product.
    """
    return {"message": "Товар создан (заглушка)"}


@router.get("/category/{category_id}")
async def get_products_by_category(category_id: int):
    """
    Retrieves the list of products in the specified category by its ID.
    """
    return {"message": f"Товары в категории {category_id} (заглушка)"}


@router.get("/{product_id}")
async def get_product(product_id: int):
    """
    Returns detailed information about the product by its ID.
    """
    return {"message": f"Детали товара {product_id} (заглушка)"}


@router.put("/{product_id}")
async def update_product(product_id: int):
    """
    Updates the product by its ID.
    """
    return {"message": f"Товар {product_id} обновлён (заглушка)"}


@router.delete("/{product_id}")
async def delete_product(product_id: int):
    """
    Deletes an item by its ID.
    """
    return {"message": f"Товар {product_id} удалён (заглушка)"}