import pandas as pd

data = {

"name": ["A", "B", "C", "D", "E"],

"category": ["X", "Y", "X", "Y", "X"],

"value": [10, 40, 30, 20, 50]

}

df = pd.DataFrame(data)

df.to_csv("data.csv", index=False)