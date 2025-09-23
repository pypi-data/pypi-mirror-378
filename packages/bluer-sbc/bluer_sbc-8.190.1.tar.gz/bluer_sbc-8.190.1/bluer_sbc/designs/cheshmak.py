from bluer_objects import README

from bluer_sbc.designs.consts import assets2

image_template = assets2 + "cheshmak/{}?raw=true"

marquee = README.Items(
    [
        {
            "name": "cheshmak",
            "marquee": image_template.format("01.png"),
            "url": "./bluer_sbc/docs/cheshmak.md",
        }
    ]
)

items = README.Items(
    [
        {
            "marquee": image_template.format(f"{index+1:02}.png"),
            "name": "",
        }
        for index in range(1)
    ]
)
