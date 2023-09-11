# Import library

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

"""# Import dataset"""

# import dataset from Google Drive
with open('/content/drive/MyDrive/Rakamin/Project/PBI Kalbe/transaction.csv','r') as data_transaction:
  data_transaction = pd.read_csv(data_transaction, delimiter=';')
with open('/content/drive/MyDrive/Rakamin/Project/PBI Kalbe/product.csv','r') as data_product:
  data_product = pd.read_csv(data_product, delimiter=';')
with open('/content/drive/MyDrive/Rakamin/Project/PBI Kalbe/store.csv','r') as data_store:
  data_store = pd.read_csv(data_store, delimiter=';')
with open('/content/drive/MyDrive/Rakamin/Project/PBI Kalbe/customer.csv','r') as data_customer:
  data_customer = pd.read_csv(data_customer, delimiter=';')

data_transaction[data_transaction['TransactionID'] == 'TR72611']

data_product.head()

data_store

data_customer.head()

"""Hal yang harus dimasukkan ke data_transaction

dari data_store
3. Group Store
4. Type
5. Latitude
6. Longitude


dari data_customer
7. Age
8. Gender
9. Marital Status
10. Income

# Merge dataset
"""

# dari data_store
merge_data_store = ['GroupStore', 'Type', 'Latitude', 'Longitude']
for store_kolom in merge_data_store:
  data_transaction[store_kolom] = data_transaction['StoreID'].map(data_store.set_index('StoreID')[store_kolom])

# dari data_customer
merge_data_customer = ['Age', 'Gender', 'Marital Status', 'Income']
for customer_kolom in merge_data_customer:
  data_transaction[customer_kolom] = data_transaction['CustomerID'].map(data_customer.set_index('CustomerID')[customer_kolom])

df = data_transaction.copy()

df.head()

df.shape

df.info()

"""# Data preprocessing

## Convert Tipe Data
1. Date --> datetime
2. Latitude --> float
3. Longitude --> float
4. Income --> float
"""

df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
df['Latitude'] = df['Latitude'].str.replace(',','.').astype(float)
df['Longitude'] = df['Longitude'].str.replace(',','.').astype(float)
df['Income'] = df['Income'].str.replace(',','.').astype(float)

"""## Data duplicated"""

df.duplicated().sum()

"""Tidak ada duplikat data pada dataset

## Data Null
"""

df.isnull().sum()

"""Ada null value pada kolom Marital Status, tetapi abaikan karena tidak memakai saat modeling

# Machine Learning Regression (Time Series)
"""

df_regresi = df.groupby('Date').agg({'Qty': 'sum'}).reset_index()

plt.figure(figsize=(10, 3))  # Ukuran gambar (opsional)
plt.plot(df_regresi['Date'], df_regresi['Qty'], marker='', linestyle='-')
# plt.title('Grafik Qty terhadap Date')
plt.xlabel('Date')
plt.ylabel('Qty')
plt.grid(True)  # Menampilkan grid
plt.tight_layout()
plt.show()

df_regresi = df_regresi.set_index('Date')

"""## Model ARIMA

### Hyperparameter
"""

from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
import warnings
import sys


warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=RuntimeWarning)

data_train = df_regresi[:round(-365/2)]
data_test = df_regresi[round(-365/2):]

from itertools import product

p = range(0,50)
d = range(0,1)
q = range(0,10)
pdq = list(product(p, d, q))

rmse_scores = []
iterasi = 0
for i,param in enumerate(pdq,1):
  sys.stdout.write(f"\rPerulangan ke-{i}")
  sys.stdout.flush()
  model = ARIMA(df_regresi, order=param)
  model_fit = model.fit()

  # forecasting
  y_pred = model_fit.predict()

  # rmse
  mse = mean_squared_error(df_regresi.Qty, y_pred)
  rmse = np.sqrt(mse)

  rmse_scores.append({'par': param, 'rmse': rmse})
  iterasi += 1

best_rmse = min(rmse_scores,key=lambda x: x['rmse'])

best_rmse

"""### Modeling"""

# Memuat fungsi ARIMA
from statsmodels.tsa.arima.model import ARIMA

model = ARIMA(df_regresi, order=best_rmse['par'])
model_fit = model.fit()

y_pred = model_fit.predict()
y_true = df_regresi.Qty

from statsmodels.tsa.arima.model import ARIMA

model = ARIMA(df_regresi, order=(49, 0, 9))
model_fit = model.fit()

"""## Evaluasi Model"""

# (49, 0, 9)
plt.figure(figsize=(10, 5))
plt.plot(y_true, label='Actual')
plt.plot(y_pred, label='Predicted')
plt.xlabel('Date')
plt.ylabel('Qty')
plt.title('Perbandingan Hasil Prediksi dan Data Sebenarnya')
plt.legend()
plt.show()

# (49,0,9)
from sklearn.metrics import mean_squared_error
mse = mean_squared_error(y_true, y_pred)
rmse = np.sqrt(mse)
rmse

"""## Forecasting 1 Bulan ke Depan"""

model_forecast = model_fit.forecast(31)

plt.figure(figsize=(10,5))
plt.plot(df_regresi.Qty, label='Data Actual 1 Tahun')
plt.plot(model_forecast, label='Data Forecasting')
plt.xlabel('Date')
plt.ylabel('Qty')
plt.title('Forecasting 1 bulan kedepan')
plt.legend()
plt.show()

model_forecast.describe()

"""# Machine Learning Clustering"""

df_cluster = df.groupby('CustomerID').agg({
    'TransactionID': 'count',
    'Qty': 'sum',
    'TotalAmount': 'sum'
}).reset_index()

df_cluster

"""## Outliers"""

plt.figure(figsize=(2, 3))  # Set the size of the figure
sns.boxplot(data=df_cluster['TotalAmount'])  # Create the boxplot
plt.title('Boxplot of Customer Data')  # Set the title of the plot
plt.xlabel('TotalAmount')  # Set the label for the x-axis
plt.ylabel('Value')  # Set the label for the y-axis
plt.show()  # Show the plot

"""Sepertinya ada outliers pada kolom TotalAmount

### Handling Outliers
"""

Q1 = df_cluster.TotalAmount.quantile(0.25)
Q3 = df_cluster.TotalAmount.quantile(0.75)

IQR = Q3 - Q1

upper_bound = Q3 + 1.5*IQR
lower_bound = Q1 - 1.5*IQR

df_cluster = df_cluster[(df_cluster.TotalAmount >= lower_bound) & (df_cluster.TotalAmount <= upper_bound)]

df_cluster.shape

"""## Standard Scaler"""

cluster = df_cluster[['Qty', 'TotalAmount']]

from sklearn.preprocessing import StandardScaler
sc = StandardScaler()
cluster_scaled = sc.fit_transform(cluster)

df_cluster_scaled = pd.DataFrame(cluster_scaled, columns=cluster.columns)

# Qty dengan TotalAmont
plt.figure(figsize=(8, 4))
plt.scatter(df_cluster_scaled.Qty, df_cluster_scaled.TotalAmount, alpha=0.5, color='blue')
plt.title('Scatter Plot antara Qty dan TotalAmount')
plt.xlabel('Qty')
plt.ylabel('TotalAmount')
plt.show()

"""## WCSS vs K-Values
mencari K optimal
"""

from sklearn.cluster import KMeans

wcss = []
for i in range(1,11):
  model = KMeans(n_clusters=i, init='k-means++', n_init=10, max_iter=300, random_state=42)
  model.fit(cluster_scaled)
  wcss.append(model.inertia_)
print(wcss)

plt.figure(figsize=(8,3))
plt.plot(list(range(1,11)), wcss)
plt.title('WCSS VS K-Value')
plt.xlabel('K-Value')
plt.ylabel('WCSS')

plt.show()

"""Terlihat WCSS mulai stabil pada K-Value = 3"""

#Elbow Method with yellowbrick library
from yellowbrick.cluster import KElbowVisualizer

visualizer = KElbowVisualizer(model, k=(1,11))
visualizer.fit(cluster_scaled)
visualizer.show()

"""Menggunakan yellowbrick library menunjukkan K-Value = 3

## Sillhoute Score

## Modeling
"""

# K-Value = 3
from sklearn.cluster import KMeans
kmeans_3 = KMeans(n_clusters = 3,init='k-means++',max_iter=300,n_init=10,random_state=42)
kmeans_3.fit(cluster_scaled)
df_cluster['Cluster'] = kmeans_3.labels_
# kmeans_3.labels_

fig,ax = plt.subplots(figsize=(8,4))
sns.scatterplot(data=df_cluster, x='Qty', y='TotalAmount', hue='Cluster',palette='Set1')

"""## Evaluasi Model
Sillhoute Score
"""

from sklearn.metrics import silhouette_score
silhouette_avg = silhouette_score(cluster_scaled, kmeans_3.labels_)
silhouette_avg

df_cluster.groupby('Cluster').agg({
    'TransactionID': 'count',
    'Qty': 'sum',
    'TotalAmount': 'sum'
}).reset_index()