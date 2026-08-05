import crud
import models
import schemas


def _make_category(db_session, name="Warhammer 40K"):
    return crud.create_category(db_session, schemas.CategoryCreate(name=name))


def _make_product(db_session, category_id, **overrides):
    defaults = dict(
        name="Space Marine Tactical Squad",
        price=45.0,
        cost_price=20.0,
        sku="SM-TAC-001",
        stock_quantity=10,
        min_stock_level=5,
        category_id=category_id,
    )
    defaults.update(overrides)
    return crud.create_product(db_session, schemas.ProductCreate(**defaults))


def test_create_user_hashes_password_and_can_be_fetched_by_email(db_session):
    crud.create_user(
        db_session,
        schemas.UserCreate(email="new@example.com", password="plaintext", full_name="New User"),
    )

    user = crud.get_user_by_email(db_session, "new@example.com")

    assert user is not None
    assert user.hashed_password != "plaintext"
    assert user.is_admin is False


def test_create_product_and_get_products_filters_by_category(db_session):
    cat_a = _make_category(db_session, "Warhammer 40K")
    cat_b = _make_category(db_session, "Age of Sigmar")
    _make_product(db_session, cat_a.id, sku="SKU-A")
    _make_product(db_session, cat_b.id, sku="SKU-B")

    products_in_a = crud.get_products(db_session, category_id=cat_a.id)

    assert len(products_in_a) == 1
    assert products_in_a[0].sku == "SKU-A"


def test_get_low_stock_products_only_returns_products_at_or_below_threshold(db_session):
    category = _make_category(db_session)
    _make_product(db_session, category.id, sku="LOW-STOCK", stock_quantity=2, min_stock_level=5)
    _make_product(db_session, category.id, sku="HIGH-STOCK", stock_quantity=50, min_stock_level=5)

    low_stock = crud.get_low_stock_products(db_session)

    skus = {p.sku for p in low_stock}
    assert "LOW-STOCK" in skus
    assert "HIGH-STOCK" not in skus


def test_add_to_cart_aggregates_quantity_for_same_product(db_session):
    category = _make_category(db_session)
    product = _make_product(db_session, category.id)

    crud.add_to_cart(db_session, user_id=1, cart_item=schemas.CartItemCreate(product_id=product.id, quantity=2))
    crud.add_to_cart(db_session, user_id=1, cart_item=schemas.CartItemCreate(product_id=product.id, quantity=3))

    items = crud.get_cart_items(db_session, user_id=1)

    assert len(items) == 1
    assert items[0].quantity == 5


def test_create_order_reduces_stock_creates_sale_and_clears_cart(db_session):
    category = _make_category(db_session)
    product = _make_product(db_session, category.id, stock_quantity=10)
    crud.create_user(db_session, schemas.UserCreate(email="buyer@example.com", password="pw"))
    user = crud.get_user_by_email(db_session, "buyer@example.com")

    crud.add_to_cart(db_session, user_id=user.id, cart_item=schemas.CartItemCreate(product_id=product.id, quantity=3))

    order = crud.create_order(
        db_session,
        user_id=user.id,
        order=schemas.OrderCreate(shipping_address={"city": "Santiago"}),
    )

    refreshed_product = crud.get_product(db_session, product.id)
    sales = db_session.query(models.Sale).all()

    assert order is not None
    assert order.total_amount == product.price * 3
    assert refreshed_product.stock_quantity == 7
    assert len(sales) == 1
    assert sales[0].quantity == 3
    assert crud.get_cart_items(db_session, user_id=user.id) == []


def test_create_order_returns_none_when_cart_is_empty(db_session):
    crud.create_user(db_session, schemas.UserCreate(email="buyer2@example.com", password="pw"))
    user = crud.get_user_by_email(db_session, "buyer2@example.com")

    order = crud.create_order(
        db_session,
        user_id=user.id,
        order=schemas.OrderCreate(shipping_address={"city": "Santiago"}),
    )

    assert order is None
