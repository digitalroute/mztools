# PaaS Tools

# Introduction

To get automatic builds to work there is some underlaying architecture, combinde with AWS S3, AWS CodeBuild and AWS Pipeline. This document will try to explain what these resources are and how they belong together.

# Howto setup AWS CLI

# How to setup PaaS Tools

## Prerequisites
Make sure you have Python3

## Installation
Download release and unzip  
Run command:  

    $ pip3 install . --user

Setup a config.ini file either in current directory or in ~/.paas-tools/config.ini

    $ mkdir ~/.paas-tools && cp config.ini ~/.paas-tools/

Edit the config file to your environment  
You should now be able to run the tool!

    $ paas-tools

# Howto deploy to test environment
## Export files
## Run command...

# Infrastrucutre information

## CodeBuild

## S3

## Code Pipeline