#!/usr/bin/env python
# coding: utf-8

# ### Import libraries

# In[ ]:


import pandas as pd
import h2o
from h2o.automl import H2OAutoML
from sklearn.preprocessing import StandardScaler
import joblib  # For saving the model
import matplotlib.pyplot as plt

# Start H2O Cluster
h2o.connect(ip="10.1.234.150", port=54321)
h2o.init()


# ### Load dataset

# In[5]:


file_path = "./data/1991-2005/monthly/solar_dataset.csv"
data = pd.read_csv(file_path)


# ### Data Preprocessing

# In[6]:


# # Convert Year and Month into a single feature 'YearMonth'
# data['YearMonth'] = data['Year'].astype(str) + data['Month'].astype(str).str.zfill(2)
# data['YearMonth'] = pd.to_datetime(data['YearMonth'], format='%Y%m')
# 
# # Drop original Year and Month columns
# data = data.drop(['Year', 'Month'], axis=1)

# Feature Scaling for coordinate and solar irradiation inputs
features = ['Azimuth (deg)', 'Longitude', 'Elevation', 'Latitude', 'Year', 'Month']
target = 'Merged Glo (Wh/m^2)'

# Scaling using StandardScaler for the coordinate features
scaler = StandardScaler()
data[['Azimuth (deg)', 'Longitude', 'Elevation', 'Latitude']] = scaler.fit_transform(
    data[['Azimuth (deg)', 'Longitude', 'Elevation', 'Latitude']])

# Convert pandas DataFrame to H2OFrame
h2o_data = h2o.H2OFrame(data)

# Specify input features and target for H2O
X = features
y = target


# ### Train Test Split

# In[7]:


# Train-Test Split (80%-20%)
train, test = h2o_data.split_frame(ratios=[0.8], seed=42)


# ### AutoML with H2O

# In[8]:


# H2O AutoML - Set max runtime in seconds or specify max_models
aml = H2OAutoML(max_runtime_secs=600, seed=42, verbosity="info", nfolds=5)
aml.train(x=X, y=y, training_frame=train)


# ### Prediction and Evaluation

# In[9]:


# Leaderboard of top models
lb = aml.leaderboard
print(lb.head())

# Predict on test set
preds = aml.leader.predict(test)

# Evaluate performance
perf = aml.leader.model_performance(test)
print(perf)


# ### Retrain Best Model on the Entire Dataset 

# In[10]:


# Combine train and test data
full_data = train.rbind(test)

# Retrain the best model (leader) using the entire dataset
aml.leader.train(x=X, y=y, training_frame=full_data)


# ### Retrain Best Model on the Entire Dataset 

# In[ ]:


model_filename = 'best_solar_model.pkl'
joblib.dump(tpot.fitted_pipeline_, model_filename)
print(f"Best model saved to {model_filename}")


# ### Plotting Actual vs Predicted

# In[ ]:


# Convert H2O predictions to pandas for visualization
test_df = test.as_data_frame()
preds_df = preds.as_data_frame()

# Plot Actual vs Predicted Solar Irradiation
plt.figure(figsize=(10, 6))
plt.plot(test_df[target].values, label='Actual')
plt.plot(preds_df['predict'].values, label='Predicted', linestyle='--')
plt.legend()
plt.xlabel('Samples')
plt.ylabel('Merged Glo (Wh/m^2)')
plt.title('Actual vs Predicted Solar Irradiation (Test Data)')
plt.show()


# In[ ]:


# plot the predicted values 
plt.figure(figsize=(10, 6))
plt.plot(preds[:50], label='Predicted')
plt.legend()
plt.xlabel('Samples')
plt.ylabel('Merged Glo (Wh/m^2)')
plt.title('Predicted Solar Irradiation')
plt.show()


# In[ ]:


#print maximum and minimum predicted values
print("Maximum predicted value:", max(preds))
print("Minimum predicted value:", min(preds))

