import pandas as pd
import csv
def linear_coefs_to_csv(X,model,filename):
    D = {}
    coefs = model.coef_
    for idx, name in enumerate(X.columns):
        D[name] = coefs[idx]
    return(D)

    #write to file:
    with open(filename, 'w') as csv_file:
        writer = csv.writer(csv_file)
        for k, v in D.items():
           writer.writerow([k,v])
