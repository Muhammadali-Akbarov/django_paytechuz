"""
Test script for Shop + Atmos integration.
"""

import requests
import json

# Test data for creating order with Atmos payment
ORDER_DATA = {
    "product_name": "Test Product",
    "amount": "50.00",
    "payment_type": "atmos"
}

# Webhook test data
WEBHOOK_DATA = {
    "store_id": "1234",
    "transaction_id": 123456,
    "transaction_time": "1656326529324",
    "amount": 5000,  # 50 som in tiyin
    "invoice": "1",  # Order ID (will be updated after order creation)
    "sign": "sample_signature"
}


def test_create_order_with_atmos():
    """Test creating order with Atmos payment"""
    
    url = "http://localhost:8000/api/orders/create"
    
    print("Testing Order Creation with Atmos Payment...")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(ORDER_DATA, indent=2)}")
    
    try:
        response = requests.post(url, json=ORDER_DATA)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Data: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            result = response.json()
            order_id = result.get('order_id')
            payment_url = result.get('payment_url')
            
            print(f"\n✅ Order created successfully!")
            print(f"Order ID: {order_id}")
            print(f"Payment URL: {payment_url}")
            
            return order_id, payment_url
        else:
            print(f"\n❌ HTTP Error: {response.status_code}")
            return None, None
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection error. Make sure Django server is running.")
        return None, None
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return None, None


def test_webhook_with_order_id(order_id):
    """Test webhook with specific order ID"""
    
    url = "http://localhost:8000/atmos/webhook/"
    
    # Update webhook data with actual order ID
    webhook_data = WEBHOOK_DATA.copy()
    webhook_data['invoice'] = str(order_id)
    
    print(f"\nTesting Webhook for Order {order_id}...")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(webhook_data, indent=2)}")
    
    try:
        response = requests.post(url, json=webhook_data)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Data: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 1:
                print("\n✅ Webhook processed successfully!")
                print("Order status should be updated to 'paid'")
            else:
                print(f"\n❌ Webhook failed: {result.get('message')}")
        else:
            print(f"\n❌ HTTP Error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection error. Make sure Django server is running.")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def main():
    """Main test function"""
    print("=== Shop + Atmos Integration Test ===\n")
    
    # Step 1: Create order with Atmos payment
    order_id, payment_url = test_create_order_with_atmos()
    
    if order_id and payment_url:
        print(f"\n📋 Next steps:")
        print(f"1. User visits: {payment_url}")
        print(f"2. User completes payment on Atmos page")
        print(f"3. Atmos sends webhook to update order status")
        
        # Step 2: Simulate webhook (in real scenario, this comes from Atmos)
        print(f"\n🔄 Simulating webhook for Order {order_id}...")
        test_webhook_with_order_id(order_id)
        
        print(f"\n✅ Integration test completed!")
        print(f"Check Order {order_id} status in Django admin")
    else:
        print("\n❌ Order creation failed, skipping webhook test")


if __name__ == "__main__":
    main()
