script to package cordova and all plugins it uses in one file.

add a marker in your cordova.js where you wnat the plgins sources to appear.

//insert packages here, is the default marker

should be somewhere between

window.cordova = require('cordova');

and

require('cordova/init');

for cordova 3.4.0

supports minifying through uglify.js

