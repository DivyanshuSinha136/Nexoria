"""Sample product catalog for the Nexoria e-commerce demo."""

PRODUCTS = [
    {
        "id": 1, "name": "Aurora Wireless Headphones", "price": 129.00,
        "category": "Audio", "icon": "mdi:headphones", "rating": 4.6, "stock": 14,
        "description": "Over-ear wireless headphones with adaptive noise cancellation and 30-hour battery life.",
    },
    {
        "id": 2, "name": "Nimbus Mechanical Keyboard", "price": 89.00,
        "category": "Accessories", "icon": "mdi:keyboard", "rating": 4.8, "stock": 22,
        "description": "Hot-swappable mechanical keyboard with per-key RGB and a machined aluminum frame.",
    },
    {
        "id": 3, "name": "Solace Smart Watch", "price": 199.00,
        "category": "Wearables", "icon": "mdi:watch", "rating": 4.3, "stock": 7,
        "description": "Fitness tracking, sleep analysis, and a always-on AMOLED display, 5 ATM water resistant.",
    },
    {
        "id": 4, "name": "Drift Portable Speaker", "price": 59.00,
        "category": "Audio", "icon": "mdi:speaker", "rating": 4.4, "stock": 31,
        "description": "Pocket-sized speaker with surprisingly big sound and 12 hours of playtime.",
    },
    {
        "id": 5, "name": "Vertex Ultrawide Monitor", "price": 449.00,
        "category": "Displays", "icon": "mdi:monitor", "rating": 4.7, "stock": 5,
        "description": "34-inch curved ultrawide, 144Hz, USB-C with 90W power delivery.",
    },
    {
        "id": 6, "name": "Cove Desk Lamp", "price": 39.00,
        "category": "Accessories", "icon": "mdi:desk-lamp", "rating": 4.2, "stock": 40,
        "description": "Adjustable color temperature LED lamp with a wireless charging base.",
    },
]


def get_product(product_id: int):
    return next((p for p in PRODUCTS if p["id"] == product_id), None)
