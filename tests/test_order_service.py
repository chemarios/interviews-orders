# tests/test_order_service.py
from typing import List, cast, Sequence
from src.order_service import Order, ProcessedOrder, ProcessedOrderOk, process_data


def test_ok_basic():
    data: List[Order] = [{"id": 1, "amount": 100}]
    out: List[ProcessedOrder] = process_data(data)
    assert out[0]["status"] == "ok"
    ok_result = cast(ProcessedOrderOk, out[0])
    assert ok_result["priority"] is False


def test_error_amount_zero():
    data: List[Order] = [{"id": 2, "amount": 0}]
    out: List[ProcessedOrder] = process_data(data)
    assert out[0]["status"] == "error"
    assert "priority" not in out[0]


def test_error_amount_negative():
    data: List[Order] = [{"id": 3, "amount": -5}]
    out: List[ProcessedOrder] = process_data(data)
    assert out[0]["status"] == "error"


def test_error_amount_missing():
    data: List[Order] = [{"id": 4}]
    out: List[ProcessedOrder] = process_data(data)
    assert out[0]["status"] == "error"


def test_priority_orders_are_first():
    data: List[Order] = [
        {"id": 1, "amount": 100, "priority": True},
        {"id": 2, "amount": 100, "priority": False},
        {"id": 3, "amount": 100, "priority": True},
    ]
    out: List[ProcessedOrder] = process_data(data)

    # Priority first
    assert out[0]["id"] == 1
    assert out[0]["status"] == "ok"
    ok_result = cast(ProcessedOrderOk, out[0])
    assert ok_result["priority"] is True

    # Non-priority orders at the end, preserving relative order
    assert [o["id"] for o in out[1:]] == [3, 2]
    for o in out[1:]:
        if o["id"] == 3:
            assert o["status"] == "ok"
            ok_o = cast(ProcessedOrderOk, o)
            assert ok_o["priority"] is True
        else:
            assert o["status"] == "ok"
            ok_o = cast(ProcessedOrderOk, o)
            assert ok_o["priority"] is False


def test_accepts_sequence_not_only_list():
    data = (
        {"id": 1, "amount": 100},
        {"id": 2, "amount": 50, "priority": True},
    )
    out: List[ProcessedOrder] = process_data(cast(Sequence[Order], data))
    assert len(out) == 2


# Additional edge case tests

def test_empty_list():
    data: List[Order] = []
    out: List[ProcessedOrder] = process_data(data)
    assert out == []


def test_single_order_priority_true():
    data: List[Order] = [{"id": 1, "amount": 100, "priority": True}]
    out: List[ProcessedOrder] = process_data(data)
    assert out[0]["status"] == "ok"
    ok_result = cast(ProcessedOrderOk, out[0])
    assert ok_result["priority"] is True


def test_single_order_priority_false():
    data: List[Order] = [{"id": 1, "amount": 100, "priority": False}]
    out: List[ProcessedOrder] = process_data(data)
    assert out[0]["status"] == "ok"
    ok_result = cast(ProcessedOrderOk, out[0])
    assert ok_result["priority"] is False


def test_mixed_valid_and_invalid_orders():
    data: List[Order] = [
        {"id": 1, "amount": 100},  # valid, non-priority
        {"id": 2, "amount": 0},    # invalid, non-priority
        {"id": 3, "amount": -10}, # invalid, non-priority
        {"id": 4, "amount": 50, "priority": True},  # valid, priority        
    ]
    out: List[ProcessedOrder] = process_data(data)
    # Sorted: priority first, then non-priority
    # Priority: id4, then non-priority: id1, id2, id3
    assert len(out) == 4
    assert out[0]["id"] == 4
    assert out[0]["status"] == "ok"
    ok_result = cast(ProcessedOrderOk, out[0])
    assert ok_result["priority"] is True
    assert out[1]["id"] == 1
    assert out[1]["status"] == "ok"
    assert out[2]["id"] == 2
    assert out[2]["status"] == "error"
    assert out[3]["id"] == 3
    assert out[3]["status"] == "error"


def test_duplicate_ids():
    data: List[Order] = [
        {"id": 1, "amount": 100},
        {"id": 1, "amount": 200},
    ]
    out: List[ProcessedOrder] = process_data(data)
    assert len(out) == 2
    assert all(o["id"] == 1 for o in out)
    assert all(o["status"] == "ok" for o in out)


def test_missing_id():
    data = [{"amount": 100}]  # missing id
    out: List[ProcessedOrder] = process_data(cast(List[Order], data))
    assert len(out) == 1
    assert out[0]["id"] is None
    assert out[0]["status"] == "error"


def test_all_priority_true():
    data: List[Order] = [
        {"id": 1, "amount": 100, "priority": True},
        {"id": 2, "amount": 200, "priority": True},
    ]
    out: List[ProcessedOrder] = process_data(data)
    assert len(out) == 2
    assert [o["id"] for o in out] == [1, 2]  # order preserved
    for o in out:
        assert o["status"] == "ok"
        ok_o = cast(ProcessedOrderOk, o)
        assert ok_o["priority"] is True


def test_all_priority_false():
    data: List[Order] = [
        {"id": 1, "amount": 100, "priority": False},
        {"id": 2, "amount": 200, "priority": False},
    ]
    out: List[ProcessedOrder] = process_data(data)
    assert len(out) == 2
    assert [o["id"] for o in out] == [1, 2]
    for o in out:
        assert o["status"] == "ok"
        ok_o = cast(ProcessedOrderOk, o)
        assert ok_o["priority"] is False


def test_large_amount():
    data: List[Order] = [{"id": 1, "amount": 1000000}]
    out: List[ProcessedOrder] = process_data(data)
    assert out[0]["status"] == "ok"


def test_amount_as_float():
    # Assuming amount should be int, but test if it handles float
    data = [{"id": 1, "amount": 100.0}]
    out: List[ProcessedOrder] = process_data(cast(List[Order], data))
    assert out[0]["status"] == "ok"  # since 100.0 > 0


def test_amount_none_explicit():
    data = [{"id": 1, "amount": None}]
    out: List[ProcessedOrder] = process_data(cast(List[Order], data))
    assert out[0]["status"] == "error"
