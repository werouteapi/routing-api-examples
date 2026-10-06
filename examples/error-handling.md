# Error Handling Example

## Scenario

Properly handle errors and implement retry logic.

```javascript
async function processPaymentWithErrorHandling(order) {
  const client = new RoutingAPI.Client({
    apiKey: process.env.ROUTING_API_KEY
  });

  try {
    const routing = await client.routePayment({
      amount: order.amount,
      currency: order.currency,
      destination: order.country
    });

    return await client.processPayment({
      provider: routing.recommendedProvider,
      ...order
    });

  } catch (error) {
    if (error.code === 'rate_limit_exceeded') {
      await delay(5000);
      return processPaymentWithErrorHandling(order);
    } else if (error.code === 'card_declined') {
      throw new Error('Payment method declined');
    } else {
      console.error('Payment error:', error);
      throw error;
    }
  }
}
```

[See full guide in routing-api-docs](https://github.com/werouteapi/routing-api-docs/blob/main/docs/error-codes.md)
