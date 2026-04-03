# PayPal Commerce Platform Setup Guide

## Quick Start

Your live_portal now has the expanded checkout system with PayPal Commerce Platform integration. Follow these steps to get it working:

## Step 1: Get PayPal Credentials

1. Go to https://developer.paypal.com
2. Log in with your PayPal account (or create one)
3. In the sidebar, click **Apps & Credentials**
4. Make sure you're on the **Sandbox** tab (for testing)
5. Under "Default Application", copy:
   - **Client ID**
   - **Secret**

## Step 2: Set Environment Variables

Before running your portal, set these environment variables (for **OpAutoClicker.shop**):

### On Windows (PowerShell):
```powershell
$env:PAYPAL_CLIENT_ID="your-client-id-here"
$env:PAYPAL_CLIENT_SECRET="your-client-secret-here"
$env:PAYPAL_API_SANDBOX="1"
$env:PORTAL_PUBLIC_BASE_URL="https://OpAutoClicker.shop"
```

### On Windows (Command Prompt):
```cmd
set PAYPAL_CLIENT_ID=your-client-id-here
set PAYPAL_CLIENT_SECRET=your-client-secret-here
set PAYPAL_API_SANDBOX=1
set PORTAL_PUBLIC_BASE_URL=https://OpAutoClicker.shop
```

### On Linux/Mac:
```bash
export PAYPAL_CLIENT_ID="your-client-id-here"
export PAYPAL_CLIENT_SECRET="your-client-secret-here"
export PAYPAL_API_SANDBOX="1"
export PORTAL_PUBLIC_BASE_URL="https://OpAutoClicker.shop"
```

## Step 3: Start the Portal

```bash
python app.py
```

Then navigate to: **https://OpAutoClicker.shop** (or your server's configured port)

## Step 4: Test the Checkout Flow

1. Click **Pricing** link
2. Log in (or register)
3. Click **Add to Cart** on any plan
4. Click **View Shopping Cart**
5. Click **Proceed to Checkout**
6. Click **Pay with PayPal**
7. You'll be redirected to PayPal's sandbox
8. Complete test payment

## Features Available

✅ **Shopping Cart** - Add multiple plans before checkout
✅ **PayPal Methods** - PayPal, Venmo, Pay Later, Credit Cards
✅ **Auto-Renewal** - Optional per plan
✅ **Instant Activation** - License keys issued immediately
✅ **NO REFUNDS Policy** - Prominently displayed everywhere
✅ **Fee Calculation** - Auto-adds PayPal fees (2.2% + $0.30)

## Production Setup

When ready to go live with real payments:

### Step 1: Switch to Production Credentials
Get your live PayPal credentials from https://developer.paypal.com (**Live** tab)

### Step 2: Update Credentials for Production
```powershell
$env:PAYPAL_CLIENT_ID="your-live-client-id"
$env:PAYPAL_CLIENT_SECRET="your-live-client-secret"
$env:PAYPAL_API_SANDBOX="0"  # Switch to production
$env:PORTAL_PUBLIC_BASE_URL="https://OpAutoClicker.shop"
```

### Step 3: Test with Live Endpoint
- Users will see real PayPal checkout
- Payments go to your actual business account
- No sandbox watermarks
- Domain will be https://OpAutoClicker.shop for PayPal redirects

## Troubleshooting

### "PayPal not configured"
- Check your environment variables are set
- Verify `PAYPAL_CLIENT_ID` and `PAYPAL_CLIENT_SECRET` are correct
- Restart the app after setting variables

### Order creation fails
- Check cart has items and total > 0
- Verify `PORTAL_PUBLIC_BASE_URL` is correct
- Verify PayPal credentials in production/sandbox environment

### Users not auto-activated
- Check email configuration if SMTP is enabled
- Verify `AUTO_APPROVE_PAID_WITH_PAYMENT_REF=True` in app.py
- Check database for purchase records (should be "approved" status)

### Payment Methods Not Showing
- Make sure you're using PayPal Business account
- Check your PayPal customer wallet settings
- Verify Venmo is linked to your PayPal account (for Venmo payments)

## Database Auto-Upgrade

The system automatically creates these new tables on first run:
- `carts` - Shopping cart per user
- `cart_items` - Items in cart
- No manual migration needed

## API Endpoints

### Cart Management
- `POST /api/cart/add` - Add item
- `POST /api/cart/remove` - Remove item
- `POST /api/cart/clear` - Clear cart
- `GET /cart` - View cart page

### Checkout
- `GET /checkout` - Checkout review page
- `POST /api/checkout/paypal` - Create PayPal order
- `GET /paypal/return-checkout` - Success return
- `GET /paypal/cancel-checkout` - Cancel return

## Configuration Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `PAYPAL_CLIENT_ID` | (empty) | Your PayPal app client ID |
| `PAYPAL_CLIENT_SECRET` | (empty) | Your PayPal app secret |
| `PAYPAL_API_SANDBOX` | `1` | Use sandbox (1) or production (0) |
| `PAYPAL_CURRENCY` | `USD` | Currency code (USD, EUR, etc.) |
| `PORTAL_PUBLIC_BASE_URL` | (empty) | Public domain for redirect URLs |
| `PAYPAL_BUSINESS` | blakeg716@hotmail.com | Legacy PayPal email (for direct checkout) |

## Next Steps

1. ✅ Configure PayPal credentials
2. ✅ Test checkout flow with sandbox
3. ✅ Verify license activation works
4. ✅ Test auto-renewal settings
5. ✅ Switch to production credentials
6. ✅ Launch!

## Support

For issues:
- Check `portal.db` for purchase records
- Review app logs for errors
- Contact PayPal support for transaction issues
- Email production contact for account issues

---

**Happy selling! Your expanded checkout is ready to accept payments.** 💳