import pandas as pd
import matplotlib.pyplot as plt
df = pd.read_csv("aggregated_events_report.csv")
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s', errors='coerce')
bydev = df.groupby('device_id')['event_type'].value_counts().unstack().fillna(0)
bydev.plot(kind='bar', stacked=True, title="Events by Device")
plt.ylabel("Count"); plt.tight_layout()
plt.savefig("events_per_device.png")
plt.show()

