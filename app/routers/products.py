from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.products import Product as ProductModel
from app.models.categories import Category as CategoryModel
from app.models.reviews import Review as ReviewModel
from app.models.users import User as UserModel
from app.schemas import Product as ProductSchema, ProductCreate
from app.schemas import Review as ReviewSchema
from app.db_depends import get_async_db
from app.auth import get_current_seller

router = APIRouter(
    prefix="/products",
    tags=["products"]
)


@router.get(
    "/",
    response_model=list[ProductSchema]
)
async def get_all_products(db: AsyncSession = Depends(get_async_db)):
    """
    Returns a list of all products.
    """
    stmt = select(ProductModel).where(ProductModel.is_active)
    result = await db.scalars(stmt)
    return result.all()


@router.post(
    "/",
    response_model=ProductSchema,
    status_code=status.HTTP_201_CREATED
)
async def create_product(product: ProductCreate,
                         db: AsyncSession = Depends(get_async_db),
                         current_user: UserModel = Depends(get_current_seller)):
    """
    Creates a new product.
    """
    stmt = select(CategoryModel).where(CategoryModel.id == product.category_id,
                                       CategoryModel.is_active)
    result = await db.scalars(stmt)
    category = result.first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Category not found or inactive")

    db_product = ProductModel(**product.model_dump(), seller_id=current_user.id)
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product


@router.get(
    "/category/{category_id}",
    response_model=list[ProductSchema],
    status_code=status.HTTP_200_OK
)
async def get_products_by_category(category_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Retrieves the list of products in the specified category by its ID.
    """
    stmt = select(CategoryModel).where(and_(CategoryModel.id == category_id,
                                            CategoryModel.is_active))
    category_result = await db.scalars(stmt)
    category = category_result.first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Category not found or inactive")

    stmt = select(ProductModel).where(ProductModel.category_id == category_id,
                                      ProductModel.is_active)
    products_result = await db.scalars(stmt)
    return products_result.all()


@router.get(
    "/{product_id}",
    response_model=ProductSchema,
    status_code=status.HTTP_200_OK
)
async def get_product(product_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Returns detailed information about the product by its ID.
    """
    stmt = select(ProductModel).where(and_(ProductModel.id == product_id,
                                           ProductModel.is_active))
    product_result = await db.scalars(stmt)
    product = product_result.first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Product not found or inactive")
    stmt = select(CategoryModel).where(and_(CategoryModel.id == product.category_id,
                                            CategoryModel.is_active))
    category_result = await db.scalars(stmt)
    category = category_result.first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Category not found or inactive")
    return product


@router.put(
    "/{product_id}",
    response_model=ProductSchema,
    status_code=status.HTTP_200_OK
)
async def update_product(product_id: int, product: ProductCreate,
                         db: AsyncSession = Depends(get_async_db),
                         current_user: UserModel = Depends(get_current_seller)):
    """
    Updates the product by its ID.
    """
    stmt = select(ProductModel).where(and_(ProductModel.id == product_id,
                                           ProductModel.is_active))
    db_product_result = await db.scalars(stmt)
    db_product = db_product_result.first()
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Product not found or inactive")

    if db_product.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You can only update your own products")

    stmt = select(CategoryModel).where(and_(CategoryModel.id == product.category_id,
                                            CategoryModel.is_active))
    category_result = await db.scalars(stmt)
    category = category_result.first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Category not found or inactive")

    update_data = product.model_dump(exclude_unset=True)
    await db.execute(
        update(ProductModel)
        .where(ProductModel.id == product_id)
        .values(**update_data)
    )
    await db.commit()
    await db.refresh(db_product)
    return db_product


@router.get(
    "/{product_id}/reviews/",
    response_model=list[ReviewSchema]
)
async def get_all_product_reviews(product_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Returns a list of all reviews for the product.
    """
    stmt = select(ProductModel).where(ProductModel.id == product_id,
                                      ProductModel.is_active)
    product = await db.scalar(stmt)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Product not found or inactive")

    stmt = select(ReviewModel).where(product.id == product_id,
                                     ReviewModel.is_active)
    result_review = await db.scalars(stmt)
    reviews = result_review.all()
    if reviews is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail = "Reviews not found or inactive")
    return reviews


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_200_OK
)
async def delete_product(product_id: int,
                         db: AsyncSession = Depends(get_async_db),
                         current_user: UserModel = Depends(get_current_seller)):
    """
    Deletes an item by its ID.
    """
    stmt = select(ProductModel).where(and_(ProductModel.id == product_id,
                                           ProductModel.is_active))
    product_result = await db.scalars(stmt)
    db_product = product_result.first()
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Product not found or inactive")

    if db_product.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You can only delete your own products")

    await db.execute(
        update(ProductModel)
        .where(ProductModel.id == product_id)
        .values(is_active=False))
    await db.commit()
    await db.refresh(db_product)
    return db_product