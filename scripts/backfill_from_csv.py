from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.backend.models.menu_item import MenuItem
from src.backend.models.order import Order, OrderLocation, OrderStatus
from src.backend.models.order_item import OrderItem
from src.backend.models.restaurant import Restaurant
from src.backend.models.review import Review
from src.backend.models.user import UserBase


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Backfill JSON seed files from food_delivery_db.csv with model validation."
    )
    parser.add_argument(
        "--csv",
        default=str(ROOT / "data" / "food_delivery_db.csv"),
        help="Path to source CSV dataset.",
    )
    parser.add_argument(
        "--user-db",
        default=str(ROOT / "data" / "user_db.json"),
        help="Path to user_db.json output.",
    )
    parser.add_argument(
        "--restaurants",
        default=str(ROOT / "data" / "restaurants.json"),
        help="Path to restaurants.json output.",
    )
    parser.add_argument(
        "--orders",
        default=str(ROOT / "data" / "orders.json"),
        help="Path to orders.json output.",
    )
    parser.add_argument(
        "--report",
        default="",
        help="Optional path for a JSON report file.",
    )
    parser.add_argument(
        "--max-orders",
        type=int,
        default=500,
        help="Maximum number of orders to create.",
    )
    parser.add_argument(
        "--password",
        default="Seed@123",
        help="Password for generated users. Must satisfy the model pattern.",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write to JSON files. Without this flag the script runs as dry run only.",
    )
    return parser.parse_args()


def read_rows(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return list(reader)


def to_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def to_int(value: str, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def normalize_text(value: str) -> str:
    value = (value or "").strip()
    value = re.sub(r"\s+", " ", value)
    return value


def normalize_food_name(value: str) -> str:
    value = normalize_text(value)
    fixes = {
        "Taccos": "Tacos",
        "Briyani rice": "Biryani Rice",
        "CoffeeBoba tea": "Coffee Boba Tea",
        "PastrySmoothie": "Pastry Smoothie",
        "Cup cake": "Cupcake",
    }
    if value in fixes:
        return fixes[value]
    return value.title()


def mode_or_default(values: list[str], default: str) -> str:
    cleaned = [normalize_text(v) for v in values if normalize_text(v)]
    if not cleaned:
        return default
    return Counter(cleaned).most_common(1)[0][0]


def city_to_province(city_value: str) -> str:
    province_codes = [loc.value for loc in OrderLocation]
    city_text = normalize_text(city_value)
    match = re.match(r"City_(\d+)", city_text)
    if not match:
        return OrderLocation.BRITISH_COLUMBIA.value
    index = int(match.group(1)) - 1
    return province_codes[index % len(province_codes)]


def make_users(
    rows: list[dict[str, str]], password: str
) -> tuple[list[dict[str, Any]], dict[str, int], dict[str, int]]:
    customer_keys = sorted({normalize_text(r.get("customer_id", "")) for r in rows if normalize_text(r.get("customer_id", ""))})
    restaurant_keys = sorted({normalize_text(r.get("restaurant_id", "")) for r in rows if normalize_text(r.get("restaurant_id", ""))})

    customer_id_map: dict[str, int] = {}
    owner_id_map: dict[str, int] = {}
    users: list[dict[str, Any]] = []

    next_id = 1

    for key in customer_keys:
        customer_id_map[key] = next_id
        user = {
            "id": next_id,
            "username": f"customer_{next_id:04d}",
            "email": f"customer_{next_id:04d}@seed.com",
            "password": password,
            "role": "customer",
            "is_logged_in": False,
            "is_blocked": False,
        }
        users.append(UserBase.model_validate(user).model_dump(mode="json"))
        next_id += 1

    for key in restaurant_keys:
        owner_id_map[key] = next_id
        user = {
            "id": next_id,
            "username": f"owner_{next_id:04d}",
            "email": f"owner_{next_id:04d}@seed.com",
            "password": password,
            "role": "restaurant owner",
            "is_logged_in": False,
            "is_blocked": False,
        }
        users.append(UserBase.model_validate(user).model_dump(mode="json"))
        next_id += 1

    return users, customer_id_map, owner_id_map


def build_restaurants(
    rows: list[dict[str, str]], owner_id_map: dict[str, int]
) -> tuple[list[dict[str, Any]], dict[str, int], dict[tuple[int, str], dict[str, Any]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        rid = normalize_text(row.get("restaurant_id", ""))
        if rid:
            grouped[rid].append(row)

    restaurants: list[dict[str, Any]] = []
    restaurant_id_map: dict[str, int] = {}
    menu_lookup: dict[tuple[int, str], dict[str, Any]] = {}

    sorted_keys = sorted(grouped.keys(), key=lambda x: int(x) if x.isdigit() else x)

    for new_id, src_rid in enumerate(sorted_keys, start=1):
        rows_for_restaurant = grouped[src_rid]

        cuisine = mode_or_default([r.get("preferred_cuisine", "") for r in rows_for_restaurant], "American")
        location = mode_or_default([r.get("location", "") for r in rows_for_restaurant], "City_1")
        avg_distance = sum(to_float(r.get("delivery_distance", "0"), 0.0) for r in rows_for_restaurant) / max(len(rows_for_restaurant), 1)
        delivery_fee = round(max(1.99, min(9.99, 1.49 + (avg_distance * 0.28))), 2)

        by_food: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in rows_for_restaurant:
            food_name = normalize_food_name(row.get("food_item", ""))
            if food_name:
                by_food[food_name].append(row)

        menu_items: list[dict[str, Any]] = []
        sorted_foods = sorted(by_food.keys())
        for menu_id, food_name in enumerate(sorted_foods, start=1):
            rows_for_food = by_food[food_name]
            avg_order_value = sum(to_float(r.get("order_value", "0"), 0.0) for r in rows_for_food) / max(len(rows_for_food), 1)
            price = round(max(4.5, min(24.99, avg_order_value * 0.38)), 2)

            menu_item = {
                "id": menu_id,
                "name": food_name,
                "description": f"{food_name} made fresh for delivery",
                "price": price,
            }
            validated_menu = MenuItem.model_validate(menu_item).model_dump(mode="json")
            menu_items.append(validated_menu)
            menu_lookup[(new_id, food_name)] = validated_menu

        restaurant = {
            "id": new_id,
            "name": f"Restaurant {new_id:03d}",
            "cuisine": cuisine.title(),
            "location": location,
            "delivery_fee": delivery_fee,
            "owner_id": owner_id_map[src_rid],
            "menu_items": menu_items,
            "is_available": bool(menu_items),
        }

        validated_restaurant = Restaurant.model_validate(restaurant).model_dump(mode="json")
        restaurants.append(validated_restaurant)
        restaurant_id_map[src_rid] = new_id

    return restaurants, restaurant_id_map, menu_lookup


def build_review(raw_rating: str, order_time: str, food_name: str) -> dict[str, Any] | None:
    rating = to_int(raw_rating, 0)
    if rating < 1 or rating > 5:
        return None

    ts = datetime.fromisoformat(order_time).replace(hour=12, minute=0, second=0, microsecond=0)

    title_map = {
        1: "Very bad",
        2: "Not great",
        3: "It was fine",
        4: "Pretty good",
        5: "Really good",
    }
    review = {
        "rating": rating,
        "title": title_map[rating],
        "comment": f"Ordered {food_name} and the meal matched the rating",
        "created_at": ts.isoformat(),
        "updated_at": ts.isoformat(),
    }
    return Review.model_validate(review).model_dump(mode="json")


def build_orders(
    rows: list[dict[str, str]],
    max_orders: int,
    customer_id_map: dict[str, int],
    restaurant_id_map: dict[str, int],
    restaurants: list[dict[str, Any]],
    menu_lookup: dict[tuple[int, str], dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    restaurants_by_id = {r["id"]: r for r in restaurants}

    orders: list[dict[str, Any]] = []
    rejects: list[dict[str, Any]] = []

    for row_index, row in enumerate(rows, start=2):
        if len(orders) >= max_orders:
            break

        src_customer = normalize_text(row.get("customer_id", ""))
        src_restaurant = normalize_text(row.get("restaurant_id", ""))
        order_time = normalize_text(row.get("order_time", ""))

        if src_customer not in customer_id_map:
            rejects.append({"row": row_index, "reason": "unknown customer_id"})
            continue
        if src_restaurant not in restaurant_id_map:
            rejects.append({"row": row_index, "reason": "unknown restaurant_id"})
            continue
        if not order_time:
            rejects.append({"row": row_index, "reason": "missing order_time"})
            continue

        try:
            timestamp = datetime.fromisoformat(order_time).replace(hour=12, minute=0, second=0, microsecond=0)
        except ValueError:
            rejects.append({"row": row_index, "reason": "invalid order_time"})
            continue

        restaurant_id = restaurant_id_map[src_restaurant]
        restaurant = restaurants_by_id[restaurant_id]

        food_name = normalize_food_name(row.get("food_item", ""))
        menu_item = menu_lookup.get((restaurant_id, food_name))
        if not menu_item:
            if restaurant["menu_items"]:
                menu_item = restaurant["menu_items"][0]
            else:
                rejects.append({"row": row_index, "reason": "no menu item available"})
                continue

        order_value = to_float(row.get("order_value", "0"), 0.0)
        unit_price = float(menu_item["price"])
        quantity = max(1, min(5, int(round(order_value / unit_price)) if unit_price > 0 else 1))

        order_item = {
            "item_id": menu_item["id"],
            "quantity": quantity,
            "price_at_purchase": unit_price,
        }
        validated_item = OrderItem.model_validate(order_item).model_dump(mode="json")

        subtotal = round(quantity * unit_price, 2)
        tax = round(subtotal * 0.05, 2)
        delivery_fee = float(restaurant["delivery_fee"])
        total = round(subtotal + tax + delivery_fee, 2)

        review = build_review(row.get("customer_rating", ""), order_time, menu_item["name"])

        order = {
            "id": len(orders) + 1,
            "customer_id": customer_id_map[src_customer],
            "restaurant_id": restaurant_id,
            "status": OrderStatus.PENDING.value,
            "location": city_to_province(row.get("location", "")),
            "order_items": [validated_item],
            "timestamp": timestamp.isoformat(),
            "subtotal_price": subtotal,
            "tax": tax,
            "delivery_fee": delivery_fee,
            "total_price": total,
            "review": review,
        }

        try:
            validated_order = Order.model_validate(order).model_dump(mode="json")
        except Exception as exc:
            rejects.append({"row": row_index, "reason": f"order validation failed: {exc}"})
            continue

        orders.append(validated_order)

    return orders, rejects


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=4), encoding="utf-8")


def main() -> None:
    args = parse_args()

    csv_path = Path(args.csv)
    user_db_path = Path(args.user_db)
    restaurants_path = Path(args.restaurants)
    orders_path = Path(args.orders)

    rows = read_rows(csv_path)
    if not rows:
        raise SystemExit("CSV has no data rows")

    users, customer_id_map, owner_id_map = make_users(rows, args.password)
    restaurants, restaurant_id_map, menu_lookup = build_restaurants(rows, owner_id_map)
    orders, rejects = build_orders(
        rows=rows,
        max_orders=args.max_orders,
        customer_id_map=customer_id_map,
        restaurant_id_map=restaurant_id_map,
        restaurants=restaurants,
        menu_lookup=menu_lookup,
    )

    report = {
        "source_csv": str(csv_path),
        "total_csv_rows": len(rows),
        "generated": {
            "users": len(users),
            "restaurants": len(restaurants),
            "orders": len(orders),
            "menu_items": sum(len(r["menu_items"]) for r in restaurants),
        },
        "rejects": {
            "count": len(rejects),
            "sample": rejects[:25],
        },
        "write_mode": bool(args.write),
        "targets": {
            "user_db": str(user_db_path),
            "restaurants": str(restaurants_path),
            "orders": str(orders_path),
        },
    }

    print(json.dumps(report, indent=2))

    if args.report:
        write_json(Path(args.report), report)

    if not args.write:
        print("Dry run complete. No files were modified. Use --write to persist data.")
        return

    write_json(user_db_path, {"Users": users})
    write_json(restaurants_path, restaurants)
    write_json(orders_path, orders)
    print("Write complete.")


if __name__ == "__main__":
    main()
