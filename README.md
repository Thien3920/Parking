# Parking-Management
## Introduction
Parking billing software uses license plate detection and facial recognition
 
[here](https://user-images.githubusercontent.com/87056480/172690680-b265082f-240a-4bac-aaa1-fd3597ac64de.mp4)
## Install
### **Cuda 11.4 - Cudnn 8.2.4**
#### **Install cuda 11.4 - ubuntu 20.04

Click [here](https://www.mongodb.com](https://medium.com/@anarmammadli/how-to-install-cuda-11-4-on-ubuntu-18-04-or-20-04-63f3dee2099) to install cuda 11.4 for ubuntu 20.04

#### **Install cudnn 8.2.4**

Click [here](https://developer.nvidia.com/rdp/cudnn-archive) to download cudnn version 8.2.4

```
$ tar -xvf cudnn-11.4-linux-x64-v8.2.4.15.tgz
$ sudo cp cuda/include/cudnn*.h /usr/local/cuda/include 
$ sudo cp -P cuda/lib64/libcudnn* /usr/local/cuda/lib64 
$ sudo chmod a+r /usr/local/cuda/include/cudnn*.h /usr/local/cuda/lib64/libcudnn*
```

### **MongoDB**
Click [here](https://www.mongodb.com) to install MongoDB
### **Parking-Management**
Clone repo and install requirements.txt in a Python=3.6 environment.
```
$ git clone git@github.com:Thien3920/Parking-Management.git  # clone
$ cd Parking-Management
$ conda create --name parking_env python=3.6
$conda activate parking_env
% pip install -r requirements.txt  # install
```

## Usage
```
python Login.py
```
## Contact me
``` 
Email: ngocthien3920@gmail.com
Phone number: 0329615785
```
