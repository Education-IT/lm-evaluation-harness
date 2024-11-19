import os
import json
import pprint
from collections import OrderedDict
lista = {
    
}

for filename in os.listdir("."):
    if filename.endswith(".json"):
        try:
            with open(filename,"r",encoding="UTF-8") as f:
                data = json.load(f)
                if "most_contaminated_domains" in data:
                    dic = data["most_contaminated_domains"]
                    for x in dic.items():
                        if x[0] in lista:
                            lista[x[0]] = lista[x[0]] + x[1]
                        else:
                            lista[x[0]] = x[1]
        except:
            print("ERROR")
lista = OrderedDict(sorted(lista.items(),key=lambda item: item[1],reverse=True))
with open("analizer.json","w",encoding="UTF-8") as f2:
    json.dump(lista,f2,indent=4)

pprint.pprint(lista)