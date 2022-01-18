import json
with open("data/new_parsed.json", "r") as fIn:
    new = json.load(fIn)
nf = []
for k, entry in enumerate(new):
    try:
        if "not" in entry:
            entry = entry.replace("not found", "")
            nf.append(entry)
    except TypeError as e:
        pass
with open("data/not_found.json", "w") as fOut:
    json.dump(nf, fOut)
