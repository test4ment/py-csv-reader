import argparse
from tabulate import tabulate
from csvreader.csvreader import CSVObject

parser = argparse.ArgumentParser()
parser.add_argument("--files", type=str, required=True, nargs="+")
parser.add_argument("--report", type=str, required=True, help="column to get mean")
args = parser.parse_args()

data = CSVObject.read_csv(args.files[0])
for fp in args.files[1:]:
    data.concat(CSVObject.read_csv(fp), copy=False, inplace=True)

print(tabulate(
    sorted(data.query().groupbycolumn("position").mean(args.report).items()), 
    headers=["position", args.report])
)
