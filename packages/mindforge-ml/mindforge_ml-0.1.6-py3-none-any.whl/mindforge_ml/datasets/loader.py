import pandas as pd
import json, requests

def load_hypertension_data():
    """
    Load the hypertension dataset from GitHub.
    Returns:
        pandas.DataFrame
    """
    url = "https://raw.githubusercontent.com/Perfect-Aimers-Enterprise/minforge/main/mindforge-ml/mindforge_ml/datasets/hypertensiondataset.csv"
    return pd.read_csv(url)


def seq2seqdataset():
    """
    Text to Text (query and target data)
    """
    # url = "https://raw.githubusercontent.com/Perfect-Aimers-Enterprise/mindforgedataset/refs/heads/main/datasets/seq2seqdataset.json"

    with open("mindforge_ml/datasets/seq2seqdataset.json") as f:
        dataset = json.load(f)
    # response = requests.get(url)
    # dataset = response.json()
    return dataset