from .raw_run import RawRun


class RawParagraph:
    def __init__(self, runs: list[RawRun]):
        self.runs = runs
        self.klasses = []
        self.text = self._run_text()

    def to_html(self) -> str:
        klass_list = " ".join(self.klasses)
        open_tag = f'<p class="{klass_list}">' if self.klasses else "<p>"
        return f"{open_tag}{self.text}</p>"

    def find(self, text: str) -> bool:
        return True if text in self.text else False

    def find_at_start(self, text: str) -> bool:
        return True if self.text.upper().startswith(text.upper()) else False

    def add_class(self, klass) -> None:
        self.klasses.append(klass)

    def to_dict(self) -> dict:
        """Convert the paragraph to a dictionary representation"""
        return {
            "type": "paragraph",
            "text": self.text,
            "runs": [run.to_dict() for run in self.runs],
            "classes": self.klasses,
        }

    def add_span(self, text: str, klass: str) -> None:
        new_str = f'<span class="{klass}">{text}</span>'
        self.text = new_str + self.text[len(text) :]

    def _run_text(self) -> str:
        return "".join([run.text for run in self.runs])
