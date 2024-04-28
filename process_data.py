import sys
import pandas as pd

def main(headers):
    # Print the selected headers
    print("Selected headers:")
    for header in headers:
        print(header)

    # Generate a DataFrame with only the selected columns
    df = pd.read_csv(sys.stdin, sep='\t')
    selected_df = df[headers]
    print(selected_df)

if __name__ == "__main__":
    headers = sys.argv[1:]
    main(headers)
