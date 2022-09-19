from sklearn.linear_model import LinearRegression
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

import matplotlib.pyplot as plt
import numpy as np

data_frame = pd.read_csv('dataset2.csv', sep=";")
data_frame.fillna(value=0, inplace=True)
data_frame.replace('N/A', 0, inplace=True)
data_frame.replace('', 0, inplace=True)

X = data_frame.drop(["FAMILIA"], axis = 1)
y = data_frame.iloc[:,-1]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

lr = LinearRegression()
lr.fit(X_train, y_train)

y_lr_train_pred = lr.predict(X_train)
y_lr_test_pred = lr.predict(X_test)

lr_train_mse = mean_squared_error(y_train, y_lr_train_pred)
lr_train_r2 = r2_score(y_train, y_lr_train_pred)

lr_test_mse = mean_squared_error(y_test, y_lr_test_pred)
lr_test_r2 = r2_score(y_test, y_lr_test_pred)

print(f"mean squared error: {lr_train_mse}")
print(f"r2 score: {lr_test_r2}")


#showing results

plt.figure(figsize=(5,5))
plt.scatter(x=y_train, y=y_lr_train_pred, c="#7CAE00", alpha=0.3)
z = np.polyfit(y_train, y_lr_train_pred, 1)
p = np.poly1d(z)

plt.plot(y_train, p(y_train), "#F8766D")
plt.ylabel('Predicted Ransom FAM')
plt.xlabel('Experimental Ransom FAM')

plt.show()