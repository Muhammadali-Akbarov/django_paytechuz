# PayTech UZ Django 💳

Simple Django REST API for creating orders with **Payme** and **Click** payment integration.

## 🚀 Quick Start

1. **Install dependencies:**

```bash
pip install -r requirements.txt
```

2. **Setup environment variables:**

```bash
cp .env.example .env
# Edit .env with your payment gateway credentials
```

3. **Run migrations:**

```bash
python manage.py migrate
```

4. **Start server:**

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

## 📋 API Usage

### Create Order

**POST** `/api/orders/create`

```json
{
  "product_name": "Test Product",
  "amount": "100.00",
  "payment_type": "payme"
}
```

**Response:**

```json
{
  "order_id": 1,
  "payment_url": "https://test.paycom.uz/...",
  "payment_type": "payme",
  "amount": "100.00",
  "status": "pending"
}
```

**Payment Types:**

- `payme` - Payme payment gateway
- `click` - Click payment gateway

## 🧪 Test with cURL

```bash
curl -X POST http://127.0.0.1:8000/api/orders/create \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Test Product",
    "amount": "100.00",
    "payment_type": "payme"
  }'
```

## ⚙️ Configuration

Create `.env` file with your payment gateway credentials:

```env
PAYME_ID=your_payme_id
PAYME_KEY=your_payme_key
CLICK_SERVICE_ID=your_service_id
CLICK_MERCHANT_ID=your_merchant_id
CLICK_MERCHANT_USER_ID=your_merchant_user_id
CLICK_SECRET_KEY=your_secret_key
```

## ✨ Features

- 💳 **Payme** payment gateway integration
- 🔗 **Click** payment gateway integration
- 🚀 Simple REST API
- ✅ Order management
- 🔒 Input validation & error handling
