import re

mystr = """lala
---- hello ------
------
lolo
lili
"""

tab = re.findall(r'^he(?s:.*)lili$',mystr, flags=re.M)
print(tab)

