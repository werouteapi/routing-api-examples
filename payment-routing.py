#!/usr/bin/env python3
"""
Routing API - Payment Routing Example (Python)
"""

from routing_api_sdk import RoutingAPIClient
import os
import json

# Initialize client
api_key = os.getenv('ROUTING_API_KEY')
client = RoutingAPIClient(api_key=api_key)

def route_payment():
    """Route a payment to the best provider"""
    
    try:
        result = client.route_payment(
            amount=10000,  # $100.00 in cents
            currency='USD',
            destination='US',
            payment_method='card',
            merchant_id='merchant_123'
        )
        
        print('Routing Decision:')
        print(f"  Provider: {result.recommended_provider}")
        print(f"  Alternatives: {', '.join(result.alternatives)}")
        print(f"  Fee: ${result.estimated_fee / 100:.2f}")
        print(f"  Time: {result.estimated_time}")
        
        return result
        
    except Exception as e:
        print(f'Routing error: {str(e)}')
        raise

def handle_payment_with_routing():
    """Complete payment flow with routing"""
    
    # Step 1: Route the payment
    routing = route_payment()
    
    # Step 2: Process with selected provider
    payment = client.process_payment(
        provider=routing.recommended_provider,
        amount=10000,
        currency='USD',
        customer_id='cust_123',
        source='card_123',
        description='Order #12345'
    )
    
    print(f'\nPayment processed: {payment.id}')
    print(json.dumps(payment.to_dict(), indent=2))
    
    return payment

def list_failed_payments():
    """List recent failed payments"""
    
    payments = client.list_payments(
        status='failed',
        limit=10
    )
    
    print(f'Failed payments: {len(payments)}')
    for payment in payments:
        print(f"  - {payment.id}: {payment.error_message}")

if __name__ == '__main__':
    try:
        handle_payment_with_routing()
        list_failed_payments()
    except Exception as e:
        print(f'Error: {str(e)}')
        exit(1)
