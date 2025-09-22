import sys
import argparse
import pandas as pd
from .core import analyze
from .report import render_report

def cli():
    p = argparse.ArgumentParser(description='MicroEDA — lightweight EDA')
    p.add_argument('input', help='CSV file or - for stdin')
    p.add_argument('--name', default=None, help='Dataset name')
    p.add_argument('--out', help='Export report to file (md|html)')
    p.add_argument('--style', default='terminal', choices=['terminal','md','html'])
    p.add_argument('--max-rows', type=int, default=10000,
                   help='If dataset large, sample first N rows')
    args = p.parse_args()

    df = pd.read_csv(sys.stdin if args.input == '-' else args.input)
    if args.max_rows and len(df) > args.max_rows:
        df = df.head(args.max_rows)

    res = analyze(df, name=args.name)
    if args.style == 'terminal':
        render_report(res, style='terminal')
    else:
        content = render_report(res, style=args.style)
        if args.out:
            with open(args.out, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Saved report to {args.out}")
        else:
            print(content)

if __name__ == "__main__":
    cli()