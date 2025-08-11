#!/usr/bin/env python3
"""
tx_predictor_md5.py

Tool Tài/Xỉu (Tai-Xiu) kết hợp:
- Dự đoán trước (probability) dựa trên lịch sử (machine learning hoặc heuristic)
- Xác minh sau khi reveal với MD5
- Xuất kết quả ở định dạng:
  #<round_id> | <MD5 status> | Prob(Tài)=0.87 | Pred: Tài | Tổng điểm: -- | (a-b-c)

Dependencies:
  - Python 3.8+
  - pip install pandas scikit-learn joblib   (joblib optional)
"""

import argparse
import hashlib
import re
import sys
from typing import Optional, Tuple, List

# Optional imports (for ML). If unavailable, heuristic fallback will be used.
try:
    import pandas as pd
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import Pipeline
    from joblib import dump, load
    ML_AVAILABLE = True
except Exception:
    ML_AVAILABLE = False

# -------------------------
# Utilities: MD5 & parsing
# -------------------------
def compute_md5(s: str) -> str:
    return hashlib.md5(s.encode('utf-8')).hexdigest()

def parse_dice_from_original(original: str) -> Optional[Tuple[int,int,int]]:
    m = re.search(r"\{(\d+)-(\d+)-(\d+)\}", original)
    if not m:
        return None
    a, b, c = int(m.group(1)), int(m.group(2)), int(m.group(3))
    return (a, b, c)

def tai_xiu_from_tuple(d: Tuple[int,int,int]) -> str:
    a,b,c = d
    if a == b == c:
        return "Bộ ba"
    total = a+b+c
    if 4 <= total <= 10:
        return "Xỉu"
    return "Tài"

def format_result_line(round_id: str, md5_status: str, prob_tai: Optional[float],
                       pred_label: str, total: Optional[int], dice: Optional[Tuple[int,int,int]]) -> str:
    prob_str = f"Prob(Tài)={prob_tai:.3f}" if prob_tai is not None else "Prob(Tài)=--"
    total_str = str(total) if total is not None else "--"
    dice_str = f"({dice[0]}-{dice[1]}-{dice[2]})" if dice else "()"
    return f"#{round_id} | {md5_status} | {prob_str} | Pred: {pred_label} | Tổng điểm: {total_str} | {dice_str}"

# -------------------------
# Feature engineering
# -------------------------
def featurize_round_id(round_id: str) -> List[float]:
    """
    Create numeric features from round_id (string).
    - digits mean/std
    - last 1-4 digits as integers (or 0)
    - length
    - count of even digits, odd digits
    """
    s = str(round_id)
    digits = [int(ch) for ch in s if ch.isdigit()]
    mean_d = float(np.mean(digits)) if digits else 0.0
    std_d = float(np.std(digits)) if digits else 0.0
    last1 = int(s[-1]) if s and s[-1].isdigit() else 0
    last2 = int(s[-2:]) if len(s) >= 2 and s[-2:].isdigit() else 0
    last3 = int(s[-3:]) if len(s) >= 3 and s[-3:].isdigit() else 0
    evens = sum(1 for d in digits if d % 2 == 0)
    odds = sum(1 for d in digits if d % 2 == 1)
    length = len(s)
    return [mean_d, std_d, last1, last2, last3, evens, odds, length]

def build_features_for_df(df: 'pd.DataFrame', lag: int = 3) -> 'pd.DataFrame':
    """
    df must contain: round_id (str), result (str) where result in {'Tài','Xỉu','Bộ ba'} or NaN.
    Builds feature columns including lag features of prior results.
    """
    feats = []
    for idx, row in df.iterrows():
        base = featurize_round_id(row['round_id'])
        feats.append(base)
    feats = pd.DataFrame(feats, columns=[
        'mean_digit', 'std_digit', 'last1', 'last2', 'last3', 'count_even', 'count_odd', 'len_id'
    ])
    # create lag features on result converted to binary (Tài=1, Xỉu=0), ignore Bộ ba (set NaN)
    label_map = {'Tài':1, 'Xỉu':0}
    res_bin = df['result'].map(label_map)
    for l in range(1, lag+1):
        feats[f'lag_{l}'] = res_bin.shift(l).fillna(-1)  # -1 means unknown
    return feats

# -------------------------
# Heuristic predictor
# -------------------------
class HeuristicPredictor:
    """
    Simple predictor when ML not available or data too small.
    Strategy:
      - Use last N results frequencies (window) to estimate probability
      - Slight bias to 50/50 if not enough data
    """
    def __init__(self, history_rounds: List[Tuple[str,str]]):
        # history_rounds: list of (round_id, result) where result in {'Tài','Xỉu','Bộ ba'}
        self.history = [r for _, r in history_rounds if r in ('Tài','Xỉu')]
        # store last 1000
        self.window = self.history[-1000:]

    def predict_prob_tai(self) -> float:
        if not self.window:
            return 0.5
        cnt_tai = sum(1 for r in self.window if r == 'Tài')
        return cnt_tai / len(self.window)

# -------------------------
# Main pipeline
# -------------------------
def train_ml_model(df_hist: 'pd.DataFrame', min_examples:int=200):
    """
    Train a logistic regression model if there's sufficient labelled data.
    Returns a pipeline (scaler + logistic) and scaler, else None.
    """
    # Prepare training rows that have result Tài or Xỉu
    df_train = df_hist[df_hist['result'].isin(['Tài','Xỉu'])].copy()
    if len(df_train) < min_examples or not ML_AVAILABLE:
        return None

    X = build_features_for_df(df_train)
    y = df_train['result'].map({'Tài':1, 'Xỉu':0}).astype(int)

    # pipeline
    pipe = Pipeline([
        ('scaler', StandardScaler()),
        ('clf', LogisticRegression(max_iter=1000))
    ])
    pipe.fit(X, y)
    return pipe

def predict_for_round(predictor, round_id: str, history_df: Optional['pd.DataFrame']=None):
    """
    predictor: either a trained ML pipeline or HeuristicPredictor object.
    Returns prob_tai (float between 0 and 1) and label 'Tài'/'Xỉu'
    """
    if predictor is None:
        # fallback pure 50/50
        prob = 0.5
        label = 'Tài' if prob >= 0.5 else 'Xỉu'
        return prob, label

    # ML pipeline: expects DataFrame row features
    if ML_AVAILABLE and hasattr(predictor, 'predict_proba'):
        # build a one-row df for features
        feat_row = build_features_for_df(pd.DataFrame([{'round_id': round_id, 'result': None}]))
        prob = predictor.predict_proba(feat_row)[0,1]  # probability of Tài (label 1)
        label = 'Tài' if prob >= 0.5 else 'Xỉu'
        return float(prob), label
    else:
        # heuristic predictor
        prob = predictor.predict_prob_tai()
        label = 'Tài' if prob >= 0.5 else 'Xỉu'
        return float(prob), label

# -------------------------
# I/O helpers
# -------------------------
def check_line_with_id(round_id: str, original: str, given_hash: Optional[str]=None) -> Tuple[str,str,Optional[Tuple[int,int,int]]]:
    computed = compute_md5(original)
    md5_status = "--"
    if given_hash:
        md5_status = "✅" if computed == given_hash.strip().lower() else "❌"
    dice = parse_dice_from_original(original)
    return md5_status, computed, dice

# -------------------------
# CLI
# -------------------------
def main():
    parser = argparse.ArgumentParser(description="TX Predictor + MD5 verifier")
    parser.add_argument("--history-csv", type=str, default=None,
                        help="CSV file of historical rounds. Must contain columns: round_id,result (Tài/Xỉu/Bộ ba). Optional: original,given_md5")
    parser.add_argument("--check-csv", type=str, default=None,
                        help="CSV to check. Must contain: round_id,original,given_md5 (given_md5 optional).")
    parser.add_argument("--output", type=str, default=None, help="Output CSV path (optional).")
    parser.add_argument("--min-train", type=int, default=200, help="Minimum labelled examples to train ML.")
    args = parser.parse_args()

    history_df = None
    ml_model = None
    heuristic = None

    if args.history_csv:
        try:
            history_df = pd.read_csv(args.history_csv, dtype=str)
            # ensure columns exist
            if 'round_id' not in history_df.columns or 'result' not in history_df.columns:
                print("history CSV must contain columns: round_id,result", file=sys.stderr)
                return
        except Exception as e:
            print("Cannot read history CSV:", e, file=sys.stderr)
            return

        if ML_AVAILABLE:
            ml_model = train_ml_model(history_df, min_examples=args.min_train)
        if ml_model is None:
            # build heuristic predictor based on history
            hist_pairs = list(history_df[['round_id','result']].itertuples(index=False, name=None))
            heuristic = HeuristicPredictor(hist_pairs)
            predictor = heuristic
            print("Using heuristic predictor (ML not trained or unavailable).")
        else:
            predictor = ml_model
            print("Using trained ML predictor.")
    else:
        # no history provided => pure heuristic 50/50
        predictor = None
        print("No history provided: predictions will be neutral (50/50).")

    # Process check CSV or read single input lines from stdin
    import csv
    out_rows = []
    if args.check_csv:
        try:
            with open(args.check_csv, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rid = row.get('round_id') or row.get('id') or row.get('#') or ''
                    original = row.get('original','')
                    given = row.get('given_md5') or row.get('md5') or ''
                    md5_status, computed_md5, dice = check_line_with_id(rid, original, given if given else None)
                    prob, predlabel = predict_for_round(predictor, rid, history_df)
                    total = sum(dice) if dice else None
                    line = format_result_line(rid, md5_status, prob, predlabel, total, dice)
                    print(line)
                    out_rows.append({
                        'round_id': rid,
                        'md5_status': md5_status,
                        'computed_md5': computed_md5,
                        'prob_tai': prob,
                        'pred_label': predlabel,
                        'total': total,
                        'dice': f"{dice}" if dice else ""
                    })
        except Exception as e:
            print("Cannot read check CSV:", e, file=sys.stderr)
            return
    else:
        # interactive: read lines from stdin as: round_id <TAB> original <TAB> given_md5(optional)
        print("Enter lines: round_id<TAB>original<TAB>given_md5(optional). Ctrl-D to end.")
        try:
            for raw in sys.stdin:
                raw = raw.strip()
                if not raw:
                    continue
                parts = raw.split('\t')
                rid = parts[0]
                original = parts[1] if len(parts) > 1 else ''
                given = parts[2] if len(parts) > 2 else ''
                md5_status, computed_md5, dice = check_line_with_id(rid, original, given if given else None)
                prob, predlabel = predict_for_round(predictor, rid, history_df)
                total = sum(dice) if dice else None
                line = format_result_line(rid, md5_status, prob, predlabel, total, dice)
                print(line)
                out_rows.append({
                    'round_id': rid,
                    'md5_status': md5_status,
                    'computed_md5': computed_md5,
                    'prob_tai': prob,
                    'pred_label': predlabel,
                    'total': total,
                    'dice': f"{dice}" if dice else ""
                })
        except KeyboardInterrupt:
            pass

    # optional CSV output
    if args.output:
        try:
            import csv as _csv
            keys = ['round_id','md5_status','computed_md5','prob_tai','pred_label','total','dice']
            with open(args.output, 'w', newline='', encoding='utf-8') as f:
                writer = _csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                for r in out_rows:
                    writer.writerow(r)
            print("Wrote output to", args.output)
        except Exception as e:
            print("Cannot write output CSV:", e, file=sys.stderr)

if __name__ == '__main__':
    main()