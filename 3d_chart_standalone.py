
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


# In[ ]:

data=pd.read_pickle("processed_data/simple_filter_14Mar18.pkl")


x=data.Lat.values
y=data.Lon.values
z=data.GPS_Alt.values


# In[7]:


fig=plt.figure(figsize=(20,10))
plt.figure(figsize=(20,10))
ax = fig.gca(projection='3d')
ax.plot(x, y, z, label='ski curve')
ax.legend()

plt.show()

