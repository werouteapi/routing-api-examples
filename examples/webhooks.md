# Webhook Handling Example

## Scenario

Receive and handle webhook events from Routing API.

```javascript
const express = require('express');
const app = express();

app.post('/webhooks/routing', express.json(), async (req, res) => {
  const event = req.body;

  switch (event.type) {
    case 'payment.completed':
      await handlePaymentCompleted(event.data);
      break;

    case 'payment.failed':
      await handlePaymentFailed(event.data);
      break;

    case 'payment.refunded':
      await handleRefund(event.data);
      break;
  }

  res.json({ received: true });
});
```

[See full guide in routing-api-docs](https://github.com/werouteapi/routing-api-docs/blob/main/docs/webhooks.md)
