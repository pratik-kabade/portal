import pandas as pd

df_tc_ts = pd.read_csv('tc-ts.csv', quotechar='"')
df_req = pd.read_csv('req.csv', quotechar='"')

merged_df = pd.merge(df_tc_ts, df_req, on='REQ_ID', how='left')

reordered_df = merged_df[["REQ_ID", "REQ_Description", "TC_Description", "TS_Description", "TS_ExpectedResult"]]

reordered_df.to_csv("data.csv", index=False)

print("Files merged successfully into 'data.csv'")
