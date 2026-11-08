# Track Coder workflow

```mermaid
flowchart TD
    A[trackcoder CLI] --> B{Command}
    B -->|log| C[Validate and merge with existing day]
    B -->|collect| D[Independent providers]
    D --> E[MonkeyType WPM]
    D --> F[Software.com CT / ACT / focus]
    D --> G[TrackMe HTML / CSS / JS + JSX]
    E --> H{At least one success?}
    F --> H
    G --> H
    H -->|No| X[Leave workbook unchanged]
    H -->|Yes| C
    C --> I{Strict provider failure or dry run?}
    I -->|Strict failure| X
    I -->|Dry run| J[Preview only]
    I -->|Normal write| K[Backup existing workbook]
    K --> L[Upsert date and atomic save]
    B -->|report| M[Read normalized records]
    B -->|export| M
    B -->|sync sheets| M
    L --> M
    M --> N[Streaks / trends / goals]
    N --> O[Terminal + self-contained HTML]
    M --> P[CSV / JSON / batched Google Sheets]
```

## Reliability invariants

1. Importing a module never opens a browser or performs network I/O.
2. A failed provider never replaces a previously stored measurement with a fake value.
3. No collection success means no workbook write.
4. Existing dates are updated, not duplicated; legacy duplicate rows are consolidated on update.
5. Damaged input workbooks are preserved.
6. Reports and exports are local-only unless the user explicitly invokes Google Sheets sync.
