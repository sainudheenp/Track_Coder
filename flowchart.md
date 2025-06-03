op2=>operation: from utils.typing_wpm import get_wpm
op4=>operation: from utils.code_time import get_code_time
op6=>operation: from utils.lines_of_code import loc
op8=>operation: from utils.xl_rw import xl_rw
op10=>operation: from utils.print_values import Print_values
op12=>operation: from utils.get_driver import get_driver
op14=>operation: from utils.total_calc import total_calc
op16=>operation: from utils.cfile import copy_past
op18=>operation: import argparse
op20=>operation: from datetime import datetime, timedelta
st23=>start: start main
io25=>inputoutput: input: 
op28=>operation: parser = argparse.ArgumentParser()
sub30=>subroutine: parser.add_argument('-date', default=(datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d'), help='Specify a date (YYYY-MM-DD)')
op32=>operation: args = parser.parse_args()
op34=>operation: yesterday = args.date
op36=>operation: try:
    print(('\n' + ('=' * 50)))
    print(f'🚀 **Track Coder Automation Started** 📊')
    print(f'📅 Date: **{yesterday}**')
    print((('=' * 50) + '\n'))
    Wpm = get_wpm()
    (Focus, ACT, CT) = get_code_time(yesterday)
    (html, css, js, total) = loc(yesterday)
    Days = xl_rw(Focus, Wpm, CT, ACT, html, css, js, total, yesterday=yesterday)
    (html_total, css_total, js_total, CT_TOTAL, ACT_TOTAL, Focus_TOTA, T_Total) = total_calc()
    Print_values(Wpm, Focus, ACT, CT, html, css, js, total, html_total, css_total, js_total, CT_TOTAL, ACT_TOTAL, Focus_TOTA, T_Total, Days)
    copy_past()
except Exception as e:
    print('Error main:', e)
e38=>end: end main
sub41=>subroutine: main()

op2->op4
op4->op6
op6->op8
op8->op10
op10->op12
op12->op14
op14->op16
op16->op18
op18->op20
op20->st23
st23->io25
io25->op28
op28->sub30
sub30->op32
op32->op34
op34->op36
op36->e38
e38->sub41

