from pydantic import BaseModel, Field, ConfigDict, EmailStr
from decimal import Decimal
from datetime import datetime

from app.globals import (PRODUCT_MIN_GRADE, PRODUCT_MAX_GRADE,
                         PRODUCT_NAME_MIN_LENGTH, PRODUCT_NAME_MAX_LENGTH,
                         PRODUCT_DESCRIPTION_MAX_LENGTH,
                         PRODUCT_IMAGE_URL_MAX_LENGTH,
                         CATEGORY_NAME_MIN_LENGTH, CATEGORY_NAME_MAX_LENGTH,
                         USER_PASSWORD_MIN_LENGTH,
                         USER_ROLE_BUYER, USER_ROLE_SELLER, USER_ROLE_ADMIN)


class CategoryCreate(BaseModel):
    """
    A model for creating and updating a category.
    """
    name: str = Field(..., min_length=CATEGORY_NAME_MIN_LENGTH,
                      max_length=CATEGORY_NAME_MAX_LENGTH,
                      description=f"Название категории ({CATEGORY_NAME_MIN_LENGTH}"
                                  f"-{CATEGORY_NAME_MAX_LENGTH} символов)")
    parent_id: int | None = Field(None, description="ID родительской категории, если есть")


class Category(BaseModel):
    """
    A model for responding with category data.
    """
    id: int = Field(..., description="Уникальный идентификатор категории")
    name: str = Field(..., description="Название категории")
    parent_id: int | None = Field(None, description="ID родительской категории, если есть")
    is_active: bool = Field(..., description="Активность категории")

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    """
    A model for creating and updating a product.
    """
    name: str = Field(..., min_length=PRODUCT_NAME_MIN_LENGTH,
                      max_length=PRODUCT_NAME_MAX_LENGTH,
                      description=f"Название товара ({PRODUCT_NAME_MIN_LENGTH}"
                                  f"-{PRODUCT_NAME_MAX_LENGTH} символов)")
    description: str | None = Field(None, max_length=PRODUCT_DESCRIPTION_MAX_LENGTH,
                                    description=f"Описание товара (до"
                                                f" {PRODUCT_DESCRIPTION_MAX_LENGTH}"
                                                f" символов)")
    price: Decimal = Field(..., gt=0, description="Цена товара (больше 0)", decimal_places=2)
    image_url: str | None = Field(None, max_length=PRODUCT_IMAGE_URL_MAX_LENGTH,
                                  description="URL изображения товара")
    stock: int = Field(..., ge=0, description="Количество товара на складе (0 или больше)")
    category_id: int = Field(..., description="ID категории, к которой относится товар")


class Product(BaseModel):
    """
    The response model with the product data.
    """
    id: int = Field(..., description="Уникальный идентификатор товара")
    name: str = Field(..., description="Название товара")
    description: str | None = Field(None, description="Описание товара")
    price: Decimal = Field(..., description="Цена товара в рублях", gt=0, decimal_places=2)
    image_url: str | None = Field(None, description="URL изображения товара")
    stock: int = Field(..., description="Количество товара на складе")
    category_id: int = Field(..., description="ID категории")
    is_active: bool = Field(..., description="Активность товара")
    rating: float = Field(..., description="Рейтинг товара")

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """
    A model for creating and updating a user.
    """
    email: EmailStr = Field(description="Email пользователя")
    password: str = Field(min_length=USER_PASSWORD_MIN_LENGTH,
                          description=f"Пароль (минимум {USER_PASSWORD_MIN_LENGTH} "
                                      f"символов)")
    role: str = Field(default=USER_ROLE_BUYER, pattern=f"^({USER_ROLE_BUYER}"
                                                       f"|{USER_ROLE_SELLER}"
                                                       f"|{USER_ROLE_ADMIN})$",
                      description=f"Роль: '{USER_ROLE_BUYER}','{USER_ROLE_SELLER}' "
                                  f"или '{USER_ROLE_ADMIN}'")


class User(BaseModel):
    """
    The response model with the user data.
    """
    id: int
    email: EmailStr
    is_active: bool
    role: str
    model_config = ConfigDict(from_attributes=True)


class ReviewCreate(BaseModel):
    """
    A model for creating and updating a review.
    """
    product_id: int = Field(..., description="Продукт, на который написан отзыв")
    comment: str = Field(..., description="Содержание комментария")
    grade: int = Field(..., ge=PRODUCT_MIN_GRADE, le=PRODUCT_MAX_GRADE, description="Оценка")


class Review(BaseModel):
    """
    The response model with the review data.
    """
    id: int = Field(..., description="Уникальный идентификатор отзыва")
    user_id: int = Field(..., description="Пользователь, оставивший отзыв")
    product_id: int = Field(..., description="Продукт, на который написан отзыв")
    comment: str = Field(..., description="Содержание комментария")
    comment_date: datetime = Field(..., description="Дата создания отзыва")
    grade: int = Field(..., ge=PRODUCT_MIN_GRADE, le=PRODUCT_MAX_GRADE, description="Оценка")
    is_active: bool = Field(..., description="Активность отзыва")

    model_config = ConfigDict(from_attributes=True)


class ProductList(BaseModel):
    """
    A list of paginations for products.
    """
    items: list[Product] = Field(description="Товары для текущей страницы")
    total: int = Field(ge=0, description="Общее количество товаров")
    page: int = Field(ge=1, description="Номер текущей страницы")
    page_size: int = Field(ge=1, description="Количество элементов на странице")

    model_config = ConfigDict(from_attributes=True)


class RefreshTokenRequest(BaseModel):
    refresh_token: str


