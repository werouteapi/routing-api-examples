# Subscription Billing Example

## Scenario

Recurring billing for subscription services:

1. Customer subscribes to plan
2. Charge recurring payments
3. Handle failed payments
4. Update subscription status
5. Send receipts

## Implementation

### 1. Setup Subscription

```javascript
async function createSubscription(customer, plan) {
  const client = new RoutingAPI.Client({
    apiKey: process.env.ROUTING_API_KEY
  });

  // Route the subscription payment
  const routing = await client.routePayment({
    amount: plan.monthlyPrice,
    currency: 'USD',
    destination: customer.country,
    paymentMethod: 'card',
    recurring: true  // Mark as recurring
  });

  // Create subscription record
  const subscription = await db.subscriptions.create({
    customerId: customer.id,
    planId: plan.id,
    status: 'active',
    provider: routing.recommendedProvider,
    nextBillDate: addMonths(new Date(), 1),
    amount: plan.monthlyPrice
  });

  return subscription;
}
```

### 2. Process Recurring Charge

```javascript
async function processRecurringCharge(subscription) {
  const client = new RoutingAPI.Client({
    apiKey: process.env.ROUTING_API_KEY
  });

  try {
    // Process payment with stored provider
    const payment = await client.processPayment({
      provider: subscription.provider,
      amount: subscription.amount,
      currency: 'USD',
      customerId: subscription.customerId,
      subscriptionId: subscription.id,
      recurring: true
    });

    // Update subscription
    await db.subscriptions.update(subscription.id, {
      status: 'active',
      lastPaymentDate: new Date(),
      nextBillDate: addMonths(new Date(), 1),
      failureCount: 0
    });

    // Send receipt
    await sendReceiptEmail(subscription, payment);

    return { success: true, payment };

  } catch (error) {
    return handleRecurringPaymentError(subscription, error);
  }
}
```

### 3. Handle Failed Payments

```javascript
async function handleRecurringPaymentError(subscription, error) {
  const failureCount = (subscription.failureCount || 0) + 1;

  // Update failure count
  await db.subscriptions.update(subscription.id, {
    failureCount: failureCount,
    lastError: error.message,
    status: failureCount >= 3 ? 'suspended' : 'active'
  });

  if (failureCount === 1) {
    // First failure - retry in 3 days
    await scheduleRetry(subscription.id, 3);
    await sendPaymentFailureEmail(subscription, 'retry');

  } else if (failureCount === 2) {
    // Second failure - retry in 5 days
    await scheduleRetry(subscription.id, 5);
    await sendPaymentFailureEmail(subscription, 'final_notice');

  } else if (failureCount >= 3) {
    // Cancel subscription after 3 failures
    await cancelSubscription(subscription.id);
    await sendSubscriptionCancelledEmail(subscription, 'payment_failed');
  }

  return { success: false, retry: failureCount < 3 };
}
```

### 4. Scheduled Job (Billing Daemon)

```javascript
// Run daily to process renewals
async function processDailyRenewals() {
  const client = new RoutingAPI.Client({
    apiKey: process.env.ROUTING_API_KEY
  });

  // Find subscriptions due for renewal
  const dueSubscriptions = await db.subscriptions.find({
    status: 'active',
    nextBillDate: { $lte: new Date() }
  });

  console.log(`Processing ${dueSubscriptions.length} renewals...`);

  for (const subscription of dueSubscriptions) {
    try {
      await processRecurringCharge(subscription);
      console.log(`✅ Renewed: ${subscription.id}`);
    } catch (error) {
      console.error(`❌ Failed: ${subscription.id} - ${error.message}`);
    }
  }
}

// Run at 00:00 UTC daily
schedule.scheduleJob('0 0 * * *', processDailyRenewals);
```

## Advanced Features

### 1. Dunning Management

```javascript
async function manageDunning(subscription) {
  const failureCount = subscription.failureCount || 0;

  const dunningStrategy = {
    1: { retryAfter: 3, message: 'Your payment failed. We'll retry in 3 days.' },
    2: { retryAfter: 5, message: 'Final retry attempt. Your subscription will be cancelled if this fails.' },
    3: { retryAfter: 0, message: 'Subscription cancelled due to payment failure.' }
  };

  const strategy = dunningStrategy[failureCount] || { cancel: true };

  if (strategy.cancel) {
    await cancelSubscription(subscription.id);
  } else {
    await scheduleRetry(subscription.id, strategy.retryAfter);
    await sendEmail(subscription.customerId, strategy.message);
  }
}
```

### 2. Plan Upgrades/Downgrades

```javascript
async function changePlan(subscription, newPlan) {
  const prorationAmount = calculateProration(
    subscription.plan,
    newPlan,
    subscription.nextBillDate
  );

  if (prorationAmount > 0) {
    // Charge immediately
    await client.processPayment({
      amount: prorationAmount,
      description: `Plan upgrade proration`
    });
  }

  await db.subscriptions.update(subscription.id, {
    planId: newPlan.id,
    amount: newPlan.monthlyPrice
  });
}
```

### 3. Retry with Fallback Provider

```javascript
async function retryWithFallback(subscription) {
  const routing = await client.routePayment({
    amount: subscription.amount,
    currency: 'USD',
    destination: subscription.country,
    excludeProvider: subscription.provider  // Skip current provider
  });

  // Try new provider
  try {
    return await client.processPayment({
      provider: routing.recommendedProvider,
      ...subscription
    });
  } catch (error) {
    console.error('Fallback failed:', error);
    throw error;
  }
}
```

## Testing

### Test Case 1: Successful Renewal

```javascript
const subscription = {
  id: 'sub_123',
  customerId: 'cust_456',
  amount: 9900,  // $99/month
  nextBillDate: new Date()
};

// Expected: Payment processes, nextBillDate updated to 1 month later
```

### Test Case 2: Failed Payment (Retry)

```javascript
// Simulate payment failure
await processRecurringCharge(subscription);

// Expected:
// - failureCount = 1
// - Retry scheduled for 3 days
// - Retry email sent
```

### Test Case 3: Failed After Retries

```javascript
// Mark as 2 failed attempts
subscription.failureCount = 2;

// Process another failure
await processRecurringCharge(subscription);

// Expected:
// - failureCount = 3
// - Subscription cancelled
// - Cancellation email sent
```

## Webhook Events

```javascript
// Listen for subscription events
webhooks.on('subscription.renewed', (event) => {
  updateSubscriptionStatus(event.subscriptionId, 'active');
});

webhooks.on('subscription.payment_failed', (event) => {
  handlePaymentFailure(event.subscriptionId);
});

webhooks.on('subscription.cancelled', (event) => {
  offboardCustomer(event.customerId);
});
```

## Database Schema

```sql
CREATE TABLE subscriptions (
  id VARCHAR(255) PRIMARY KEY,
  customerId VARCHAR(255),
  planId VARCHAR(255),
  status VARCHAR(50),  -- active, suspended, cancelled
  amount INTEGER,
  currency VARCHAR(3),
  provider VARCHAR(50),
  nextBillDate TIMESTAMP,
  lastPaymentDate TIMESTAMP,
  failureCount INTEGER DEFAULT 0,
  lastError VARCHAR(500),
  createdAt TIMESTAMP,
  updatedAt TIMESTAMP
);
```

## See Also

- [Payment Routing Guide](../../docs/payment-routing.md)
- [Error Handling](error-handling.md)
- [Webhook Handling](webhooks.md)
