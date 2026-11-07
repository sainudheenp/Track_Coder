"""Legacy report formatter; new commands use trackcoder.reporting."""

from trackcoder.timeutils import human_duration, parse_duration


def split(val):
    return human_duration(parse_duration(val))


def Print_values(Wpm, Focus, ACT, CT, html, css, js, total, html_total, css_total,
                 js_total, CT_TOTAL, ACT_TOTAL, Focus_TOTAL, T_Total, Days):
    text = "\n".join([
        "Coding Activity Report",
        "-" * 40,
        f"Typing  : [{Wpm if Wpm is not None else 'n/a'}wpm]",
        f"Focus   : [{split(Focus)}][{split(Focus_TOTAL)}]",
        f"CT      : [{split(CT)}][{split(CT_TOTAL)}]",
        f"ACT     : [{split(ACT)}][{split(ACT_TOTAL)}]",
        f"HTML    : [{html}][{html_total}]",
        f"CSS     : [{css}][{css_total}]",
        f"JS      : [{js}][{js_total}]",
        f"TOTAL   : [{total}][{T_Total}]",
        f"Days    : #{Days}",
    ])
    print(text)
    try:
        import pyperclip
        pyperclip.copy(text)
        print("Copied to clipboard.")
    except Exception as exc:
        print(f"Clipboard unavailable: {exc}")
