from tkinter import   *

str = {
        "\n"
        f"Typing  : [{Wpm}][50%]\n"
        f"Focus   : [{Focus}][{Focus_TOTAL}]\n"
        f"CT      : [{CT}][{CT_TOTAL}]\n"
        f"ACT     : [{ACT}][{ACT_TOTAL}]\n"
        f"HTML    : [{html}][{html_total}]\n"
        f"CSS     : [{css}]{css_total}]\n"
        f"JS      : [{js}][{js_total}]\n"
        f"TOTAL   : [{total}][{T_Total}]\n"
}




root = Tk()
window =Label(root,text=str )
window.pack()
root.geometry("300x399")
root.mainloop()


