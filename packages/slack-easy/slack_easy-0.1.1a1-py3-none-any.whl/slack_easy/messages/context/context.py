from ...blocks import Context
from ...interface import BaseSlackMessage


class ContextMessage(BaseSlackMessage):
    def __init__(self, **kwargs):
        elements = []
        for k, v in kwargs.items():
            if k.startswith("text_"):
                elements.append((v, "text"))
            elif k.startswith("image_url_"):
                elements.append((v, "image_url"))
            else:
                # other parameter like header, sub_header
                pass
        self.elements = elements
        for i, element in enumerate(self.elements):
            del kwargs[element[1]+f"_{i+1}"]
        super().__init__(**kwargs)

    def build_blocks(self) -> list[dict]:
        blocks = [{
            "type": "context",
            "elements": []
        }]
        for value, value_type in self.elements:
            if value_type == "text":
                blocks[0]["elements"].append(Context.mrkdwn(value))
            elif value_type == "image_url":
                blocks[0]["elements"].append(Context.image_url(value))
            else:
                raise ValueError("parameter value_type must be 'text' or 'image_url'")
        return blocks
