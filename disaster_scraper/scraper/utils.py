import os
import pandas as pd

def save_to_csv(data):
    df = pd.DataFrame(data)
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/disaster_news.csv", mode='a', header=not os.path.exists("data/disaster_news.csv"), index=False)
