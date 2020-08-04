#!/bin/bash

echo "Hello World!"

echo "This is ${0}."

echo "A.K.A. $(readlink -f ${0})."

echo "Arguments are:"

for an_arg in "${@}" ; do
   echo "- ${an_arg}"
done