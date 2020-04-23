# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 20:41:23 2020

@author: IkrimaNingrrum
"""

# In[1]:

import librosa
import librosa.feature
import librosa.display
import glob
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.utils.np_utils import to_categorical
from sklearn.metrics import confusion_matrix
import itertools
import numpy as np
import tensorflow as tf 
# In[2]:

def display_mfcc(song):
    y, _ = librosa.load(song)
    mfcc = librosa.feature.mfcc(y)

    plt.figure(figsize=(10, 4))
    librosa.display.specshow(mfcc, x_axis='time', y_axis='mel')
    plt.colorbar()
    plt.title(song)
    plt.tight_layout()
    plt.show()
# In[3]:

display_mfcc('singers/Lady Gaga/Lady Gaga - BadRomance.wav')

display_mfcc('singers/Lady Gaga/Lady Gaga - Alejandro.wav')
# In[4]:
def extract_features_song(f):
    y, _ = librosa.load(f)
    # get Mel-frequency cepstral coefficients
    mfcc = librosa.feature.mfcc(y)
    # normalize values between -1,1 (divide by max)
    mfcc /= np.amax(np.absolute(mfcc))
    return np.ndarray.flatten(mfcc)[-60000:]

# In[5]:

extract_features_song('singers/Lady Gaga/Lady Gaga - BadRomance.wav')

extract_features_song('singers/Lady Gaga/Lady Gaga - Alejandro.wav')

# In[6]:

def generate_features_and_labels():
    all_features = []
    all_labels = []

    singers = ['Raisa', 'BigBang', 'Katy Perry', 'EXO', 'GOT7', 'Lady Gaga', 'Demi Lovato', 'Meghan Trainor', 'Red Velvet', 'Trevor Daniel']
    for singer in singers:
        sound_files = glob.glob('singers/'+singer+'/*.mp3')
        print('Processing %d songs by %s ...' % (len(sound_files), singer))
        
        for f in sound_files:
            features = extract_features_song(f)
            all_features.append(features)
            all_labels.append(singer)

    # convert labels to one-hot encoding
    label_uniq_ids, label_row_ids = np.unique(all_labels, return_inverse=True)
    label_row_ids = label_row_ids.astype(np.int32, copy=False)
    onehot_labels = to_categorical(label_row_ids, len(label_uniq_ids))
    return np.stack(all_features), onehot_labels
# In[7]:
    
features, labels = generate_features_and_labels()

print(np.shape(features))
print(np.shape(labels))
# In[8]:

training_split = 0.8

# last column has genre, turn it into unique ids
alldata = np.column_stack((features, labels))

np.random.shuffle(alldata)
splitidx = int(len(alldata) * training_split)
train, test = alldata[:splitidx,:], alldata[splitidx:,:]

print(np.shape(train))
print(np.shape(test))
# In[9]:

train_input = train[:,:-10]
train_labels = train[:,-10:]

test_input = test[:,:-10]
test_labels = test[:,-10:]

print(np.shape(train_input))
print(np.shape(train_labels))

print(np.shape(test_input))
print(np.shape(test_labels))
# In[10]:

model = tf.keras.Sequential()
model.add(tf.keras.layers.Dense(100, input_dim=np.shape(train_input)[1]))
model.add(tf.keras.layers.Activation('relu'))
model.add(tf.keras.layers.Dense(10))
model.add(tf.keras.layers.Activation('softmax'))
model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])
print(model.summary())
# In[11]:

model.fit(train_input, train_labels, epochs=10, batch_size=32,
          validation_split=0.2)

loss, acc = model.evaluate(test_input, test_labels, batch_size=32)

print("Done!")
print("Loss: %.4f, accuracy: %.4f" % (loss, acc))

# save the trained model
model.save("singers2.hdf5")
# In[12]:

import tensorflow as tf 
model2 = tf.keras.models.load_model("singers.hdf5")
print(model2.summary())
# In[13]:

def predict(song_path):
    song = np.stack([extract_features_song(song_path)])
    # do the prediction
    prediction = model2.predict(song, batch_size=32)

    print("Prediction: %s, confidence: %.2f" % (np.argmax(prediction), np.max(prediction)))
# In[14]:

predict('singers/Trevor Daniel/Trevor Daniel - Falling.wav')

predict('singers/Lady Gaga/Lady Gaga - Alejandro.wav')
# In[15]:
pred_labels = model2.predict(test_input)
cm = confusion_matrix(test_labels.argmax(axis=1), pred_labels.argmax(axis=1))
cm
# In[16]:
# In[16]:

def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)
    plt.figure(figsize=(6,6), dpi=100)
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=90)
    plt.yticks(tick_marks, classes)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
# In[17]:

singers = ['Raisa', 'BigBang', 'Katy Perry', 'EXO', 'GOT7', 'Lady Gaga', 'Demi Lovato', 'Meghan Trainor', 'Red Velvet', 'Trevor Daniel']
plot_confusion_matrix(cm, classes=singers, normalize=True)
plt.show()