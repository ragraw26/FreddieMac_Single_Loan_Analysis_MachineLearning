#!/bin/bash

python3 /src/PART1-downloader.py $USERNAME $PASSWD $STARTYEAR $ENDYEAR

#find .

if [ $? -eq 0 ]
then
  echo "Successfully created files"
else
  echo "Could not create file" >&2
fi
