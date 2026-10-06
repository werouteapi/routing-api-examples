// Routing API - Payment Routing Example (Node.js)

const RoutingAPI = require('routing-api-sdk-nodejs');

// Initialize client
const client = new RoutingAPI.Client({
  apiKey: process.env.ROUTING_API_KEY
});

async function routePayment() {
  try {
    // Route a payment
    const result = await client.routePayment({
      amount: 10000, // $100.00 in cents
      currency: 'USD',
      destination: 'US',
      paymentMethod: 'card',
      merchantId: 'merchant_123'
    });

    console.log('Routing Decision:');
    console.log(`  Provider: ${result.recommendedProvider}`);
    console.log(`  Alternatives: ${result.alternatives.join(', ')}`);
    console.log(`  Fee: $${result.estimatedFee / 100}`);
    console.log(`  Time: ${result.estimatedTime}`);

    return result;
  } catch (error) {
    console.error('Routing error:', error.message);
    throw error;
  }
}

async function handlePaymentWithRouting() {
  // Step 1: Route the payment
  const routing = await routePayment();

  // Step 2: Process with selected provider
  const payment = await client.processPayment({
    provider: routing.recommendedProvider,
    amount: 10000,
    currency: 'USD',
    customerId: 'cust_123',
    source: 'card_123',
    description: 'Order #12345'
  });

  console.log('Payment processed:', payment.id);
  return payment;
}

// Run if executed directly
if (require.main === module) {
  handlePaymentWithRouting()
    .then(() => console.log('Success!'))
    .catch(err => console.error('Error:', err));
}

module.exports = { routePayment, handlePaymentWithRouting };
