# Atmos Payment Integration - Complete Guide

Bu loyihada Atmos to'lov tizimi to'liq integratsiya qilingan. Shop app bilan birgalikda ishlaydi va payment link yaratish + webhook orqali to'lov holatini kuzatish imkonini beradi.

## 🎯 Qanday Ishlaydi

1. **Order yaratish** - Foydalanuvchi mahsulot buyurtma qiladi
2. **Payment link yaratish** - Atmos da to'lov linki yaratiladi  
3. **To'lov sahifasiga yo'naltirish** - Foydalanuvchi Atmos sahifasida to'lov qiladi
4. **Webhook qabul qilish** - To'lov holatini webhook orqali kuzatamiz
5. **Order statusini yangilash** - Muvaffaqiyatli to'lovdan keyin Order "paid" holatiga o'tadi

## 📁 Fayl Tuzilishi

```
├── atmos/                          # Atmos payment app
│   ├── models.py                   # AtmosTransaction modeli
│   ├── services.py                 # Atmos API bilan ishlash
│   ├── views.py                    # Payment link + webhook views
│   ├── serializers.py              # API serializers
│   ├── urls.py                     # URL routing
│   └── admin.py                    # Django admin
├── shop/                           # Shop app (yangilangan)
│   ├── models.py                   # Order modeli (atmos payment type qo'shildi)
│   └── views.py                    # Order yaratish + Atmos integratsiyasi
└── test_shop_atmos.py              # To'liq integration test
```

## 🔧 Konfiguratsiya

### 1. Settings.py

```python
INSTALLED_APPS = [
    # ... boshqa applar
    'atmos',
]

# Atmos konfiguratsiyasi (Base URL hard coded: https://partner.atmos.uz)
ATMOS = {
    'CONSUMER_KEY': 'your_consumer_key',
    'CONSUMER_SECRET': 'your_consumer_secret',
    'STORE_ID': 'your_store_id',
    'TERMINAL_ID': 'your_terminal_id',
    'API_KEY': 'your_api_key_for_webhook_signature',
    'IS_TEST_MODE': True,
}
```

### 2. Environment Variables (.env)

```
# Base URL is hard coded as https://partner.atmos.uz
ATMOS_CONSUMER_KEY=your_atmos_consumer_key
ATMOS_CONSUMER_SECRET=your_atmos_consumer_secret
ATMOS_STORE_ID=your_atmos_store_id
ATMOS_TERMINAL_ID=your_atmos_terminal_id
ATMOS_API_KEY=your_api_key_for_webhook_signature
ATMOS_TEST_MODE=True
```

### 3. URLs (backend/urls.py)

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shop.urls')),
    path('', include('payment.urls')),
    path('atmos/', include('atmos.urls')),  # Atmos URLs
]
```

## 🚀 API Endpoints

### 1. Order Yaratish (Atmos Payment bilan)

**POST** `/api/orders/create`

```json
{
    "product_name": "Test Product",
    "amount": "50.00",
    "payment_type": "atmos"
}
```

**Response:**
```json
{
    "order_id": 1,
    "payment_url": "https://test-checkout.pays.uz/invoice/get?storeId=1234&transactionId=123456",
    "payment_type": "atmos",
    "amount": "50.00",
    "status": "pending"
}
```

### 2. Webhook Endpoint (Internal)

**POST** `/atmos/webhook/`

Atmos tomonidan avtomatik yuboriladi:
```json
{
    "store_id": "1234",
    "transaction_id": 123456,
    "transaction_time": "1656326529324",
    "amount": 5000,
    "invoice": "1",
    "sign": "digital_signature"
}
```

**Eslatma:** Bu endpoint faqat Atmos tomonidan ishlatiladi, frontend dan chaqirilmaydi.

## 🔄 To'lov Jarayoni

1. **Frontend:** Order yaratish so'rovi yuboradi
2. **Backend:** Order yaratiladi va Atmos payment link yaratiladi
3. **Frontend:** Foydalanuvchini payment_url ga yo'naltiradi
4. **Atmos:** Foydalanuvchi to'lov qiladi
5. **Atmos:** Webhook yuboradi
6. **Backend:** Order statusini "paid" ga yangilaydi

## 🧪 Test Qilish

### 1. To'liq Integration Test

```bash
python test_shop_atmos.py
```

### 2. Alohida Atmos Test

```bash
python atmos/test_payment.py
```

### 3. Manual Test

1. **Order yarating:**
```bash
curl -X POST http://localhost:8000/api/orders/create \
  -H "Content-Type: application/json" \
  -d '{"product_name": "Test", "amount": "50.00", "payment_type": "atmos"}'
```

2. **Payment URL ga tashrif buyuring**

3. **Webhook simulate qiling:**
```bash
curl -X POST http://localhost:8000/atmos/webhook/ \
  -H "Content-Type: application/json" \
  -d '{"store_id": "1234", "transaction_id": 123456, "amount": 5000, "invoice": "1", "sign": "test"}'
```

## 📊 Database Models

### AtmosTransaction
```python
class AtmosTransaction(models.Model):
    transaction_id = models.BigIntegerField(unique=True, null=True, blank=True)
    account = models.CharField(max_length=255)  # Order ID
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_url = models.URLField(max_length=500, null=True, blank=True)
    status = models.CharField(max_length=20, default='created')
    webhook_received_at = models.DateTimeField(null=True, blank=True)
```

### Order (yangilangan)
```python
class Order(models.Model):
    PAYMENT_TYPE_CHOICES = (
        ('payme', 'Payme'),
        ('click', 'Click'),
        ('atmos', 'Atmos'),  # Yangi qo'shildi
    )
    # ... boshqa fieldlar
```

## 🔒 Xavfsizlik

1. **Environment Variables:** Barcha kalitlar .env faylda
2. **Webhook Signature:** Atmos webhook signature tekshirish (implement qilish kerak)
3. **HTTPS:** Production da majburiy
4. **CSRF:** Webhook endpoint uchun o'chirilgan

## 📝 Keyingi Qadamlar

1. **Webhook signature verification** - Atmos dokumentatsiyasiga ko'ra
2. **Error handling** - To'lov xatoliklari uchun
3. **Logging** - To'lov jarayonini kuzatish
4. **Testing** - Unit va integration testlar
5. **Monitoring** - To'lov statistikasi

## 🎉 Xulosa

Atmos payment integration tayyor! 

- ✅ Order yaratish bilan integratsiya
- ✅ Payment link yaratish
- ✅ Webhook handling
- ✅ Order status yangilash
- ✅ Test scriptlar

Endi production da ishlatish uchun faqat haqiqiy Atmos kalitlarini o'rnatish va webhook signature verification qo'shish kerak.
