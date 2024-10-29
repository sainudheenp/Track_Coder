import clipboard

def split(val):
    h , m = val.split(":")
    return f"{h}hr {m}min"



def Print_values(Wpm, Focus, ACT, CT, html, css, js, total,html_total ,css_total, js_total, CT_TOTAL, ACT_TOTAL,Focus_TOTAL,T_Total ):


    print("\n \n \n \n")

    print(f"Typing  : [{Wpm}][50%]")
    print(f"Focus   : [{split(Focus)}][{split(Focus_TOTAL)}]")
    print(f"CT      : [{split(CT)}][{split(CT_TOTAL)}]")
    print(f"ACT     : [{split(ACT)}][{split(ACT_TOTAL)}]")
    print(f"HTML    : [{html}][{html_total}]")
    print(f"CSS     : [{css}][{css_total}]")
    print(f"JS      : [{js}][{js_total}]")
    print(f"TOTAL   : [{total}][{T_Total}]")

    clipboard.copy(
        "\n"
        f"Typing  : [{Wpm}][50%]\n"
        f"Focus   : [{split(Focus)}][{split(Focus_TOTAL)}]\n"
        f"CT      : [{split(CT)}][{split(CT_TOTAL)}]"
        f"ACT     : [{split(ACT)}][{split(ACT_TOTAL)}]\n"
        f"HTML    : [{html}][{html_total}]\n"
        f"CSS     : [{css}]{css_total}]\n"
        f"JS      : [{js}][{js_total}]\n"
        f"TOTAL   : [{total}][{T_Total}]\n"

    )



