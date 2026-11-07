"""Human-readable terminal reports and a self-contained HTML dashboard."""

from __future__ import annotations

import html
import os
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .analytics import AnalyticsReport, GoalProgress
from .models import DailyMetrics
from .timeutils import human_duration


def _wpm(value: float | None) -> str:
    return "—" if value is None else f"{value:.0f}"


def daily_text(record: DailyMetrics) -> str:
    """A stable plain-text summary suitable for terminals and clipboards."""
    return "\n".join([
        f"Track Coder · {record.day.isoformat()}",
        "─" * 34,
        f"Focus          {human_duration(record.focus_minutes):>10}",
        f"Code time      {human_duration(record.code_time_minutes):>10}",
        f"Active code    {human_duration(record.active_code_time_minutes):>10}",
        f"Typing         {(_wpm(record.wpm) + ' wpm') if record.wpm is not None else 'not collected':>10}",
        f"HTML / CSS / JS {record.html:>4} / {record.css:>4} / {record.javascript:>4}",
        f"Total lines    {record.total_lines:>10,}",
        f"Active day     {'yes' if record.is_active else 'no':>10}",
        *( [f"Notes          {record.notes}"] if record.notes else [] ),
    ])


def summary_text(report: AnalyticsReport) -> str:
    period = report.period
    lines = [
        "",
        f"TRACK CODER  /  {period.start.isoformat()} → {period.end.isoformat()}",
        "═" * 62,
        f"  Active days     {period.active_days}/{period.elapsed_days}  ({period.consistency:.0f}% consistency)",
        f"  Focus           {human_duration(period.focus_minutes)}",
        f"  Code time       {human_duration(period.code_time_minutes)}",
        f"  Lines changed   {period.total_lines:,}",
        f"  Average WPM     {_wpm(period.average_wpm)}",
        f"  Current streak  {report.current_streak.length} days",
        f"  Best streak     {report.best_streak.length} days",
        "",
        "GOALS (prorated to this period)",
    ]
    for goal in report.goals:
        lines.append(
            f"  {goal.name:<15} {goal.format_actual():>9} / {goal.format_target():<9} {goal.percentage:>5.0f}%"
        )
    lines.extend(["", "INSIGHTS"])
    lines.extend(f"  • {insight}" for insight in report.insights)
    lines.append("")
    return "\n".join(lines)


def _change_badge(value: float | None) -> str:
    if value is None:
        return '<span class="trend neutral">new baseline</span>'
    css = "positive" if value >= 0 else "negative"
    arrow = "↑" if value >= 0 else "↓"
    return f'<span class="trend {css}">{arrow} {abs(value):.0f}%</span>'


def _bar_chart(report: AnalyticsReport) -> str:
    period = report.period
    by_date = {record.day: record for record in period.records}
    days = [period.start + timedelta(days=index) for index in range(period.elapsed_days)]
    values = [by_date.get(day, DailyMetrics(day)).code_time_minutes for day in days]
    maximum = max(values, default=0)
    width = max(720, len(days) * 30)
    height = 230
    chart_top, chart_bottom = 24, 178
    usable = chart_bottom - chart_top
    slot = (width - 50) / max(len(days), 1)
    parts = [
        f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" aria-label="Daily code time bar chart">',
        f'<line x1="38" y1="{chart_bottom}" x2="{width - 10}" y2="{chart_bottom}" class="axis" />',
        f'<text x="4" y="28" class="axis-label">{html.escape(human_duration(maximum))}</text>',
        '<text x="20" y="182" class="axis-label">0m</text>',
    ]
    label_every = max(1, len(days) // 6)
    for index, (day, value) in enumerate(zip(days, values)):
        bar_height = usable * value / maximum if maximum else 0
        x = 44 + index * slot
        y = chart_bottom - bar_height
        bar_width = max(5, slot - 9)
        parts.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{max(bar_height, 1):.1f}" '
            f'rx="4" class="bar{" empty" if value == 0 else ""}"><title>{day.isoformat()}: '
            f'{html.escape(human_duration(value))}</title></rect>'
        )
        if index % label_every == 0 or index == len(days) - 1:
            parts.append(
                f'<text x="{x + bar_width / 2:.1f}" y="204" text-anchor="middle" class="axis-label">'
                f'{day.strftime("%m-%d")}</text>'
            )
    parts.append("</svg>")
    return "".join(parts)


def _goal_card(goal: GoalProgress) -> str:
    complete = goal.percentage >= 100
    remaining = "Goal reached" if complete else (
        f"{goal.remaining:,} lines left" if goal.kind == "lines"
        else f"{human_duration(goal.remaining)} left"
    )
    return f"""
      <article class="goal{' complete' if complete else ''}">
        <div class="goal-heading"><strong>{html.escape(goal.name)}</strong><span>{goal.percentage:.0f}%</span></div>
        <div class="progress" role="progressbar" aria-valuenow="{min(goal.percentage, 100):.0f}" aria-valuemin="0" aria-valuemax="100" aria-label="{html.escape(goal.name)} goal">
          <span style="width:{min(goal.percentage, 100):.2f}%"></span>
        </div>
        <div class="goal-meta"><span>{html.escape(goal.format_actual())} / {html.escape(goal.format_target())}</span><span>{html.escape(remaining)}</span></div>
      </article>"""


def render_html(report: AnalyticsReport) -> str:
    period = report.period
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    language_values = [
        ("JavaScript / JSX", period.javascript, "violet"),
        ("HTML", period.html, "orange"),
        ("CSS", period.css, "blue"),
    ]
    language_html = []
    for name, value, css in language_values:
        share = value / period.total_lines * 100 if period.total_lines else 0
        language_html.append(f"""
          <div class="language-row"><div><span>{name}</span><strong>{value:,}</strong></div>
          <div class="language-track"><span class="{css}" style="width:{share:.2f}%"></span></div>
          <small>{share:.1f}% of tracked lines</small></div>""")

    recent = list(reversed(period.records[-10:]))
    if recent:
        table_rows = "".join(
            "<tr>"
            f"<td>{record.day.isoformat()}</td>"
            f"<td>{human_duration(record.focus_minutes)}</td>"
            f"<td>{human_duration(record.code_time_minutes)}</td>"
            f"<td>{_wpm(record.wpm)}</td>"
            f"<td>{record.total_lines:,}</td>"
            f"<td><span class=\"status {'active' if record.is_active else ''}\">{'Active' if record.is_active else 'Rest'}</span></td>"
            f"<td class=\"notes\">{html.escape(record.notes) if record.notes else '—'}</td>"
            "</tr>" for record in recent
        )
    else:
        table_rows = '<tr><td colspan="7" class="empty-table">No records in this period. Run <code>trackcoder log</code> to get started.</td></tr>'

    insights = "".join(f"<li>{html.escape(insight)}</li>" for insight in report.insights)
    goals = "".join(_goal_card(goal) for goal in report.goals)
    chart = _bar_chart(report)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="dark">
<title>Track Coder · {period.start.isoformat()} to {period.end.isoformat()}</title>
<style>
:root{{--bg:#080d19;--panel:#101827;--panel2:#131e30;--line:#243149;--text:#eef3ff;--muted:#91a0ba;--mint:#5eead4;--blue:#60a5fa;--violet:#a78bfa;--orange:#fb923c;--red:#fb7185}}
*{{box-sizing:border-box}} body{{margin:0;background:radial-gradient(circle at 85% -10%,#153c49 0,transparent 30%),var(--bg);color:var(--text);font:15px/1.55 Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
main{{max-width:1180px;margin:auto;padding:42px 28px 60px}} header{{display:flex;justify-content:space-between;gap:24px;align-items:flex-end;margin-bottom:30px}}.eyebrow{{color:var(--mint);font-size:12px;font-weight:800;letter-spacing:.18em;text-transform:uppercase}}h1{{font-size:clamp(30px,5vw,48px);letter-spacing:-.045em;line-height:1.05;margin:8px 0 12px}}.subtitle,.muted{{color:var(--muted)}}.generated{{text-align:right;font-size:12px;color:var(--muted)}}
.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:14px}}.card,.panel{{background:linear-gradient(145deg,rgba(19,30,48,.96),rgba(13,22,37,.96));border:1px solid var(--line);border-radius:18px;box-shadow:0 14px 40px #0002}}.card{{padding:21px}}.card-label{{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.1em}}.value{{font-size:32px;font-weight:750;letter-spacing:-.04em;margin:8px 0 3px}}.trend{{display:inline-flex;border-radius:99px;padding:2px 8px;font-size:11px;font-weight:700}}.positive{{color:var(--mint);background:#5eead412}}.negative{{color:var(--red);background:#fb718512}}.neutral{{color:var(--muted);background:#91a0ba12}}
.grid{{display:grid;grid-template-columns:1.7fr 1fr;gap:14px;margin-top:14px}}.panel{{padding:24px;min-width:0}}.panel h2{{font-size:16px;margin:0}}.panel-heading{{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:20px}}.panel-heading span{{color:var(--muted);font-size:12px}}.chart-scroll{{overflow-x:auto}}.chart{{width:100%;min-width:620px;display:block}}.axis{{stroke:var(--line)}}.axis-label{{fill:var(--muted);font-size:10px}}.bar{{fill:var(--mint);opacity:.88}}.bar.empty{{fill:var(--line);opacity:.45}}
.streaks{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:24px}}.streak{{background:#ffffff05;border:1px solid var(--line);border-radius:12px;padding:15px}}.streak strong{{font-size:28px;display:block}}.streak span{{font-size:11px;color:var(--muted)}}.language-row{{margin-top:18px}}.language-row>div:first-child{{display:flex;justify-content:space-between}}.language-track{{height:7px;background:#263249;border-radius:10px;margin:7px 0 4px;overflow:hidden}}.language-track span{{height:100%;display:block;border-radius:10px}}.violet{{background:var(--violet)}}.orange{{background:var(--orange)}}.blue{{background:var(--blue)}}.language-row small{{color:var(--muted)}}
.goals{{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}}.goal-heading,.goal-meta{{display:flex;justify-content:space-between;gap:10px}}.goal-heading span{{color:var(--mint);font-weight:700}}.progress{{height:9px;border-radius:10px;background:#273249;margin:13px 0 8px;overflow:hidden}}.progress span{{display:block;height:100%;background:linear-gradient(90deg,var(--blue),var(--mint));border-radius:10px}}.goal.complete .progress span{{background:var(--mint)}}.goal-meta{{font-size:11px;color:var(--muted)}}
.insights{{margin:0;padding-left:20px;color:#c5d1e5}}.insights li+li{{margin-top:9px}}.table-wrap{{overflow-x:auto}}table{{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums}}th{{text-align:left;color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.1em;padding:10px;border-bottom:1px solid var(--line)}}td{{padding:12px 10px;border-bottom:1px solid #24314980}}tbody tr:last-child td{{border:0}}.status{{color:var(--muted);font-size:11px;background:#91a0ba12;padding:3px 8px;border-radius:99px}}.status.active{{color:var(--mint);background:#5eead412}}.empty-table{{text-align:center;color:var(--muted);padding:30px}}.notes{{max-width:260px;overflow-wrap:anywhere;color:var(--muted)}}code{{color:var(--mint)}}footer{{margin-top:24px;color:var(--muted);font-size:11px;text-align:center}}
@media(max-width:850px){{.cards{{grid-template-columns:repeat(2,1fr)}}.grid{{grid-template-columns:1fr}}.goals{{grid-template-columns:1fr}}header{{align-items:flex-start;flex-direction:column}}.generated{{text-align:left}}}}
@media(max-width:480px){{main{{padding:26px 16px}}.cards{{grid-template-columns:1fr 1fr;gap:8px}}.card{{padding:15px}}.value{{font-size:25px}}.panel{{padding:18px}}}}
@media print{{:root{{--bg:#fff;--panel:#fff;--panel2:#fff;--text:#172033;--muted:#58667a;--line:#dbe2ec}}body{{background:#fff}}main{{padding:10px}}.card,.panel{{box-shadow:none;break-inside:avoid}}.chart-scroll,.table-wrap{{overflow:visible}}}}
</style>
</head>
<body><main>
<header><div><div class="eyebrow">Personal engineering analytics</div><h1>Track Coder</h1><div class="subtitle">{period.start.isoformat()} <span aria-hidden="true">→</span> {period.end.isoformat()} · {period.elapsed_days} days</div></div><div class="generated">Generated {generated}<br>Local-first · no tracking scripts</div></header>
<section class="cards" aria-label="Period summary">
  <article class="card"><div class="card-label">Focus time</div><div class="value">{human_duration(period.focus_minutes)}</div>{_change_badge(report.change('focus_minutes'))}</article>
  <article class="card"><div class="card-label">Code time</div><div class="value">{human_duration(period.code_time_minutes)}</div>{_change_badge(report.change('code_time_minutes'))}</article>
  <article class="card"><div class="card-label">Lines changed</div><div class="value">{period.total_lines:,}</div>{_change_badge(report.change('total_lines'))}</article>
  <article class="card"><div class="card-label">Active days</div><div class="value">{period.active_days}<small class="muted"> / {period.elapsed_days}</small></div><span class="trend neutral">{period.consistency:.0f}% consistency</span></article>
</section>
<section class="grid">
  <article class="panel"><div class="panel-heading"><h2>Daily code time</h2><span>Hover bars for exact values</span></div><div class="chart-scroll">{chart}</div></article>
  <article class="panel"><div class="panel-heading"><h2>Momentum &amp; languages</h2><span>All-time streaks</span></div>
    <div class="streaks"><div class="streak"><strong>{report.current_streak.length}</strong><span>CURRENT STREAK · DAYS</span></div><div class="streak"><strong>{report.best_streak.length}</strong><span>BEST STREAK · DAYS</span></div></div>
    {''.join(language_html)}
  </article>
</section>
<section class="panel" style="margin-top:14px"><div class="panel-heading"><h2>Goals</h2><span>Prorated from daily / weekly targets</span></div><div class="goals">{goals}</div></section>
<section class="grid">
  <article class="panel"><div class="panel-heading"><h2>Recent activity</h2><span>Average {_wpm(period.average_wpm)} WPM</span></div><div class="table-wrap"><table><thead><tr><th>Date</th><th>Focus</th><th>Code</th><th>WPM</th><th>Lines</th><th>Status</th><th>Notes</th></tr></thead><tbody>{table_rows}</tbody></table></div></article>
  <article class="panel"><div class="panel-heading"><h2>What the data says</h2><span>Rule-based, private insights</span></div><ul class="insights">{insights}</ul></article>
</section>
<footer>Generated by Track Coder · Source data stays in your workbook unless you explicitly sync it.</footer>
</main></body></html>
"""


def write_html_report(report: AnalyticsReport, destination: str | Path) -> Path:
    path = Path(destination).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_name = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", prefix=f".{path.name}-", dir=path.parent, delete=False,
        ) as temporary:
            temporary.write(render_html(report))
            temporary_name = temporary.name
        os.replace(temporary_name, path)
    except Exception:
        if temporary_name and os.path.exists(temporary_name):
            os.unlink(temporary_name)
        raise
    return path
