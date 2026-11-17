
from decimal import Decimal, ROUND_HALF_UP

ZERO = Decimal('0')
FOURPLACES = Decimal('0.0001')
TWOPLACES = Decimal('0.01')


def signed_quantity(movement_type: str, quantity: Decimal) -> Decimal:
    quantity = Decimal(quantity)
    if quantity <= 0:
        raise ValueError('Movement quantity must be greater than zero')
    if movement_type in {'receipt', 'transfer_in', 'adjustment_in', 'opening'}:
        return quantity
    if movement_type in {'issue', 'transfer_out', 'adjustment_out'}:
        return -quantity
    raise ValueError('Unsupported inventory movement type')


def apply_movement(on_hand: Decimal, movement_type: str, quantity: Decimal, allow_negative: bool = False) -> Decimal:
    updated = Decimal(on_hand) + signed_quantity(movement_type, quantity)
    if updated < 0 and not allow_negative:
        raise ValueError('Inventory movement would create negative stock')
    return updated.quantize(FOURPLACES)


def weighted_average(current_quantity: Decimal, current_average: Decimal, receipt_quantity: Decimal, receipt_unit_cost: Decimal):
    current_quantity = Decimal(current_quantity); current_average = Decimal(current_average)
    receipt_quantity = Decimal(receipt_quantity); receipt_unit_cost = Decimal(receipt_unit_cost)
    if current_quantity < 0 or current_average < 0 or receipt_quantity <= 0 or receipt_unit_cost < 0:
        raise ValueError('Invalid weighted-average valuation inputs')
    new_quantity = current_quantity + receipt_quantity
    new_value = current_quantity * current_average + receipt_quantity * receipt_unit_cost
    average = (new_value / new_quantity).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
    return new_quantity.quantize(FOURPLACES), average, new_value.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def issue_value(quantity: Decimal, average_cost: Decimal):
    quantity = Decimal(quantity); average_cost = Decimal(average_cost)
    if quantity <= 0 or average_cost < 0:
        raise ValueError('Invalid issue valuation inputs')
    return (quantity * average_cost).quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def transfer_quantities(source_on_hand: Decimal, quantity: Decimal):
    source_after = apply_movement(source_on_hand, 'transfer_out', quantity)
    return source_after, Decimal(quantity).quantize(FOURPLACES)


def reorder_status(on_hand: Decimal, reserved: Decimal, reorder_point: Decimal, reorder_quantity: Decimal):
    on_hand = Decimal(on_hand); reserved = Decimal(reserved)
    reorder_point = Decimal(reorder_point); reorder_quantity = Decimal(reorder_quantity)
    if min(on_hand, reserved, reorder_point, reorder_quantity) < 0:
        raise ValueError('Reorder inputs cannot be negative')
    available = on_hand - reserved
    needs_reorder = available <= reorder_point
    suggested = reorder_quantity if needs_reorder else ZERO
    return available.quantize(FOURPLACES), needs_reorder, suggested.quantize(FOURPLACES)


def validate_tracking(tracking_mode: str, quantity: Decimal, lot_number: str | None, serial_number: str | None):
    quantity = Decimal(quantity)
    if tracking_mode == 'none': return
    if tracking_mode == 'lot' and not (lot_number or '').strip():
        raise ValueError('Lot number is required for lot-tracked items')
    if tracking_mode == 'serial':
        if not (serial_number or '').strip(): raise ValueError('Serial number is required for serial-tracked items')
        if quantity != 1: raise ValueError('Serial-tracked movements must have quantity 1')
    if tracking_mode not in {'none', 'lot', 'serial'}:
        raise ValueError('Unsupported tracking mode')
