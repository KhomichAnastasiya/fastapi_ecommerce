from fastapi import APIRouter

# The router
router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)


@router.get("/")
async def get_all_categories():
    """
    Returns a list of all product categories.
    """
    return {"message": "Список всех категорий (заглушка)"}


@router.post("/")
async def create_category():
    """
    Creates a new category.
    """
    return {"message": "Категория создана (заглушка)"}


@router.put("/{category_id}")
async def update_category(category_id: int):
    """
    Updates a category by its ID.
    """
    return {"message": f"Категория с ID {category_id} обновлена (заглушка)"}


@router.delete("/{category_id}")
async def delete_category(category_id: int):
    """
    Deletes a category by its ID.
    """
    return {"message": f"Категория с ID {category_id} удалена (заглушка)"}