from keras import models,layers
import numpy
from keras.datasets import mnist
(ti,tl),(tei,tel) = mnist.load_data()
from keras.utils import to_categorical

net = models.Sequential()
net.add(layers.Dense(64,activation='relu',input_shape=(28*28,)))
net.add(layers.Dense(10,activation='softmax',))
net.compile(optimizer='rmsprop',loss='categorical_crossentropy',metrics=['accuracy'])
print('compile network')


ti=ti.reshape((60000,28*28)).astype('float32') /255
tei=tei.reshape((10000,28*28)).astype('float32') /255

tl,tel = to_categorical(tl),to_categorical(tel)
print('load mnist')
net.fit(ti,tl,epochs=5,batch_size=128)
net.save('mnist_1')
print('save complete')
tl,ta  = net.evaluate(tei,tel)
print(f'test_acc:{ta},test_loss:{tl}')
for layer in net.weights:
    numpy.save(layer.name.replace('/','-'),layer.numpy())

