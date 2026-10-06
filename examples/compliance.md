# Compliance Checks Example

## Scenario

Verify customer compliance before processing payments.

```javascript
async function checkCompliance(customer) {
  const client = new RoutingAPI.Client({
    apiKey: process.env.ROUTING_API_KEY
  });

  const result = await client.checkCompliance({
    type: 'person',
    firstName: customer.firstName,
    lastName: customer.lastName,
    country: customer.country,
    dateOfBirth: customer.dob
  });

  if (result.sanctioned) {
    throw new Error('Customer is sanctioned');
  }

  return result;
}
```

[See full guide in routing-api-docs](https://github.com/werouteapi/routing-api-docs/blob/main/docs/compliance.md)
