import pandas as pd
scorecard = pd.read_csv("device_event_phase_scorecard.csv")
summary = scorecard.groupby("device_id").sum(numeric_only=True)
print("\n--- Forensic Phase Hit Counts By Device ---\n")
print(summary.to_markdown())
with open("phase_dashboard.md", "w") as f:
    f.write(summary.to_markdown())

