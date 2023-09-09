import argparse
import pandas as pd

print('Starting script')

parser = argparse.ArgumentParser(description = 'This is my first script to do something within a docker')

parser.add_argument('-a', '--csv_to_read', type = str, help = 'This is the path to the csv file to read')
parser.add_argument('-b', '--csv_to_write', type = str, help = 'This is the path to the csv file to write')

args = parser.parse_args()

df = pd.read_csv(args.csv_to_read)

output = df['Outcome Type'].value_counts(normalize=True, dropna=False).reset_index()

output.to_csv(args.csv_to_write, index = False)

print('Finished script')