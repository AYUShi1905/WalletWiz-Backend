import asyncio
from datetime import datetime, timedelta
import os
import sys

# Ensure parent directory is in path when running directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.database import init_db
from core.security import hash_password
from models.db_user import User
from models.db_transaction import Transaction, TransactionCategory, PaymentMethod

MOCK_TRANSACTIONS = [
    # Food & Dining
    {"amount": 250.00, "category": TransactionCategory.FOOD_DINING, "payment_method": PaymentMethod.UPI, "merchant": "Starbucks", "description": "Morning coffee", "days_ago": 0},
    {"amount": 850.00, "category": TransactionCategory.FOOD_DINING, "payment_method": PaymentMethod.UPI, "merchant": "Pizza Hut", "description": "Dinner with friends", "days_ago": 1},
    {"amount": 420.00, "category": TransactionCategory.FOOD_DINING, "payment_method": PaymentMethod.CASH, "merchant": "McDonalds", "description": "Lunch on the go", "days_ago": 4},
    {"amount": 120.00, "category": TransactionCategory.FOOD_DINING, "payment_method": PaymentMethod.UPI, "merchant": "Chai Point", "description": "Tea and snacks", "days_ago": 8},
    {"amount": 1500.00, "category": TransactionCategory.FOOD_DINING, "payment_method": PaymentMethod.CARD, "merchant": "Absolute Barbecues", "description": "Team lunch", "days_ago": 15},
    
    # Shopping
    {"amount": 2499.00, "category": TransactionCategory.SHOPPING, "payment_method": PaymentMethod.CARD, "merchant": "Zara", "description": "New jacket", "days_ago": 2},
    {"amount": 799.00, "category": TransactionCategory.SHOPPING, "payment_method": PaymentMethod.UPI, "merchant": "Amazon", "description": "Book and phone case", "days_ago": 6},
    {"amount": 1200.00, "category": TransactionCategory.SHOPPING, "payment_method": PaymentMethod.CASH, "merchant": "Local Market", "description": "Grocery shopping", "days_ago": 12},
    {"amount": 4500.00, "category": TransactionCategory.SHOPPING, "payment_method": PaymentMethod.CARD, "merchant": "Nike Store", "description": "Running shoes", "days_ago": 25},
    
    # Travel & Transport
    {"amount": 280.00, "category": TransactionCategory.TRAVEL_TRANSPORT, "payment_method": PaymentMethod.UPI, "merchant": "Uber", "description": "Ride to office", "days_ago": 0},
    {"amount": 340.00, "category": TransactionCategory.TRAVEL_TRANSPORT, "payment_method": PaymentMethod.UPI, "merchant": "Ola Cabs", "description": "Ride back home", "days_ago": 1},
    {"amount": 150.00, "category": TransactionCategory.TRAVEL_TRANSPORT, "payment_method": PaymentMethod.CASH, "merchant": "Auto Rickshaw", "description": "Short transit", "days_ago": 5},
    {"amount": 1200.00, "category": TransactionCategory.TRAVEL_TRANSPORT, "payment_method": PaymentMethod.CARD, "merchant": "MakeMyTrip", "description": "Train ticket booking", "days_ago": 20},
    
    # Bills & Utilities
    {"amount": 3200.00, "category": TransactionCategory.BILLS_UTILITIES, "payment_method": PaymentMethod.UPI, "merchant": "State Electricity Board", "description": "Electricity bill", "days_ago": 5},
    {"amount": 799.00, "category": TransactionCategory.BILLS_UTILITIES, "payment_method": PaymentMethod.UPI, "merchant": "Airtel Fiber", "description": "Monthly broadband bill", "days_ago": 10},
    {"amount": 299.00, "category": TransactionCategory.BILLS_UTILITIES, "payment_method": PaymentMethod.CARD, "merchant": "Netflix", "description": "Monthly subscription", "days_ago": 14},
    
    # Entertainment
    {"amount": 750.00, "category": TransactionCategory.ENTERTAINMENT, "payment_method": PaymentMethod.UPI, "merchant": "BookMyShow", "description": "Movie tickets for two", "days_ago": 3},
    {"amount": 450.00, "category": TransactionCategory.ENTERTAINMENT, "payment_method": PaymentMethod.UPI, "merchant": "Smaaash", "description": "Gaming arcade", "days_ago": 18},
    
    # Health & Medical
    {"amount": 650.00, "category": TransactionCategory.HEALTH_MEDICAL, "payment_method": PaymentMethod.CARD, "merchant": "Apollo Pharmacy", "description": "Prescription medicines", "days_ago": 7},
    {"amount": 1200.00, "category": TransactionCategory.HEALTH_MEDICAL, "payment_method": PaymentMethod.CARD, "merchant": "Dr. Batra Clinic", "description": "Regular checkup fee", "days_ago": 22},
    
    # Others
    {"amount": 500.00, "category": TransactionCategory.OTHERS, "payment_method": PaymentMethod.CASH, "merchant": "Gave to friend", "description": "Lent cash to Rahul", "days_ago": 9}
]

async def seed_data():
    print("Connecting to MongoDB Atlas...")
    await init_db()
    
    test_email = "testuser@walletwiz.com"
    test_password = "password123"
    
    # 1. Create or retrieve test user
    print(f"Checking if test user '{test_email}' exists...")
    user = await User.find_one(User.email == test_email)
    
    if not user:
        print("Creating default test user...")
        user = User(
            email=test_email,
            password_hash=hash_password(test_password),
            first_name="Ayushi",
            auth_provider="email",
            created_at=datetime.utcnow()
        )
        await user.insert()
        print("✅ User created successfully.")
    else:
        print("Test user already exists.")
        # Clear old transactions for this user for a clean run
        print("Clearing old transactions for test user...")
        await Transaction.find(Transaction.user_id == user.id).delete()
        print("✅ Old transactions cleared.")

    # 2. Insert mock transactions
    print("Generating mock transactions...")
    transactions_to_insert = []
    base_time = datetime.utcnow()
    
    for mock in MOCK_TRANSACTIONS:
        # Calculate past date
        tx_date = base_time - timedelta(days=mock["days_ago"])
        # Adjust time slightly to spread them out during the day
        tx_date = tx_date.replace(hour=12 + mock["days_ago"] % 8, minute=mock["amount"] % 60 if isinstance(mock["amount"], int) else 30)
        
        tx = Transaction(
            user_id=user.id,
            amount=mock["amount"],
            category=mock["category"],
            payment_method=mock["payment_method"],
            merchant=mock["merchant"],
            description=mock["description"],
            transaction_date=tx_date,
            source_type="manual",
            created_at=tx_date
        )
        transactions_to_insert.append(tx)
        
    print(f"Inserting {len(transactions_to_insert)} transactions...")
    await Transaction.insert_many(transactions_to_insert)
    print("\n🎉 Seeding complete!")
    print("-------------------------------------------------")
    print(f"Test User Email    : {test_email}")
    print(f"Test User Password : {test_password}")
    print("-------------------------------------------------")

if __name__ == "__main__":
    asyncio.run(seed_data())
