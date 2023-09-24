from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Image, Item
from db import engine


async def check_image(image_path: str, hashed: str):
    async with AsyncSession(engine) as session:
        async with session.begin():
            existing_image = await session.execute(
                select(Image).where(Image.hashed == hashed)
            )
            existing_image = existing_image.scalar()

            if existing_image:
                return existing_image.id, False
            return None, True


async def create_image(image_path: str, hashed: str, path: str):
    async with AsyncSession(engine) as session:
        async with session.begin():
            image = Image(image=image_path, hashed=hashed, processed_image_path=path)
            session.add(image)
            await session.flush()
            await session.refresh(image)
            id = image.id
            print(id)
            await session.commit()
            return id, True



async def create_item(x1: float, y1: float, x2: float, y2: float, photo_id: int) -> Item:
    async with AsyncSession(bind=engine) as session:
        async with session.begin():
            item = Item(x1=x1, y1=y1, x2=x2, y2=y2, photo_id=photo_id)
            session.add(item)
            await session.commit()
    return item


async def get_items_by_image_id(image_id: int):
    async with AsyncSession(bind=engine) as session:
        async with session.begin():
            query = select(Item).where(Item.photo_id == image_id)
            result = await session.execute(query)
            items = result.scalars().all()

            # Создаем список словарей для представления объектов Item
            items_data = [
                {
                    "id": item.id,
                    "x1": item.x1,
                    "y1": item.y1,
                    "x2": item.x2,
                    "y2": item.y2,
                }
                for item in items
            ]

    return items_data


async def get_image_path_by_id(image_id: int):
    async with AsyncSession(engine) as session:
        async with session.begin():
            image = await session.execute(
                select(Image).where(Image.id == image_id)
            )
            image = image.scalar()
            if image:
                return image.processed_image_path
