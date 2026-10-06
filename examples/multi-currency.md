# Multi-Currency Payments Example

## Scenario

Handle payments in different currencies and countries.

```javascript
async function processMultiCurrencyPayment(order) {
  const client = new RoutingAPI.Client({
    apiKey: process.env.ROUTING_API_KEY
  });

  // Route with local currency
  const routing = await client.routePayment({
    amount: order.amount,
    currency: order.currency,  // EUR, GBP, JPY, etc
    destination: order.country
  });

  return await client.processPayment({
    provider: routing.recommendedProvider,
    ...order
  });
}
```

[See full example in ecommerce.md](ecommerce.md)
