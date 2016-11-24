# This makes Events its own package, which is useful for our purposes
import os

# This is weird but oh well:
for module in os.listdir(os.path.dirname(__file__)):
    if module == '__init__.py' or module[-3:] != '.py':
        continue
    __import__(module[:-3], locals(), globals())
del module