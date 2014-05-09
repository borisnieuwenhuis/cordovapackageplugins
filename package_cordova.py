
"""massages the cordova.js file and its plugins into one file"""

import re, json
from optparse import OptionParser
from subprocess import call

parser = OptionParser()
parser.add_option("-u", "--uglify", dest="uglify", action="store_true", default=False,
                  help="use uglify to minify packaged result file")

parser.add_option("-m", "--md5", dest="md5", action="store_true", default=False,
                  help="use md5 to sign the result filename")

parser.add_option("-o", "--output", dest="filename", action="store",
                  help="save results in file with this name")
(options, args) = parser.parse_args()

PACKAGE_MARKER = r"//insert packages here"
CORDOVA_PATH = "js/lib/cordova"

def read_as_string(filename):
    with open ("%s/%s" % (CORDOVA_PATH, filename), "r") as f:
        return f.read()

def insert_file(target, filename):
    to_insert = read_as_string(filename)
    return re.sub(PACKAGE_MARKER, "%s\n%s" % (to_insert, PACKAGE_MARKER), target), to_insert

cordovaJS = read_as_string("cordova.js")

regex = r"function injectScript\(url, onload, onerror\) {.*?^}"
substitution = r"""function injectScript(url, onload, onerror) {
    onload();
}
"""
cordovaJS = re.sub(regex, substitution, cordovaJS, flags = re.MULTILINE | re.DOTALL)

cordovaJS, pluginloaderJS = insert_file(cordovaJS, "cordova_plugins.js")

matches = re.match(r".*module.exports = (\[.*?\]);", pluginloaderJS, flags = re.MULTILINE | re.DOTALL)
if matches is None:
    raise ValueError("no plugins installed")

plugin_list = matches.group(1)
plugin_list = json.loads(plugin_list)
for plugin in plugin_list:
    cordovaJS, _ignored = insert_file(cordovaJS, plugin['file'])


if options.filename:
    destination = "%s/%s" % (CORDOVA_PATH, options.filename)
    with open(destination, "w") as f:
        f.write(cordovaJS)

    if options.uglify:
        cmd = "uglifyjs --screw-ie8 -o %s %s" % (destination, destination)
        print cmd
        call(cmd, shell=True)

    if options.md5:
        import hashlib, os, shutil
        path = os.path.dirname(destination)
        filename = os.path.basename(destination)

        md5 = hashlib.md5(open(destination).read()).hexdigest()
        print filename, path
        md5_dest = os.path.join(path, os.path.splitext(filename)[0] + "." + md5 + os.path.splitext(filename)[1])
        print "generating md5 filename", md5_dest
        shutil.copyfile(destination, md5_dest)
else:
    print cordovaJS

