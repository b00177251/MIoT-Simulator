import pandas as pd
# assumes you have a manual/automatic annotation CSV: event_id,event_type,device_id,framework_ISO,framework_NIST,...
hits = pd.read_csv("framework_detection_log.csv")
event_types = hits['event_type'].unique()
frameworks = [col for col in hits.columns if col.startswith('framework_')]
for fw in frameworks:
    print(f"\nCoverage for {fw}:")
    for etype in event_types:
        found = hits[(hits['event_type'] == etype) & (hits[fw] == 1)].shape[0]
        total = hits[hits['event_type'] == etype].shape[0]
        print(f"  {etype}: {found}/{total} events ({100*found/total if total else 0:.1f}% covered)")

