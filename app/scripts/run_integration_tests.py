import asyncio
import os
import sys

# Ensure parent directory is in path when running directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from httpx import AsyncClient, ASGITransport
from main import app
from core.database import init_db
from models.db_transaction import Transaction

async def run_tests():
    print("🚀 Starting WalletWiz End-to-End Integration Tests...")
    
    # 1. Initialize Beanie Database Connection
    print("Initializing Database Connection...")
    await init_db()
    
    # We use httpx.AsyncClient to query the FastAPI app in-memory (no server process needed!)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        
        # 2. Test Root/Health Endpoint
        print("\n[Test 1] GET / (Health Check)")
        response = await client.get("/")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        print("   ✅ Status: 200")
        print(f"   ✅ Response: {data}")
        
        # 3. Test Auth Login (Get JWT Token)
        print("\n[Test 2] POST /api/v1/auth/login")
        login_payload = {
            "email": "testuser@walletwiz.com",
            "password": "password123"
        }
        response = await client.post("/api/v1/auth/login", json=login_payload)
        assert response.status_code == 200, f"Failed: {response.text}"
        token_data = response.json()
        token = token_data.get("access_token")
        assert token is not None, "Access token not found in response"
        print("   ✅ Status: 200")
        print("   ✅ JWT Token received successfully.")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 4. Test Get All Transactions
        print("\n[Test 3] GET /api/v1/transactions")
        response = await client.get("/api/v1/transactions", headers=headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        tx_data = response.json()
        items = tx_data.get("data", [])
        total_items = tx_data.get("pagination", {}).get("total_items", 0)
        print("   ✅ Status: 200")
        print(f"   ✅ Retrieved {len(items)} transactions on page 1. Total items in DB: {total_items}")
        assert total_items >= 21, f"Expected at least 21 transactions in DB from seeding, got {total_items}"
        
        # 5. Test Analytics Dashboard Aggregation
        print("\n[Test 4] GET /api/v1/analytics/dashboard")
        response = await client.get("/api/v1/analytics/dashboard?timeframe=this-month", headers=headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        analytics_data = response.json()
        print("   ✅ Status: 200")
        print(f"   ✅ Total spent this month: {analytics_data.get('total_spent')}")
        print(f"   ✅ Daily average spending : {analytics_data.get('daily_average')}")
        print(f"   ✅ Categories found       : {[c['category'] for c in analytics_data.get('by_category', [])]}")
        print(f"   ✅ PM methods found      : {[p['payment_method'] for p in analytics_data.get('by_payment_method', [])]}")
        
        # 6. Test Gemini Agent: Q&A Query
        print("\n[Test 5] POST /api/v1/chat (LLM Database Query)")
        chat_payload = {
            "message": "how much did I spend in total on coffee?"
        }
        response = await client.post("/api/v1/chat", json=chat_payload, headers=headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        chat_data = response.json()
        print("   ✅ Status: 200")
        print(f"   🤖 Tool Triggered : {chat_data.get('tool_triggered')}")
        print(f"   🤖 Agent Response : {chat_data.get('response')}")
        
        # 7. Test Gemini Agent: Log Transaction
        print("\n[Test 6] POST /api/v1/chat (LLM Transaction Logging)")
        chat_log_payload = {
            "message": "spent 350 on UPI at Starbucks for coffee today"
        }
        # Get count of transactions in the database before sending message
        count_before = await Transaction.find().count()
        
        response = await client.post("/api/v1/chat", json=chat_log_payload, headers=headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        chat_log_data = response.json()
        print("   ✅ Status: 200")
        print(f"   🤖 Tool Triggered : {chat_log_data.get('tool_triggered')}")
        print(f"   🤖 Agent Response : {chat_log_data.get('response')}")
        
        # Get count of transactions in the database after message
        count_after = await Transaction.find().count()
        print(f"   ✅ Database Count Before: {count_before} | After: {count_after}")
        assert count_after == count_before + 1, "Transaction was not saved to database!"
        print("   ✅ New transaction successfully verified in MongoDB Atlas!")
        
    print("\n🎉 ALL 6 INTEGRATION TESTS PASSED SUCCESSFULLY! 🎉")

if __name__ == "__main__":
    asyncio.run(run_tests())
