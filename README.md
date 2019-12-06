# mztools
[![Build Status](https://travis-ci.org/digitalroute/mztools.svg?branch=master)](https://travis-ci.org/digitalroute/mztools)

## Introduction

mztools is used to control your PaaS environment for Digital Routes MediationZone.

## Prerequisites

Make sure you have Python3.

Configure AWS CLI with the credentials passed to you for your environment:
`aws configure`

## Installation

Run command:  

    $ pip install mztools

## Unittesting

Install tox:
    $ pip install tox

Run tox:
    $ tox

## Compile locally for testing purpose

Run below commands:

    $ python setup.py build
    $ sudo python setup.py install
    
This compiled mztools will be available at `/usr/local/bin/mztools` in your local machine