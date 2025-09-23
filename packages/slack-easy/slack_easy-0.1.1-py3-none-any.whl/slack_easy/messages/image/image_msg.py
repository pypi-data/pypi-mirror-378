from ...blocks import Image
from ...interface import BaseSlackMessage


class ImageMessage(BaseSlackMessage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.image_url = kwargs.get('image_url')
        self.image_buffer = kwargs.get('image_buffer')
        self.image_name = kwargs.get('image_name')
        self.preview = self.preview or self.header or self.sub_header or self.image_name or 'You got a new message'

    def upload_image_buffer(self):
        image_url = self.slack_bot.image_upload(
            buffer=self.image_buffer,
            file_name=self.image_name
        )
        return image_url

    def build_blocks(self) -> list:
        if not self.image_url and not self.image_buffer:
            raise ValueError(f"No image url or image buffer provided")
        if self.image_buffer is not None:
            image_url = self.upload_image_buffer()
        else:
            image_url = self.image_url
        blocks = Image.image(image_url, self.image_name)
        return blocks
