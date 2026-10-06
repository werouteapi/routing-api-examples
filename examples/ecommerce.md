# E-commerce Integration Example

## Scenario

A typical e-commerce flow with payment routing:

1. Customer adds items to cart
2. Checkout page shows price in USD
3. Customer clicks "Pay"
4. Route payment to best provider
5. Process payment
6. Update order status
7. Send confirmation

## Implementation

### 1. Routing Payment

```javascript
const RoutingAPI = require('routing-api-sdk-nodejs');

const client = new RoutingAPI.Client({
  apiKey: process.env.ROUTING_API_KEY
});

async function checkoutOrder(order) {
  // Step 1: Route the payment
  const routing = await client.routePayment({
    amount: order.totalAmount,     // in cents
    currency: order.currency,      // USD, EUR, etc
    destination: order.country,
    paymentMethod: order.method    // card, bank_transfer, etc
  });

  return routing;
}
```

### 2. Compliance Check

For payments over $10,000 USD:

```javascript
async function validateCustomer(customer) {
  const compliance = await client.checkCompliance({
    type: 'person',
    firstName: customer.firstName,
    lastName: customer.lastName,
    country: customer.country,
    dateOfBirth: customer.dob
  });

  if (compliance.sanctioned) {
    throw new Error('Customer is sanctioned');
  }

  return compliance;
}
```

### 3. Complete Checkout Flow

```javascript
async function processCheckout(order, customer) {
  try {
    // Validate customer for large orders
    if (order.totalAmount > 1000000) {  // > $10,000
      await validateCustomer(customer);
    }

    // Route payment
    const routing = await checkoutOrder(order);

    // Process with recommended provider
    const payment = await client.processPayment({
      provider: routing.recommendedProvider,
      amount: order.totalAmount,
      currency: order.currency,
      customerId: customer.id,
      orderId: order.id,
      description: `Order #${order.id}`
    });

    // Update order
    await updateOrder(order.id, {
      status: 'paid',
      paymentId: payment.id,
      provider: routing.recommendedProvider
    });

    // Send confirmation email
    await sendConfirmationEmail(customer.email, order, payment);

    return { success: true, payment };

  } catch (error) {
    // Try fallback provider
    if (routing && routing.alternatives.length > 0) {
      return await processCheckout(
        order,
        customer,
        routing.alternatives[0]
      );
    }

    // Mark order as failed
    await updateOrder(order.id, {
      status: 'payment_failed',
      error: error.message
    });

    throw error;
  }
}
```

## Best Practices

### 1. Always Validate Large Orders

```javascript
if (order.totalAmount > 1000000) {
  await validateCustomer(customer);
}
```

### 2. Implement Fallback Logic

```javascript
const providers = [
  routing.recommendedProvider,
  ...routing.alternatives
];

for (const provider of providers) {
  try {
    return await processWithProvider(provider);
  } catch (err) {
    continue;
  }
}
```

### 3. Store Provider Selection

```javascript
await db.orders.update({
  id: order.id,
  providerId: routing.recommendedProvider,
  routingScore: routing.score,
  estimatedFee: routing.estimatedFee
});
```

### 4. Monitor Fees

```javascript
const savingsByProvider = {
  provider: routing.recommendedProvider,
  fee: routing.estimatedFee,
  savedVs: routing.alternatives.map(alt => ({
    provider: alt,
    savings: routing.alternativeFees[alt] - routing.estimatedFee
  }))
};
```

## Testing

### Test Case 1: US Payment

```javascript
const order = {
  id: 'order_123',
  totalAmount: 10000,  // $100
  currency: 'USD',
  country: 'US',
  method: 'card'
};

// Expected: stripe recommended with $2.50 fee
```

### Test Case 2: International Payment

```javascript
const order = {
  id: 'order_456',
  totalAmount: 50000,  // €500
  currency: 'EUR',
  country: 'DE',
  method: 'bank_transfer'
};

// Expected: sepa_bank_transfer recommended
```

### Test Case 3: High-Value Order

```javascript
const order = {
  id: 'order_789',
  totalAmount: 10000000,  // $100,000
  currency: 'USD',
  country: 'US',
  method: 'card'
};

// Expected: requires KYC verification first
```

## Error Handling

```javascript
async function handlePaymentError(error, order) {
  switch (error.code) {
    case 'sanctioned_entity':
      // Cannot process
      return { blocked: true, reason: 'Sanctions check failed' };

    case 'card_declined':
      // Try alternative payment method
      return { retry: true, method: 'bank_transfer' };

    case 'rate_limit_exceeded':
      // Wait and retry
      await delay(5000);
      return { retry: true };

    default:
      // Log and notify
      console.error('Payment error:', error);
      return { error: error.message };
  }
}
```

## Sample Order Flow

```
Customer → Checkout Page
    ↓
Rate Limits Check (if needed)
    ↓
Compliance Check (if > $10k)
    ↓
Route Payment (get best provider)
    ↓
Process Payment
    ↓
Update Order Status
    ↓
Send Confirmation
    ↓
Success ✅
```

## See Also

- [Payment Routing Guide](https://github.com/werouteapi/routing-api-docs/blob/main/docs/payment-routing.md)
- [Compliance Guide](https://github.com/werouteapi/routing-api-docs/blob/main/docs/compliance.md)
- [Error Codes](https://github.com/werouteapi/routing-api-docs/blob/main/docs/error-codes.md)
