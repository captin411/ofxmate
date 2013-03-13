Overview
=========

Desktop app for downloading OFX statement data


Installing
==========

OSX
---

> sudo easy_install ofxmate

OSX - DMG build
---------------

Download the source

> get source from https://github.com/captin411/ofxmate

> unpack it

> sudo python setup.py install

> sudo python setup.py py2dmg

> open ./dist

Windows
-------

> easy_install ofxmate

Note: Make sure %PYTHON_HOME%\Scripts is added to your %PATH% otherwise the 'ofxmated' command will not be found on your path.

Source
------

> get source from https://github.com/captin411/ofxmate

> unpack it

> sudo python setup.py install

Quick Start
===========

This distribution comes with a small web application so that you can add your banks, accounts and credentials.

Run this command in the terminal or command prompt

> ofxmate

If you need to, you can override the port that is bound to (8080)

> ofxmate -p 8080

And if you don't want the webbrowser opened on start

> ofxmate -b

Daemonizing on OSX or Linux
> nohup ofxmate -b &

Screen Shots
============

Searching for a bank
--------------------
http://cl.ly/image/1u0r3E2z2G0j
http://cl.ly/image/1J2K391G2104

Adding a bank
--------------------
http://cl.ly/image/1T294228380a

Your list of banks
--------------------
http://cl.ly/image/0a3Y1q3W3V1P
