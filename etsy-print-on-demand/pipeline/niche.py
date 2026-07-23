"""Worker 1: Niche picker.

Takes a niche either from the Research Hub's notes doc (manual copy/paste
for now — see research-hub/README.md) or from the command line. This stage
is intentionally not automated: niche selection is a judgment call, not a
repetitive task worth scripting.
"""

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Niche:
    audience: str
    theme: str

    @property
    def label(self) -> str:
        return f"{self.theme} for {self.audience}"

    @property
    def slug(self) -> str:
        text = f"{self.audience}-{self.theme}".lower()
        text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
        return text
