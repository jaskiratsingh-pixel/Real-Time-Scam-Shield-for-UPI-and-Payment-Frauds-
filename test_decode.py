import cv2
import numpy as np
import pandas as pd

from qr import decode_qr

CSV_PATH = "data/labelled_items.csv"


def load_items():
    return pd.read_csv(CSV_PATH)


def test_has_100_plus_items():
    assert len(load_items()) >= 100


def test_labels_are_valid():
    df = load_items()
    assert set(df["label"]) <= {"legit", "scam"}


def test_both_classes_present():
    df = load_items()
    assert (df["label"] == "legit").sum() >= 40
    assert (df["label"] == "scam").sum() >= 40


def test_decode_all_images():
    df = load_items()
    failed = []
    for _, row in df.iterrows():
        got = decode_qr("test_qr/" + row["image_file"])
        if got != row["qr_text"]:
            failed.append(row["image_file"])
    assert not failed, f"{len(failed)} images failed: {failed[:5]}"


def test_missing_file_returns_none():
    assert decode_qr("no_such_file.png") is None


def test_image_without_qr_returns_none(tmp_path):
    blank = np.full((200, 200, 3), 255, dtype=np.uint8)
    path = str(tmp_path / "blank.png")
    cv2.imwrite(path, blank)
    assert decode_qr(path) is None