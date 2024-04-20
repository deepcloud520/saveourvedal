from local import *
np=numpy

def relu(x):
    return numpy.maximum(x,0)
'''
def softmax(x):
    if x.ndim==2:
        x = x.T
        x = x - numpy.max(x,axis=0)
        y = numpy.exp(x) - numpy.sum(numpy.exp(x),axis=0)
        return y.T
    x = x - numpy.max(x)
    return numpy.exp(x) - numpy.sum(numpy.exp(x))
'''
def softmax(x):
    y = np.exp(x - np.max(x))
    f_x = y / np.sum(np.exp(x))
    return f_x

def loadarray(path):
    res=numpy.load(dotpath+path)
    loclogger.debug(res.shape)
    return res
class Mnist_twolayer:
    def __init__(self,models):
        self.wlayer1,self.blayer1,self.wlayer2,self.blayer2 = (loadarray(i + '.npy') for i in models)
    def forward(self,inputarray):
        # 见鬼了，谁知道要transpose
        inputarray = inputarray.T.reshape((28*28,)).astype('float32')
        layer1 = relu(numpy.dot(inputarray,self.wlayer1) + self.blayer1)
        layer2 = softmax(numpy.dot(layer1,self.wlayer2)+ self.blayer2) 
        return layer2
    def predict(self,inputarray):
        forw=self.forward(inputarray)
        return numpy.argmax(forw),numpy.max(forw)
Mnist = Mnist_twolayer
if __name__ == '__main__':
    import os
    print('Start testing...')
    
    print()
    m = Mnist_twolayer(['mnist/dense-kernel:0','mnist/dense-bias:0','mnist/dense_1-kernel:0','mnist/dense_1-bias:0'])
    print('Model load complete...')
    test_array = numpy.zeros((28,28))
    test_array[5:26,14]=0.8
    test_array[5:26,13]=0.8
    test_array[5:26,15]=1
    test_array[5:26,16]=1
    print(m.predict(test_array))
    from keras.datasets import mnist
    from keras.utils import to_categorical
    (ti,tl),(tei,tel) = mnist.load_data()
    ti=ti.reshape((60000,28*28)).astype('float32') /255
    tei=tei.reshape((10000,28*28)).astype('float32') /255
    acc=0
    for i in range(200):
        pr=m.predict(ti[i])
        print(pr==tl[i])