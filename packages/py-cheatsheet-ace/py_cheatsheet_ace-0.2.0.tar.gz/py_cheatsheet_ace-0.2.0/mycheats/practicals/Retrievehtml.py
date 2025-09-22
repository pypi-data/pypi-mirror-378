#<html>
#<head>
 #   <title>sample page</title>
#</head>
#<body>
 #   <h1>
  #  talk to yourself once in a day.
   # otherwise person you miss meeting an
   # intelligent person on this world
    #</h1>
#</body>
#</html>
import re

# This code requires the 'a.html' file to be in the same directory
file = open('a.html', 'r')
content = file.read()
file.close()

print("matche for 's': ", re.findall(r's', content))