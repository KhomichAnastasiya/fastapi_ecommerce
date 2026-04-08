from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func

from app.models.reviews import Review as ReviewModel
from app.models.users import User as UserModel
from app.models.products import Product as ProductModel
from app.schemas import Review as ReviewSchema, ReviewCreate
from app.db_depends import get_async_db
from app.auth import get_current_user, get_current_buyer, USER_ROLE_ADMIN

router = APIRouter(
    prefix = "/reviews",
    tags=["reviews"]
)


async def update_product_rating(db: AsyncSession, product_id: int):
    result = await db.execute(
        select(func.avg(ReviewModel.grade)).where(
            ReviewModel.product_id == product_id,
            ReviewModel.is_active == True
        )
    )
    avg_rating = result.scalar() or 0.0
    product = await db.get(ProductModel, product_id)
    product.rating = avg_rating
    await db.commit()


@router.get(
    "/",
    response_model=list[ReviewSchema]
)
async def get_all_reviews(db: AsyncSession = Depends(get_async_db)):
    """
    Returns a list of all reviews.
    """
    stmt = select(ReviewModel).where(ReviewModel.is_active)
    result = await db.scalars(stmt)
    return result.all()


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


@router.post(
    "/",
    response_model=ReviewSchema,
    status_code=status.HTTP_201_CREATED
)
async def create_review_for_product(new_review: ReviewCreate,
                                    db: AsyncSession = Depends(get_async_db),
                                    _current_user: UserModel = Depends(get_current_buyer)):
    """
    Creates a new review about the product.
    """
    stmt = select(ProductModel).where(ProductModel.id == new_review.product_id,
                                       ProductModel.is_active)
    product = await db.scalar(stmt)
    if product is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    stmt = select(ReviewModel).where(ReviewModel.product_id == new_review.product_id,
                                     ReviewModel.is_active)
    result_reviews = await db.scalars(stmt)
    reviews = result_reviews.all()
    if reviews is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    db_review = ReviewModel(
        product_id = new_review.product_id,
        user_id = _current_user.id,
        grade=new_review.grade,
        comment=new_review.comment,
        is_active=True
    )
    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)
    await update_product_rating(db, db_review.product_id)
    return db_review


@router.delete(
    "/{review_id}",
    status_code=status.HTTP_200_OK
)
async def delete_review(review_id: int, db: AsyncSession = Depends(get_async_db),
                        current_user: UserModel = Depends(get_current_user)):
    """
    Deletes an review by its ID.
    """
    stmt = select(ReviewModel).where(ReviewModel.id == review_id,
                                     ReviewModel.is_active)
    review = await db.scalar(stmt)
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if current_user.role != USER_ROLE_ADMIN and current_user.id != review.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    await db.execute(
        update(ReviewModel)
        .where(ReviewModel.id == review_id)
        .values(is_active=False)
    )
    await db.commit()
    await update_product_rating(db, review.product_id)
    return {"message": "Review deleted"}
