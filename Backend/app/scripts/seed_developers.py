"""
Seed script for creating sample developers.
"""

import asyncio
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import create_db_connection, get_async_session
from app.models import Developer, User, UserRole
from app.models.developer import VerificationStatus


async def seed_developers():
    """Create sample developers."""

    await create_db_connection()

    async for db in get_async_session():
        # Sample developers.
        developers_data = [
            {
                "user": {
                    "phone": "+79991234567",
                    "email": "info@pik.ru",
                    "first_name": "Александр",
                    "last_name": "Петров",
                    "middle_name": "Сергеевич",
                    "role": UserRole.DEVELOPER,
                    "is_verified": True,
                },
                "developer": {
                    "company_name": "ПИК",
                    "legal_name": 'ПАО "ПИК-специализированный застройщик"',
                    "inn": "7704217201",
                    "ogrn": "1027700155967",
                    "legal_address": "127055, г. Москва, ул. Большая Тишинская, д. 38",
                    "contact_phone": "+74951234567",
                    "contact_email": "info@pik.ru",
                    "website": "https://pik.ru",
                    "description": "Крупнейший застройщик России, специализирующийся на жилой недвижимости премиум и комфорт-класса",
                    "rating": Decimal("4.8"),
                    "reviews_count": 156,
                    "is_verified": True,
                    "verification_status": VerificationStatus.APPROVED,
                },
            },
            {
                "user": {
                    "phone": "+79992345678",
                    "email": "info@lsr.ru",
                    "first_name": "Мария",
                    "last_name": "Иванова",
                    "middle_name": "Александровна",
                    "role": UserRole.DEVELOPER,
                    "is_verified": True,
                },
                "developer": {
                    "company_name": "Группа ЛСР",
                    "legal_name": 'АО "Группа ЛСР"',
                    "inn": "7801001234",
                    "ogrn": "1027800000012",
                    "legal_address": "190031, г. Санкт-Петербург, набережная реки Фонтанки, д. 59",
                    "contact_phone": "+78122345678",
                    "contact_email": "info@lsr.ru",
                    "website": "https://www.lsr.ru",
                    "description": "Группа ЛСР - ведущая девелоперская компания, строящая жилые комплексы в Москве и Санкт-Петербурге",
                    "rating": Decimal("4.6"),
                    "reviews_count": 89,
                    "is_verified": True,
                    "verification_status": VerificationStatus.APPROVED,
                },
            },
            {
                "user": {
                    "phone": "+79993456789",
                    "email": "info@samolet.ru",
                    "first_name": "Игорь",
                    "last_name": "Смирнов",
                    "role": UserRole.DEVELOPER,
                    "is_verified": True,
                },
                "developer": {
                    "company_name": "Самолет",
                    "legal_name": 'ООО "Самолет Девелопмент"',
                    "inn": "7722334455",
                    "ogrn": "1027722334455",
                    "legal_address": "109004, г. Москва, ул. Александра Солженицына, д. 23Б, стр. 1",
                    "contact_phone": "+74953456789",
                    "contact_email": "info@samolet.ru",
                    "website": "https://samolet.ru",
                    "description": "Самолет - современная девелоперская компания, создающая комфортные жилые кварталы",
                    "rating": Decimal("4.4"),
                    "reviews_count": 67,
                    "is_verified": True,
                    "verification_status": VerificationStatus.APPROVED,
                },
            },
            {
                "user": {
                    "phone": "+79994567890",
                    "email": "info@newdev.ru",
                    "first_name": "Елена",
                    "last_name": "Волкова",
                    "role": UserRole.DEVELOPER,
                    "is_verified": False,
                },
                "developer": {
                    "company_name": "НовСтрой",
                    "legal_name": 'ООО "НовСтрой-Инвест"',
                    "inn": "7733445566",
                    "ogrn": "1027733445566",
                    "legal_address": "119435, г. Москва, ул. Малая Пироговская, д. 18",
                    "contact_phone": "+74954567890",
                    "contact_email": "info@newdev.ru",
                    "website": "https://novstroy.ru",
                    "description": "Молодая амбициозная команда профессионалов в сфере девелопмента",
                    "rating": Decimal("4.2"),
                    "reviews_count": 23,
                    "is_verified": False,
                    "verification_status": VerificationStatus.PENDING,
                },
            },
        ]

        for data in developers_data:
            # Create user
            user = User(**data["user"])
            db.add(user)
            await db.flush()  # Get user.id

            # Create developer profile
            developer_data = data["developer"].copy()
            developer_data["user_id"] = user.id
            developer = Developer(**developer_data)
            db.add(developer)

        await db.commit()
        print("✅ Sample developers created successfully!")
        break


if __name__ == "__main__":
    asyncio.run(seed_developers())
