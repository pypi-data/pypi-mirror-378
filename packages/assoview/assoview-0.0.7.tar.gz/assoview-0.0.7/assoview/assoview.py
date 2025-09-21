
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


#SUBPACKAGE: arule01---------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
# functions: association tree will be created for data input as 0 1 format
#***********************************************************************************************************
def arule01():
  import pandas as pd
  from mlxtend.frequent_patterns import apriori, association_rules
  from google.colab import files

  # Allow the user to upload the file
  uploaded = files.upload()

  # Assume only one file is uploaded, get the file name
  file_name = list(uploaded.keys())[0]

  # Load the dataset from the uploaded file
  df = pd.read_excel(file_name)

  # Display the dataset
  print("Dataset:")
  print(df)

  # Remove 'Transaction' column if it exists
  if 'Transaction' in df.columns:
      df = df.drop(columns=['Transaction'])

  # Prompt the user to input the minimum support value
  while True:
      try:
          min_support = float(input("Please enter the minimum support value (less than 1):\n "))
          if min_support <= 0 or min_support >= 1:
              raise ValueError("The value must be between 0 and 1 (exclusive).")
          break
      except ValueError as e:
          print(e)

  # Perform Apriori algorithm to find frequent itemsets
  frequent_itemsets = apriori(df, min_support=min_support, use_colnames=True)

  # Display the frequent itemsets
  print("\nFrequent Itemsets:")
  print(frequent_itemsets)

  # Generate the association rules
  rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1)

  # Display the association rules
  print("\nAssociation Rules:")
  print(rules)


#SUBPACKAGE: arule---------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
# functions: association tree will be created for data input as text (e.g. milk, chips, cake)
#***********************************************************************************************************

def arule():
  import warnings
  import datetime

  # 1) Suppress the deprecation warning in output
  warnings.filterwarnings(
      "ignore",
      message="datetime.datetime.utcnow.*",
      category=DeprecationWarning,
  )

  # 2) Monkey patch datetime.utcnow to be timezone-aware
  datetime.utcnow = lambda: datetime.datetime.now(datetime.timezone.utc)

  import pandas as pd
  from mlxtend.frequent_patterns import apriori
  from google.colab import files

  # Upload the file
  uploaded = files.upload()
  file_name = next(iter(uploaded.keys()))
  df = pd.read_excel(file_name)

  # Ensure expected column exists
  if 'Items' not in df.columns:
      raise ValueError("Input file must contain a column named 'Items' with comma-separated items.")

  # Split items and one-hot encode
  df['Items'] = df['Items'].astype(str).str.split(', ')
  df_onehot = df['Items'].str.join('|').str.get_dummies()

  # Minimum support input
  min_support = float(input("Please enter the minimum support value (less than 1): "))

  # Frequent itemsets
  frequent_itemsets = apriori(df_onehot, min_support=min_support, use_colnames=True)

  # Make a quick lookup dict for supports of itemsets to avoid KeyErrors
  support_lookup = {frozenset(s): sup for s, sup in zip(frequent_itemsets['itemsets'], frequent_itemsets['support'])}

  # Custom association rules without lift
  rules = []
  for _, row in frequent_itemsets.iterrows():
      itemset = row['itemsets']
      if len(itemset) < 2:
          continue  # need at least 2 items to form a rule
      for item in itemset:
          antecedent = itemset - {item}
          antecedent_support = support_lookup.get(frozenset(antecedent))
          if antecedent_support and antecedent_support > 0:
              confidence = row['support'] / antecedent_support
              if confidence >= min_support:
                  rules.append(
                      {
                          "If": ', '.join(sorted(antecedent)),
                          "Then": item,
                          "Support": row['support'],
                          "Confidence": confidence,
                      }
                  )

  # Convert to DataFrame
  rules_df = pd.DataFrame(rules)

  # Sort and save
  if not rules_df.empty:
      rules_df = rules_df.sort_values(by='Confidence', ascending=False)
      output_file = 'custom_association_rules_output.xlsx'
      rules_df.to_excel(output_file, index=False)
      files.download(output_file)
      print("\nThe association rules have been saved to 'custom_association_rules_output.xlsx' and are available for download.")
  else:
      print("No rules met the specified minimum support/confidence thresholds.")


#
