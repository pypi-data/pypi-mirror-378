from bluer_ugv.swallow.README import items
from bluer_ugv.README.swallow.analog import items as items_analog
from bluer_ugv.README.swallow.digital import items as items_digital

docs = (
    [
        {
            "items": items,
            "path": "../docs/bluer_swallow",
        }
    ]
    + items_analog
    + items_digital
)
