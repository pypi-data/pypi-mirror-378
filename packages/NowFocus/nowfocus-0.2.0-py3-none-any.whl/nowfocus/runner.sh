#!/bin/sh

if pidof "nowfocus"; then
        kill -s 10 $(pidof nowfocus)
    else
        python3 __main__.py
fi
# python3 _main.py