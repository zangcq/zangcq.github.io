---
title: "openjdk8u build"
date: 2021-06-21 11:37:00
categories: ["java"]
permalink: "/2021/06/21/openjdk8u-build/"
legacy: true
toc: true
classes: wide
---

```
    # jdk7
    wget https://download.java.net/openjdk/jdk7u75/ri/openjdk-7u75-b13-linux-x64-18_dec_2014.tar.gz
    tar xzf openjdk-7u75-b13-linux-x64-18_dec_2014.tar.gz
    
    
    export JAVA_HOME=/yourpath/java-se-7u75-ri
    export PATH=$PATH:$JAVA_HOME/bin
    
    source jdk7.sh
    
    # depend
    sudo apt-get update
    
    sudo apt-get install -y autoconf
    sudo apt-get install -y file
    sudo apt-get install -y libx11-dev libxext-dev libxrender-dev libxrandr-dev libxtst-dev libxt-dev
    sudo apt-get install -y libcups2-dev libfontconfig1-dev libasound2-dev
    
    # config
    bash configure --with-vendor-name=OpenJDK --with-debug-level=release --with-native-debug-symbols=none
    make JOBS=8 all
    
```
