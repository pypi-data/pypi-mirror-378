from typing import Any
import sys

try:
    import colorama
    colorama.init()
except ImportError:
    sys.stderr.write("Warning: colorama library not found. ANSI colors may not work on Windows.\n")
    sys.stderr.flush()


class Control:
    """A control object to carry styling commands."""
    def __init__(self, **kwargs):
        self.params = kwargs


class PPrint:
    """
    A class for creating styled console output with a C++ cout-like syntax.
    It supports method chaining for embedded styling.
    """
    def __init__(self):
        self._colorset = {
            0: "\033[30m", 1: "\033[31m", 2: "\033[32m", 3: "\033[33m", 4: "\033[34m",
            5: "\033[35m", 6: "\033[36m", 7: "\033[37m", 8: "\033[90m", 9: "\033[91m",
            10: "\033[92m", 11: "\033[93m", 12: "\033[94m", 13: "\033[95m", 14: "\033[96m",
            15: "\033[97m"
        }
        self._bg_colorset = {
            0: "\033[40m", 1: "\033[41m", 2: "\033[42m", 3: "\033[43m", 4: "\033[44m",
            5: "\033[45m", 6: "\033[46m", 7: "\033[47m", 8: "\033[100m", 9: "\033[101m",
            10: "\033[102m", 11: "\033[103m", 12: "\033[104m", 13: "\033[105m", 14: "\033[106m",
            15: "\033[107m"
        }
        self._styleset = {
            "bold": "\033[1m", "italic": "\033[3m", "underline": "\033[4m",
            "blink": "\033[5m", "reverse": "\033[7m"
        }
        self._RESET_CODE = "\033[0m"
        self._ansi_code = ""
        self._end = "\n"

    def __lshift__(self, item: Any) -> "PPrint":
        """
        Overloads the '<<' operator to handle both styling and printing.
        """
        if isinstance(item, Control):
            if 'color' in item.params:
                c = item.params['color']
                if c not in self._colorset:
                    raise ValueError(f"Invalid color index: {c}. Must be between 0 and 15.")
                self._ansi_code += self._colorset[c]

            if 'bg_color' in item.params:
                c = item.params['bg_color']
                if c not in self._bg_colorset:
                    raise ValueError(f"Invalid background color index: {c}. Must be between 0 and 15.")
                self._ansi_code += self._bg_colorset[c]

            if 'style' in item.params:
                s = item.params['style']
                if isinstance(s, str):
                    s = [s]
                for style_name in s:
                    if style_name not in self._styleset:
                        raise ValueError(
                            f"Invalid style: '{style_name}'. Supported styles are {list(self._styleset.keys())}."
                        )
                    self._ansi_code += self._styleset[style_name]

            if 'end' in item.params:
                self._end = item.params['end']

        else:
            output = f"{self._ansi_code}{str(item)}{self._RESET_CODE}"
            print(output, end=self._end)
            self._ansi_code = ""
            self._end = "\n"

        return self
    def __repr__(self):
        return ""


# Public API
pprint = PPrint()
color = lambda c: Control(color=c)
bg_color = lambda c: Control(bg_color=c)
style = lambda s: Control(style=s)
end = lambda e: Control(end=e)
