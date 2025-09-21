from dataclasses import dataclass
from functools import partial
import re

from dyngle.error import DyngleError


PATTERN = re.compile(r'\{\{\s*([^}]+)\s*\}\}')


@dataclass
class Template:

    template: str

    def render(self, data: dict = None, expressions: dict = None) -> str:
        """Render the template with the provided data and expressions.

        Parameters
        ----------
        data : dict
            String data to insert
        expressions : dict
            Functions to call with data

        Returns
        -------
        str
            Template rendered with expression resolution and values inserted.
        """

        data = data if data else {}
        expressions = expressions if expressions else {}
        resolver = partial(self._resolve, live_data=data | expressions)
        return PATTERN.sub(resolver, self.template)

    def _resolve(self, match, *, live_data: dict):
        """Resolve a single name/path from the template. The argument is a
        merge of the raw data and the expressions, either of which are valid
        substitutions."""
        key = match.group(1).strip()
        return self.resolve(key, live_data)

    @staticmethod
    def resolve(key: str, live_data: dict):
        parts = key.split('.')
        current = live_data
        for part in parts:
            if part not in current:
                raise DyngleError(
                    f"Invalid expression or data reference '{key}")
            current = current[part]
        if callable(current):
            return current(live_data)
        else:
            return current
