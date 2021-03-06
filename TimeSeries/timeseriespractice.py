# -*- coding: utf-8 -*-
"""TimeSeriesPractice.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1QKezZdzD-hZhspGFT7TfWWjsmEIlbZHu
"""

#install library kaggle untuk download dataset
!pip install kaggle

#buat directory .kaggle
!mkdir .kaggle
!ls -a

#buat token untuk bisa akses download dataset
import json, os
token = {"username":"donodanar35","key":"92c113ad1a2fdabc92ea0f3fe5666e90"}

with open('/content/.kaggle/kaggle.json', 'w') as file:
    json.dump(token, file)

!chmod 600 /content/.kaggle/kaggle.json
!cp /content/.kaggle/kaggle.json ~/.kaggle/kaggle.json

os.listdir('.kaggle/')
!kaggle config set -n path -v{/content}

#download dataset climate change earth surface dari kaggle
!kaggle datasets download -d berkeleyearth/climate-change-earth-surface-temperature-data -p /tmp

import zipfile,os
local_zip = '/tmp/climate-change-earth-surface-temperature-data.zip'
zip_ref = zipfile.ZipFile(local_zip, 'r')

#ekstra dataset file zip ke destinasi /tmp
zip_ref.extractall('/tmp')
zip_ref.close()

os.listdir('/tmp')

import pandas as pd
import numpy as np
from keras.layers import Dense, LSTM
import matplotlib.pyplot as plt
import tensorflow as tf

df = pd.read_csv('/tmp/GlobalTemperatures.csv')
df = df.drop(['LandAverageTemperatureUncertainty','LandMaxTemperature','LandMaxTemperatureUncertainty','LandMinTemperature','LandMinTemperatureUncertainty','LandAndOceanAverageTemperature','LandAndOceanAverageTemperatureUncertainty'],axis=1)
df

df.isnull().sum()

#hilangkan baris null dari dataframe
df = df.dropna()
df.notnull().sum()

df.isnull().sum()

from sklearn.model_selection import train_test_split

#pisahkan dataset training dan dataset validation sebenar 80% dan 20%
dates = df['dt'].values
temp  = df['LandAverageTemperature'].values
temp_latih, temp_val, dates_latih, dates_val = train_test_split(temp, dates, test_size=0.2)

plt.figure(figsize=(15,5))
plt.plot(dates_latih, temp_latih)
plt.title('Land Average Temperature on Earth',
          fontsize=20);

def windowed_dataset(series, window_size, batch_size, shuffle_buffer):
    series = tf.expand_dims(series, axis=-1)
    ds = tf.data.Dataset.from_tensor_slices(series)
    ds = ds.window(window_size + 1, shift=1, drop_remainder=True)
    ds = ds.flat_map(lambda w: w.batch(window_size + 1))
    ds = ds.shuffle(shuffle_buffer)
    ds = ds.map(lambda w: (w[:-1], w[1:]))
    return ds.batch(batch_size).prefetch(1)

train_set = windowed_dataset(temp_latih, window_size=60, batch_size=100, shuffle_buffer=1000)
val_set = windowed_dataset(temp_val, window_size=60, batch_size=100, shuffle_buffer=1000)
model = tf.keras.models.Sequential([
      tf.keras.layers.LSTM(60, return_sequences=True),
      tf.keras.layers.LSTM(60),
      tf.keras.layers.Dense(30, activation="relu"),
      tf.keras.layers.Dense(10, activation="relu"),
      tf.keras.layers.Dense(1),
])

#buat kelas dan fungsi callback
class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('val_mae')<4):
      if(logs.get('mae')<4):      
        print("\nMAE data latih dan validation telah mencapai 4%!")
        self.model.stop_training = True
callbacks = myCallback()

optimizer = tf.keras.optimizers.SGD(lr=1.0000e-04, momentum=0.9)
model.compile(loss=tf.keras.losses.Huber(),
              optimizer=optimizer,
              metrics=["mae"])
history = model.fit(train_set,validation_data=val_set, epochs=200, callbacks=[callbacks])

import matplotlib.pyplot as plt

history_dict = history.history

mae=history_dict['mae']
val_mae=history_dict['val_mae']
epochs = range(1, len(mae) + 1)

plt.figure(figsize=(12,9))
plt.plot(epochs, mae, 'bo', label='Training mae')
plt.plot(epochs, val_mae, 'b', label='Validation mae')
plt.title('Training and Validation MAE')
plt.xlabel('Epochs')
plt.ylabel('MAE')
plt.legend()
plt.show()

history_dict = history.history
loss=history_dict['loss']
val_loss=history_dict['val_loss']
epochs = range(1, len(loss) + 1)

plt.figure(figsize=(12,9))
plt.plot(epochs, loss, 'bo', label='Training loss')
plt.plot(epochs, val_loss, 'b', label='Validation loss')
plt.title('Training and Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.show()