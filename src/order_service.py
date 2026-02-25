from typing import List, Sequence, TypedDict, Union, Required

class Order(TypedDict, total=False):
    id: Required[int]
    amount: int
    priority: bool

class ProcessedOrderBase(TypedDict):
    id: int
    status: str

class ProcessedOrderOk(ProcessedOrderBase):
    priority: bool

class ProcessedOrderError(ProcessedOrderBase):
    pass

ProcessedOrder = Union[ProcessedOrderOk, ProcessedOrderError]

def _is_invalid_amount(order: Order) -> bool:
    amount = order.get("amount")
    return amount is None or amount <= 0

def _build_error_order(order: Order) -> ProcessedOrderError:
    return {
        "id": order.get("id"),
        "status": "error",
    }

def _build_ok_order(order: Order) -> ProcessedOrderOk:
    return {
     "id": order["id"],
        "status": "ok",
        "priority": bool(order.get("priority", False)),
    }

def _sort_orders_for_processing(orders: Sequence[Order]) -> List[Order]:
    """
    Ensure that orders with the priority flag are processed first.
    """
    return sorted(orders, key=lambda o: bool(o.get("priority", False)), reverse=True)

def process_orders(orders: Sequence[Order]) -> List[ProcessedOrder]:
    """
    Process incoming orders and return typed processed orders.
    """
    sorted_orders = _sort_orders_for_processing(orders)
    results: List[ProcessedOrder] = []

    for order in sorted_orders:
        if "id" not in order:
            results.append(_build_error_order(order))
        elif _is_invalid_amount(order):
            results.append(_build_error_order(order))
        else:
            results.append(_build_ok_order(order))

    return results

def process_data(items: Sequence[Order]) -> List[ProcessedOrder]:
    """
    Public API used by callers and tests.
    """
    return process_orders(items)

