#!/bin/bash

python3 /src/PART2-downloader.py $USERNAME $PASSWD $TRAINQUARTER $TESTQUARTER

#find .

if [ $? -eq 0 ]
then
  echo "Successfully created files"
else
  echo "Could not create file" >&2
fi
