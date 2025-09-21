from bluer_objects.README.items import ImageItems
from bluer_ugv.README.consts import algo_docs, assets2_bluer_swallow
from bluer_ugv.README.swallow.digital.algo.navigation import items as navigation_items
from bluer_ugv.README.swallow.digital.algo.yolo import items as yolo_items

items = (
    [
        {
            "path": "../docs/bluer_swallow/digital/algo",
        },
        {
            "path": "../docs/bluer_swallow/digital/algo/driving.md",
        },
    ]
    + navigation_items
    + [
        {
            "path": "../docs/bluer_swallow/digital/algo/tracking",
            "items": ImageItems(
                {
                    f"{assets2_bluer_swallow}/target-selection.png": f"{algo_docs}/socket.md",
                }
            ),
        }
    ]
    + yolo_items
)
