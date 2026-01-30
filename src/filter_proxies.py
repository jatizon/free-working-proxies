import pandas as pd
import os

def filter_by_success_rate(df, folder_path="../proxies"):
    def categorize(rate):
        if rate == 0:
            return "NOT WORKING"
        elif rate < 0.7:
            return "BAD"
        elif rate < 0.9:
            return "GOOD"
        else:
            return "VERY_GOOD"
    
    df["status"] = df["success_rate"].apply(categorize)

    os.makedirs(folder_path, exist_ok=True)
    
    for category in ["BAD", "GOOD", "VERY_GOOD"]:
        df_cat = df[df["status"] == category]
        if not df_cat.empty:
            df_cat.to_csv(f"{folder_path}/{category.lower()}_proxies.csv", index=False)
    
    return df
