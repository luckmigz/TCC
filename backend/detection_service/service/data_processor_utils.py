# service/data_processor_utils.py
import pandas as pd

def contar_por_classe(detections: list):
    """
    Conta quantas detecções existem por classe (rótulo).
    """
    df = pd.DataFrame(detections)
    return df["label"].value_counts().to_dict()
