import re
import toml

"""
mystr = '''lala
---- hello ------
------
lolo
lili
'''

tab = re.findall(r'^he(?s:.*)lili$',mystr, flags=re.M)
print(tab)
"""

parsed_toml = toml.load('sorter.toml')

print(parsed_toml)

print(not (re.search('lala','lolo',re.IGNORECASE)==None))


