import asyncio
import random
import uuid
from datetime import datetime, timedelta, date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models.user import User, UserRole
from app.models.developer import Developer, VerificationStatus
from app.models.property import Property, PropertyType, DealType, PropertyStatus, RenovationType
from app.models.booking import Booking, BookingStatus, BookingSource
from app.models.promo_code import PromoCode, PromoCodeType, PromoCodeStatus
from app.models.complex import Complex, ComplexClass, ComplexStatus
from app.models.lead import Lead, LeadType, LeadStatus
from app.models.review import Review
from app.models.favorite import Favorite

engine = create_async_engine(
    "postgresql+asyncpg://postgres:password@localhost:5432/realestate",
    echo=True,
)

async def create_test_data(db: AsyncSession):
    print("Creating test data...")
    
    # Create users
    users = []
    user_names = [
        ("Александр", "Петров"), ("Мария", "Иванова"), ("Дмитрий", "Сидоров"),
        ("Елена", "Козлова"), ("Андрей", "Смирнов"), ("Ольга", "Волкова"),
        ("Сергей", "Лебедев"), ("Наталья", "Новикова"), ("Михаил", "Морозов"),
        ("Татьяна", "Павлова")
    ]
    
    for i in range(10):
        first_name, last_name = user_names[i]
        user = User(
            phone=f'+7926{random.randint(1000000, 9999999)}',
            email=f'{first_name.lower()}.{last_name.lower()}.{i}.{int(datetime.now().timestamp())}@email.ru',
            first_name=first_name,
            last_name=last_name,
            role=UserRole.USER if i >= 5 else UserRole.DEVELOPER,  # First 5 will be developers
            is_active=True,
            is_verified=True
        )
        users.append(user)
        db.add(user)
    
    await db.commit()  # Commit users first
    print(f"Created {len(users)} users")

    # Create developers
    developers = []
    company_names = ["ПИК", "Самолет", "ЛСР", "Группа Эталон", "Донстрой"]
    
    for i in range(5):
        developer = Developer(
            user_id=users[i].id,
            company_name=company_names[i],
            legal_name=f'ООО "{company_names[i]}"',
            inn=f'{random.randint(1000000000, 9999999999)}',
            ogrn=f'{random.randint(1000000000000, 9999999999999)}',
            legal_address=f'г. Москва, ул. Строительная, д. {i+1}',
            contact_phone=users[i].phone,
            contact_email=users[i].email,
            website=f'https://{company_names[i].lower().replace(" ", "")}.ru',
            description=f'Крупная строительная компания {company_names[i]}',
            is_verified=True,
            verification_status=VerificationStatus.APPROVED,
            rating=Decimal(str(round(random.uniform(3.5, 5.0), 2))),
            reviews_count=random.randint(10, 200)
        )
        developers.append(developer)
        db.add(developer)
    
    await db.commit()  # Commit developers
    print(f"Created {len(developers)} developers")

    # Create complexes
    complexes = []
    complex_names = [
        ("ЖК Солнечный", "Современный жилой комплекс с развитой инфраструктурой"),
        ("ЖК Зеленый город", "Экологичный комплекс рядом с парком"),
        ("ЖК Центральный", "Элитный комплекс в центре города"),
        ("ЖК Семейный", "Комфортное жилье для семей с детьми"),
        ("ЖК Бизнес-класс", "Престижный комплекс повышенной комфортности")
    ]
    
    districts = ["Центральный", "Северный", "Южный", "Восточный", "Западный"]
    
    for i in range(5):
        name, description = complex_names[i]
        complex_obj = Complex(
            developer_id=developers[i % len(developers)].id,
            name=name,
            description=description,
            complex_class=random.choice([ComplexClass.ECONOMY, ComplexClass.COMFORT, ComplexClass.BUSINESS]),
            region="Московская область",
            city="Москва",
            district=districts[i],
            address=f'ул. {districts[i]}, д. {random.randint(1, 50)}',
            latitude=55.7558 + random.uniform(-0.1, 0.1),
            longitude=37.6176 + random.uniform(-0.1, 0.1),
            status=ComplexStatus.READY,
            total_buildings=random.randint(3, 15),
            total_apartments=random.randint(100, 500),
            price_from=Decimal(str(random.randint(3000000, 6000000))),
            price_to=Decimal(str(random.randint(8000000, 15000000))),
            has_parking=True,
            has_playground=True,
            has_school=random.choice([True, False]),
            has_kindergarten=random.choice([True, False]),
            has_shopping_center=random.choice([True, False]),
            has_fitness_center=random.choice([True, False]),
            construction_start_date=date(2023, random.randint(1, 12), random.randint(1, 28)),
            planned_completion_date=date(2025, random.randint(1, 12), random.randint(1, 28))
        )
        complexes.append(complex_obj)
        db.add(complex_obj)
    
    await db.commit()  # Commit complexes
    print(f"Created {len(complexes)} complexes")

    # Create properties
    properties = []
    for _ in range(20):
        property_obj = Property(
            developer_id=random.choice(developers).id,
            complex_id=random.choice(complexes).id,
            title=f'Квартира №{_}',
            description='Описание квартиры...',
            property_type=PropertyType.APARTMENT,
            deal_type=DealType.SALE,
            price=round(random.uniform(3000000, 15000000), 2),
            currency='RUB',
            region='Московская область',
            city='Москва',
            street='ул. Примерная',
            house_number=f'{random.randint(1, 100)}',
            rooms_count=random.randint(1, 4),
            floor=random.randint(1, 25),
            total_floors=25,
            has_parking=random.choice([True, False]),
            status=PropertyStatus.ACTIVE
        )
        properties.append(property_obj)
        db.add(property_obj)
    
    await db.commit()  # Commit properties first
    print(f"Created {len(properties)} properties")

    # Create bookings
    bookings = []
    for i, property_obj in enumerate(properties[:15]):  # Only for first 15 properties
        user = random.choice(users)
        booking = Booking(
            user_id=user.id,
            property_id=property_obj.id,
            developer_id=property_obj.developer_id,
            booking_number=f'BK{2024000 + i}',
            status=random.choice([BookingStatus.PENDING, BookingStatus.CONFIRMED, BookingStatus.PAID]),
            source=BookingSource.PLATFORM,
            property_price=property_obj.price,
            discount_amount=Decimal('0.00'),
            final_price=property_obj.price,
            booking_date=datetime.now() - timedelta(days=random.randint(1, 30)),
            contact_phone=user.phone,
            contact_email=user.email
        )
        bookings.append(booking)
        db.add(booking)
    
    print(f"Created {len(bookings)} bookings")

    # Create promo codes
    promo_codes = []
    for i in range(5):
        discount_percent = random.randint(5, 30)
        promo_code = PromoCode(
            developer_id=random.choice(developers).id,
            code=f'PROMO{i}',
            title=f'Скидка {discount_percent}%',
            description=f'Промокод на скидку {discount_percent}% при покупке недвижимости',
            promo_type=PromoCodeType.PERCENTAGE,
            discount_percentage=Decimal(str(discount_percent)),
            status=PromoCodeStatus.ACTIVE,
            valid_from=date.today(),
            valid_until=date.today() + timedelta(days=30),
            for_new_users_only=random.choice([True, False])
        )
        promo_codes.append(promo_code)
        db.add(promo_code)
    
    print(f"Created {len(promo_codes)} promo codes")

    # Commit all changes
    await db.commit()


# Asynchronous execution entry
async def main():
    AsyncSessionLocal = sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )
    async with AsyncSessionLocal() as session:
        await create_test_data(session)

if __name__ == "__main__":
    asyncio.run(main())

