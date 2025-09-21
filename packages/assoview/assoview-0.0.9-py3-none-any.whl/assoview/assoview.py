
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
  import pandas as pd
  from mlxtend.frequent_patterns import apriori
  from google.colab import files

  # Upload the file
  uploaded = files.upload()
  file_name = list(uploaded.keys())[0]
  df = pd.read_excel(file_name)

  # Split items and one-hot encode
  df['Items'] = df['Items'].str.split(', ')
  df_onehot = df['Items'].str.join('|').str.get_dummies()

  # Minimum support input
  min_support = float(input("Please enter the minimum support value (less than 1): "))

  # Frequent itemsets
  frequent_itemsets = apriori(df_onehot, min_support=min_support, use_colnames=True)

  # Custom association rules without lift
  rules = []
  for i, row in frequent_itemsets.iterrows():
      for item in row['itemsets']:
          antecedent = row['itemsets'] - {item}
          if len(antecedent) > 0:
              antecedent_support = frequent_itemsets[
                  frequent_itemsets['itemsets'] == antecedent
              ]['support'].values[0]
              confidence = row['support'] / antecedent_support
              if confidence >= min_support:
                  rules.append(
                      {
                          "If": ', '.join(antecedent),
                          "Then": item,
                          "Support": row['support'],
                          "Confidence": confidence,
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

