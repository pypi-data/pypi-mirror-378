
#***********************************************************************************************************
#*************************** WELCOME MESSAGE ****************************************************************
#***********************************************************************************************************
def assoview():
#  pip install mlxtend pandas openpyxl
#  pip install pandas scikit-learn openpyxl matplotlib
  print("**********************************************************")
  print("assoview")
  print()
  print()
  print("Function: arule")
  print("Input file format: MS Excel")
  print("Notes: use the 'Items' for the rules mining")
  # print()
  # print()
  print("**********************************************************")


#SUBPACKAGE: arule---------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
# functions: association tree will be created for data input as text (e.g. milk, chips, cake)
#***********************************************************************************************************

def arule():
    # --- stdlib setup (safe) ---
    import warnings
    warnings.filterwarnings(
        "ignore",
        message=r"datetime\.datetime\.utcnow.*",
        category=DeprecationWarning,
    )

    # If you need “now in UTC”, do this explicitly:
    import datetime
    now_utc = datetime.datetime.now(datetime.timezone.utc)  # use this when needed

    # --- third-party imports ---
    import pandas as pd
    from mlxtend.frequent_patterns import apriori
    from google.colab import files

    # Upload the file
    uploaded = files.upload()
    file_name = list(uploaded.keys())[0]
    df = pd.read_excel(file_name)

    # Split items and one-hot encode
    df['Items'] = df['Items'].astype(str).str.split(', ')
    df_onehot = df['Items'].str.join('|').str.get_dummies()

    # Minimum support input
    min_support = float(input("Please enter the minimum support value (less than 1): "))

    # Frequent itemsets
    frequent_itemsets = apriori(df_onehot, min_support=min_support, use_colnames=True)

    # Custom association rules without lift
    rules = []
    for _, row in frequent_itemsets.iterrows():
        itemset = row['itemsets']
        # ensure it's a set-like (mlxtend uses frozenset)
        for item in itemset:
            antecedent = set(itemset) - {item}
            if antecedent:
                # look up support for the antecedent if it exists
                mask = frequent_itemsets['itemsets'].apply(lambda s: set(s) == antecedent)
                if not mask.any():
                    continue
                antecedent_support = frequent_itemsets.loc[mask, 'support'].values[0]
                confidence = row['support'] / antecedent_support
                if confidence >= min_support:
                    rules.append(
                        {
                            "If": ', '.join(sorted(antecedent)),
                            "Then": item,
                            "Support": row['support'],
                            "Confidence": confidence,
                            # Example of using the UTC time if you want to stamp outputs:
                            "GeneratedAtUTC": now_utc.isoformat()
                        }
                    )

    # Convert to DataFrame
    rules_df = pd.DataFrame(rules)

    # Sort and save
    rules_df = rules_df.sort_values(by='Confidence', ascending=False)
    output_file = 'custom_association_rules_output.xlsx'
    rules_df.to_excel(output_file, index=False)
    files.download(output_file)

    print("\nThe association rules have been saved to 'custom_association_rules_output.xlsx' and are available for download.")

