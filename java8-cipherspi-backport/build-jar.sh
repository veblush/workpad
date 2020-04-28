#!/bin/bash

set -ex

# Download original CipherSpi.java file from jdk8u repository
mkdir -p ./src/share/classes/javax/crypto
wget http://hg.openjdk.java.net/jdk8u/jdk8u/jdk/raw-file/f54e9b7c1036/src/share/classes/javax/crypto/CipherSpi.java -P ./src/share/classes/javax/crypto

# Get patch file for https://bugs.openjdk.java.net/browse/JDK-8178374
wget http://hg.openjdk.java.net/jdk/jdk/raw-rev/e93ba293e962

# Apply the patch file with a slight path modification
sed -i 's/src\/java.base\/share\/classes/src\/share\/classes/g' e93ba293e962
patch -p1 < e93ba293e962

# Build a class file from the modified source
javac ./src/share/classes/javax/crypto/CipherSpi.java -d ./

# Build a new jce.jar file by combining the existing one with newly built class file
cp /opt/java/openjdk/jre/lib/jce.jar jce.jar
jar -uf jce.jar javax/crypto/CipherSpi.class

# Store all output files to output directory
mkdir ./output
cp jce.jar ./output
cp javax/crypto/CipherSpi.class ./output
