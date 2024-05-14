import discogs_client as discogs
token = input("Input user token (https://www.discogs.com/settings/developers): ")
d = discogs.Client('ExampleApplication/0.1', user_token=token)
while True:
    title = input("Search title: ")
    catno = input("Catalog NO: ")
    if catno == "":
        results = results = d.search(title = title,type = 'release')
    else:
        results = d.search(title = title,type = 'release', catno = catno)
    barcode = [x.data['barcode'] for x in results]
    prevUnique = []
    while len(results) > 1:
        barcode = [x.data['barcode'] for x in results]
        unique = [x for row in barcode for x in row if sum(row.count(x) for row in barcode) == 1]
        if unique == []:
            break
        for elem in unique:
            print(elem)
        print("too many results to determine, type runout that matches")
        print("Use 'Q' to quit and 'NOT' for non-matching runout")
        var = input("runout: ")
        if var == "Q":
            break
        if "NOT" in var:
            var = var[var.find("NOT")+3:]
            new = [z for z in results if var not in str(z.data['barcode'])]
            if new == []:
                continue
            results = new
        else:
            new = [z for z in results if var in str(z.data['barcode'])]
            if new == []:
                continue
            results = new
    for res in results:
        print("https://www.discogs.com" + res.url)
    cont = input("Continue? (Y/N): ").lower()
    if cont == 'n ':
        break
