from typing import Union, Literal


class TextEditor:
    def __init__(self, initial_text: str = ""):
        self.text = initial_text

    def insert_text(self, text: str):
        self.text += text

    def replace_text(
        self,
        old_text: str,
        new_text: str,
        occurrence: Union[int, Literal["all"]] = "all",
    ):
        if occurrence == "all":
            self.text = self.text.replace(old_text, new_text)
        else:
            self.text = self.text.replace(old_text, new_text, occurrence)

    def update_text(self, text: str):
        self.text = text

    def get_text(self):
        return self.text
