from bluer_objects.README.items import ImageItems
from bluer_ugv.README.consts import assets2, assets2_bluer_swallow
from bluer_ugv.parts.db import db_of_parts
from bluer_ugv.swallow.parts import dict_of_parts
from bluer_ugv.README.swallow.digital.design.mechanical import items as mechanical_items

items = (
    [
        {
            "path": "../docs/bluer_swallow/digital/design",
        },
        {
            "path": "../docs/bluer_swallow/digital/design/operation.md",
            "items": ImageItems(
                {
                    f"{assets2_bluer_swallow}/20250915_111435.jpg": "",
                }
            ),
        },
        {
            "path": "../docs/bluer_swallow/digital/design/parts.md",
            "items": db_of_parts.as_images(
                dict_of_parts,
                reference="../../../parts",
            ),
            "macros": {
                "parts:::": db_of_parts.as_list(
                    dict_of_parts,
                    reference="../../../parts",
                    log=False,
                ),
            },
        },
        {
            "path": "../docs/bluer_swallow/digital/design/terraform.md",
            "items": ImageItems(
                {
                    f"{assets2_bluer_swallow}/20250611_100917.jpg": "",
                    f"{assets2_bluer_swallow}/lab.png": "",
                    f"{assets2_bluer_swallow}/lab2.png": "",
                }
            ),
        },
        {
            "path": "../docs/bluer_swallow/digital/design/steering-over-current-detection.md",
            "items": ImageItems(
                {
                    "../../../../../diagrams/bluer_swallow/steering-over-current.png": "../../../../../diagrams/bluer_swallow/steering-over-current.svg",
                }
            ),
        },
        {
            "path": "../docs/bluer_swallow/digital/design/rpi-pinout.md",
        },
    ]
    + mechanical_items
    + [
        {
            "path": "../docs/bluer_swallow/digital/design/ultrasonic-sensor-tester.md",
            "cols": 2,
            "items": ImageItems(
                {
                    f"{assets2_bluer_swallow}/20250918_122725.jpg": "",
                    f"{assets2_bluer_swallow}/20250918_194715-2.jpg": "",
                    f"{assets2_bluer_swallow}/20250918_194804_1.gif": "",
                    f"{assets2}/ultrasonic-sensor-tester/00.jpg": "",
                }
            ),
        },
    ]
)
