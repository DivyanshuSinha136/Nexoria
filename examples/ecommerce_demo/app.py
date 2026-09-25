"""
Nexoria showcase: a small but real e-commerce site.

Demonstrates, in one app:
  - nexoria.style (Theme, Stylesheet, dark/light toggle, base classes)
  - nexoria.gsap (hero fade-in animation)
  - nexoria.iconify (cart/star/product icons)
  - nexoria.qrcode (order confirmation QR code)
  - State + plain server-side mutation, both driving real WebSocket-
    patched interactivity (add to cart, quantity steppers, checkout)
  - multi-page routing (catalog / product detail / cart / checkout)

Simplification, stated plainly: the cart is a single process-wide
in-memory store (not per-user session/cookie-scoped) -- correct and
simple for a showcase/demo running one visitor at a time. A real
multi-user storefront would key it off a session id instead.

Run:
    pip install nexoria
    cd examples/ecommerce_demo
    python app.py
    # open http://127.0.0.1:8000
"""

from nexoria import App, Component, el, State, Router, Stylesheet
from nexoria.style import theme_toggle_button
from nexoria.gsap import Tween, Timeline, Animation
from nexoria.iconify import Icon
from nexoria.qrcode import QRCode

from products import PRODUCTS, get_product

# --- process-wide demo store (see module docstring) -----------------------
CART: dict[int, int] = {}          # product_id -> quantity
ORDERS: dict[str, dict] = {}       # order_id -> {"items": [...], "total": float}
_next_order_num = [1000]


def cart_count() -> int:
    return sum(CART.values())


def cart_subtotal() -> float:
    total = 0.0
    for pid, qty in CART.items():
        product = get_product(pid)
        if product:
            total += product["price"] * qty
    return total


def money(amount: float) -> str:
    return f"${amount:,.2f}"


# --- shared styling ---------------------------------------------------------
styles = Stylesheet()
styles.add(".shop-grid", display="grid", grid_template_columns="repeat(auto-fill, minmax(240px, 1fr))", gap="20px")
styles.add(".product-icon", width="100%", height="140px", display="flex", align_items="center",
           justify_content="center", background="var(--nx-surface-alt)", border_radius="var(--nx-radius-sm)",
           font_size="48px", color="var(--nx-primary)", margin_bottom="14px")
styles.add(".price-tag", font_size="1.25rem", font_weight="700", color="var(--nx-text)")
styles.add(".cart-badge", position="relative")
styles.add(".cart-count", position="absolute", top="-6px", right="-8px", background="var(--nx-danger)",
           color="white", font_size="0.7rem", font_weight="700", border_radius="999px",
           padding="1px 6px", line_height="1.4")
styles.add(".cart-row", display="grid", grid_template_columns="64px 1fr auto auto", gap="16px",
           align_items="center", padding="14px 0", border_bottom="1px solid var(--nx-border)")
styles.add(".qty-stepper", display="inline-flex", align_items="center", gap="10px")


def Nav():
    return el("nav",
        el("a", el("span", "\u2b21 Nexoria Shop", class_="nx-brand"), href="/"),
        el("div",
            el("a", "Shop", href="/", class_="nx-btn-ghost nx-btn"),
            el("a",
                Icon("mdi:cart-outline", size="20px"),
                el("span", str(cart_count()), class_="cart-count") if cart_count() else None,
                href="/cart", class_="nx-btn nx-btn-ghost cart-badge",
            ),
            theme_toggle_button(),
            class_="nx-row",
        ),
        class_="nx-nav",
    )


def stars(rating: float):
    full = int(rating)
    return el("div",
        *[Icon("mdi:star", size="16px", color="#f5b400") for _ in range(full)],
        *[Icon("mdi:star-outline", size="16px", color="#f5b400") for _ in range(5 - full)],
        el("span", f" {rating}", style={"color": "var(--nx-text-muted)", "font_size": "0.85rem"}),
        class_="nx-row",
    )


class Shop(Component):
    styles = styles

    def render(self):
        hero_anim = Animation(
            Timeline(
                Tween(".hero-title", opacity=0, y=16, from_vars=True, duration=0.5, ease="power2.out"),
                Tween(".hero-sub", opacity=0, y=16, from_vars=True, duration=0.5, position="-=0.25"),
            ),
            name="shop-hero",
        )

        cards = []
        for p in PRODUCTS:
            cards.append(el("div",
                el("div", Icon(p["icon"], size="48px"), class_="product-icon"),
                el("span", p["category"], class_="nx-badge"),
                el("h3", p["name"], style={"margin": "10px 0 4px"}),
                stars(p["rating"]),
                el("p", p["description"], style={"color": "var(--nx-text-muted)", "font_size": "0.9rem", "margin": "8px 0"}),
                el("div",
                    el("span", money(p["price"]), class_="price-tag"),
                    el("a", "View", href=f"/product/{p['id']}", class_="nx-btn nx-btn-ghost"),
                    class_="nx-row", style={"justify_content": "space-between", "margin_top": "10px"},
                ),
                class_="nx-card",
            ))

        return el("div",
            Nav(),
            el("div",
                el("span", "New arrivals", class_="nx-badge hero-title"),
                el("h1", "Gear that keeps up with you", class_="hero-title"),
                el("p", "Curated electronics, shipped fast.", class_="hero-sub",
                   style={"color": "var(--nx-text-muted)", "margin_bottom": "28px"}),
                el("div", *cards, class_="shop-grid"),
                hero_anim.to_element(),
            ),
            class_="nx-container",
        )


class ProductDetail(Component):
    styles = styles

    def setup(self):
        self.state = State({"qty": 1})

    def render(self):
        product = get_product(int(self.props["id"]))
        if not product:
            return el("div", Nav(), el("div", el("h1", "Product not found"), class_="nx-container"))

        qty = self.state["qty"]

        return el("div",
            Nav(),
            el("div",
                el("a", "\u2190 Back to shop", href="/", style={"color": "var(--nx-text-muted)"}),
                el("div",
                    el("div", Icon(product["icon"], size="96px"), class_="product-icon", style={"height": "260px", "font_size": "96px"}),
                    el("div",
                        el("span", product["category"], class_="nx-badge"),
                        el("h1", product["name"]),
                        stars(product["rating"]),
                        el("p", product["description"], style={"color": "var(--nx-text-muted)", "margin": "12px 0"}),
                        el("p", money(product["price"]), class_="price-tag", style={"font_size": "1.75rem"}),
                        el("p", f"{product['stock']} in stock", style={"color": "var(--nx-text-muted)", "font_size": "0.85rem"}),
                        el("div",
                            el("button", "\u2212", class_="nx-btn nx-btn-ghost",
                               on_click=lambda e: self.state.update(qty=max(1, self.state["qty"] - 1))),
                            el("span", str(qty), style={"min_width": "24px", "text_align": "center"}),
                            el("button", "+", class_="nx-btn nx-btn-ghost",
                               on_click=lambda e: self.state.update(qty=min(product["stock"], self.state["qty"] + 1))),
                            class_="qty-stepper",
                        ),
                        el("button", "Add to cart", class_="nx-btn", style={"margin_top": "16px"},
                           on_click=lambda e: CART.__setitem__(product["id"], CART.get(product["id"], 0) + self.state["qty"])),
                        style={"display": "flex", "flex_direction": "column", "gap": "6px"},
                    ),
                    style={"display": "grid", "grid_template_columns": "1fr 1fr", "gap": "32px", "margin_top": "16px"},
                ),
                class_="nx-card",
            ),
            class_="nx-container",
        )


class CartPage(Component):
    styles = styles

    def render(self):
        rows = []
        for pid, qty in list(CART.items()):
            product = get_product(pid)
            if not product:
                continue

            def make_set_qty(pid=pid):
                def set_qty(new_qty):
                    if new_qty <= 0:
                        CART.pop(pid, None)
                    else:
                        CART[pid] = new_qty
                return set_qty
            set_qty = make_set_qty()

            rows.append(el("div",
                Icon(product["icon"], size="32px"),
                el("div",
                    el("strong", product["name"]),
                    el("div", money(product["price"]), style={"color": "var(--nx-text-muted)", "font_size": "0.85rem"}),
                ),
                el("div",
                    el("button", "\u2212", class_="nx-btn nx-btn-ghost", on_click=lambda e, f=set_qty, q=qty: f(q - 1)),
                    el("span", str(qty), style={"min_width": "20px", "text_align": "center"}),
                    el("button", "+", class_="nx-btn nx-btn-ghost", on_click=lambda e, f=set_qty, q=qty: f(q + 1)),
                    class_="qty-stepper",
                ),
                el("span", money(product["price"] * qty), class_="price-tag"),
                class_="cart-row",
            ))

        if not rows:
            body = el("div",
                Icon("mdi:cart-off", size="40px", color="var(--nx-text-muted)"),
                el("p", "Your cart is empty.", style={"color": "var(--nx-text-muted)"}),
                el("a", "Browse the shop", href="/", class_="nx-btn"),
                style={"display": "flex", "flex_direction": "column", "align_items": "center", "gap": "10px", "padding": "40px 0"},
            )
        else:
            body = el("div",
                *rows,
                el("div",
                    el("span", "Subtotal", style={"color": "var(--nx-text-muted)"}),
                    el("span", money(cart_subtotal()), class_="price-tag"),
                    class_="nx-row", style={"justify_content": "space-between", "margin_top": "16px"},
                ),
                el("a", "Proceed to checkout", href="/checkout", class_="nx-btn",
                   style={"width": "100%", "text_align": "center", "margin_top": "16px", "display": "block"}),
            )

        return el("div", Nav(), el("div", el("h1", "Your Cart"), body, class_="nx-card"), class_="nx-container")


class CheckoutPage(Component):
    styles = styles

    def setup(self):
        self.order_id = None

    def _place_order(self, payload):
        global _next_order_num
        if not CART:
            return
        items = []
        for pid, qty in CART.items():
            product = get_product(pid)
            if product:
                items.append({"name": product["name"], "qty": qty, "price": product["price"]})
        order_id = f"NX-{_next_order_num[0]}"
        _next_order_num[0] += 1
        ORDERS[order_id] = {"items": items, "total": cart_subtotal()}
        CART.clear()
        self.order_id = order_id

    def render(self):
        if self.order_id:
            order = ORDERS[self.order_id]
            qr = QRCode(f"ORDER:{self.order_id}", size=160, dot_color="#6366f1")
            return el("div", Nav(),
                el("div",
                    Icon("mdi:check-circle", size="48px", color="var(--nx-success)"),
                    el("h1", "Order placed!"),
                    el("p", f"Order {self.order_id} \u00b7 {money(order['total'])}", style={"color": "var(--nx-text-muted)"}),
                    qr.to_element(),
                    el("p", "Scan to track your order.", style={"color": "var(--nx-text-muted)", "font_size": "0.85rem"}),
                    el("a", "Back to shop", href="/", class_="nx-btn"),
                    style={"display": "flex", "flex_direction": "column", "align_items": "center", "gap": "12px", "padding": "20px 0"},
                ),
                class_="nx-card", style={"max_width": "480px", "margin": "0 auto"},
            )

        if not CART:
            return el("div", Nav(), el("div", el("h1", "Nothing to check out"),
                       el("a", "Browse the shop", href="/", class_="nx-btn")), class_="nx-container")

        lines = []
        for pid, qty in CART.items():
            product = get_product(pid)
            if product:
                lines.append(el("div",
                    el("span", f"{product['name']} \u00d7 {qty}"),
                    el("span", money(product["price"] * qty)),
                    class_="nx-row", style={"justify_content": "space-between", "padding": "6px 0"},
                ))

        return el("div", Nav(),
            el("div",
                el("h1", "Checkout"),
                *lines,
                el("div",
                    el("strong", "Total"),
                    el("span", money(cart_subtotal()), class_="price-tag"),
                    class_="nx-row", style={"justify_content": "space-between", "margin": "16px 0", "border_top": "1px solid var(--nx-border)", "padding_top": "12px"},
                ),
                el("button", "Place order", class_="nx-btn", style={"width": "100%"}, on_click=self._place_order),
                class_="nx-card",
            ),
            class_="nx-container", style={"max_width": "480px", "margin": "0 auto"},
        )


router = Router()
router.add("/", Shop)
router.add("/product/:id", ProductDetail)
router.add("/cart", CartPage)
router.add("/checkout", CheckoutPage)

app = App(
    name="Nexoria Shop",
    router=router,
    gsap=True,
    iconify=True,
    qrcode=True,
    description="A small electronics storefront built with Nexoria.",
    debug=True,
)

if __name__ == "__main__":
    app.run(reload=True)
