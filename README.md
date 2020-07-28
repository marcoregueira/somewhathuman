# SomewhatHuman
Old Makehuman fork. Just for fun and for the web.

** AGPL license ** be warned.


This is a proof of concept in converting a graphical 3D design desktop application made in Python into a web enabled application. The goal was to provide a Flask interface to the app, allowing to change parameters of the human model, and showing it in the browser using a 3D library instead of a rendered image. 

Only a small set of actions is available. All the QT user interface has been removed and only a few options have been implemented, but it would be possible to enable more options following the same pattern.

The result was quite successful, as it proved to be feasible and went to the box of forgotten projects inmediately afterwards.

There is a demo in Heroku, that almost never works, because it depletes all assigned CPU resources in the free tier inmediately.

![alt tag](https://raw.githubusercontent.com/marcoregueira/somewhathuman/develop/src/phyton/makehuman/static/images/capture.png)
