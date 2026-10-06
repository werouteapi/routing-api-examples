# Routing API - Integration Examples

Real-world code examples for integrating the Routing API into your application.

## Examples by Language

### JavaScript/Node.js
```javascript
const RoutingAPI = require('routing-api-sdk-nodejs');

const client = new RoutingAPI.Client({
  apiKey: 'your-api-key'
});

const result = await client.routePayment({
  amount: 10000,
  currency: 'USD',
  destination: 'US',
  paymentMethod: 'card'
});

console.log('Best provider:', result.recommendedProvider);
```

### Python
```python
from routing_api_sdk import RoutingAPIClient

client = RoutingAPIClient(api_key='your-api-key')

result = client.route_payment(
    amount=10000,
    currency='USD',
    destination='US',
    payment_method='card'
)

print(f'Best provider: {result.recommended_provider}')
```

### Go, Java, Ruby, PHP, Swift, Rust, Dart, Perl, C#, Elixir
See `/examples/{language}` directories for complete examples.

## Use Cases

- [E-commerce Integration](examples/ecommerce.md)
- [Subscription Billing](examples/subscriptions.md)
- [Multi-Currency Payments](examples/multi-currency.md)
- [Compliance Checks](examples/compliance.md)
- [Webhook Handling](examples/webhooks.md)
- [Error Handling](examples/error-handling.md)

## Quick Start

1. Get your API key from the developer dashboard
2. Install the SDK for your language:
   ```bash
   npm install routing-api-sdk-nodejs
   pip install routing-api-sdk-python
   go get github.com/werouteapi/routing-api-sdk-go
   ```
3. Copy an example from this repo
4. Replace `your-api-key` with your actual key
5. Run and test

## Common Tasks

- **Route a payment** - See `examples/payment-routing.md`
- **Check compliance** - See `examples/compliance-check.md`
- **Handle webhooks** - See `examples/webhook-listener.md`
- **Process refunds** - See `examples/refunds.md`

## Support

Email: support@webundle.org
