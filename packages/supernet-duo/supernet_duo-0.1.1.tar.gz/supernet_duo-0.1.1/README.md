# Supernet_Duo

An extremely powerful, lightweight, and simple text classification model, consisting of two neurons each with assigned jobs and a parabolic non-linear activation function. The weight of the connection between the two neurons is variable, and the model is trained and run instantly on the data provided in a dictionary.

## Installation
```bash
pip install supernet_duo
```

## Usage
```python
from supernet_duo import network
#Data that the model is trained on
mydata = {'123':'Class1','321':'Class2','01234':'Class1'}
#Text that is run through the model
input_string = '3210'
#Stregnth of the connection between neurons
weight = 4
#Run function
print(network(input_string,mydata,weight))
#Output: Class2
```
