from bluer_objects.README.items import ImageItems
from bluer_ugv.README.consts import bluer_swallow_mechanical_design

items = [
    {
        "path": "../docs/bluer_swallow/digital/design/mechanical",
        "items": ImageItems(
            {
                f"{bluer_swallow_mechanical_design}/robot.png": f"{bluer_swallow_mechanical_design}/robot.stl",
                f"{bluer_swallow_mechanical_design}/cage.png": f"{bluer_swallow_mechanical_design}/cage.stl",
                f"{bluer_swallow_mechanical_design}/measurements.png": "",
            }
        ),
    },
    {
        "path": "../docs/bluer_swallow/digital/design/mechanical/v1.md",
        "items": ImageItems(
            {
                f"{bluer_swallow_mechanical_design}/v1/robot.png": f"{bluer_swallow_mechanical_design}/v1/robot.stl",
                f"{bluer_swallow_mechanical_design}/v1/cage.png": f"{bluer_swallow_mechanical_design}/v1/cage.stl",
                f"{bluer_swallow_mechanical_design}/v1/measurements.png": "",
            }
        ),
    },
]
