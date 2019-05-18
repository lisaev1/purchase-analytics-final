#!python3
import os, sys, csv, argparse

# The strategy is simple:
# 1. Read "products.csv" and make a python dictionary "prods" that maps
#    product_id -> python set of department_id, e.g. prod["123"] = {"4", "17"}
#    means that product 123 belongs to depts 4 and 17, while prod["34"] = {"2"}
#    implies product 34 belongs only to dept 2.
# 2. Loop over "order_products.csv" (i.e. over product_id) and count occurences
#    of each department_id extracted from "prod". Additionally, note if the
#    reordered field is = 0, in which case it's a 1st time order. The results
#    are stored in another dictionary of lists, "res" that contains
#    department_id as keys and lists of the form [n_ord, n_ord_1] for total
#    number of orders and 1st time orders, e.g. res["4"] = [27, 13] means that
#    dept 4 had 27 orders, of which 13 were 1st timers.
# 3. Rest of the code is trivial and is there to comform to the instructions.

# -----------------------------------------------------------------------------
# Subroutines
# -----------------------------------------------------------------------------

def _parseopts():
    """
    Parse cmdline options to determine source and output files. The file names
    are provided via optional arguments. Note, that repeated optional arguments
    are not allowed. E.g. -p xxx.csv -p yyy.csv will trigger an error.
    Returns:
        Tuple of 3 files (products database, orders database, reports file).
    """
    ap = argparse.ArgumentParser(description = "Order statistics by department")

    ap.add_argument("-p", "--prod-db", type = str,
            default = ["products.csv"],
            help = "Products database (default: products.csv)",
            action = "append",
            metavar = "FILE")

    ap.add_argument("-o", "--order-prod-db", type = str,
            default = ["order_products.csv"],
            help = "Database or orders (default: order_products.csv)",
            action = "append",
            metavar = "FILE")

    ap.add_argument("-r", "--report-to", type = str,
            default = ["report.csv"],
            help = "Redirect report to this file [\"-\" for stdout] (default: report.csv)",
            action = "append",
            metavar = "FILE")

    args = ap.parse_args()

    #-- abort if any flag is passed more than once
    if (len(args.prod_db) > 2):
        s = "products database"
    elif (len(args.order_prod_db) > 2):
        s = "orders database"
    elif (len(args.report_to) > 2):
        s = "reports"
    else:
        s = "x"

    if (s != "x"):
        print("ERROR: Several {} files passed! Please provide only one.".format(s))
        sys.exit(1)

    return (args.prod_db[-1], args.order_prod_db[-1], args.report_to[-1])



def _col_idx(r, *cols):
    """
    Returns indeces of named columns.
    Input:
        r (list) -- row, read from the csv file;
        cols (strings) -- required column names, e.g. "c1", "c2", "c3" (if a
                          name is not found in "r", its index will be "a", so
                          we fail with a bang somewhere);
    Returns:
        f2i (dictionary) -- field name to index mapping.
    """

    f2i = dict(zip(cols, ("a", ) * len(cols)))

    for i in range(len(r)):
        p = r[i].lower()

        if (p in f2i.keys()):
            if (f2i[p] != "a"):
                print("WARNING: Column {} is encountered more than once! Using the right-most one.".format(p))
            f2i[p] = i

    return f2i

# -----------------------------------------------------------------------------
# Main program
# -----------------------------------------------------------------------------

#-- parse cmdline arguments
f_prods, f_ord_prods, f_rep = _parseopts()

#-- check input files
j = 2 + len("product_id")
for fd, i in zip((f_prods, f_ord_prods),
                 (j + len("department_id"), j + len("reordered"))):
    if (not (os.path.isfile(fd) and (os.path.getsize(fd) >= i))):
        print("File \"{}\" does not exist or is too small! Aborting.".format(fd))
        sys.exit(1)

#
# Step 1 -- process the products database (we could use csv.DictReader(), but
# it's slow as hell)...
#
fd = open(f_prods, mode = "rt", newline = "")
data = csv.reader(fd, delimiter = ",", quotechar = '"')
r = next(data)

#-- let's not rely on fixed column order (f2i = field_2_index)
f2i = _col_idx(r, "product_id", "department_id")

#-- build the "prod" dict
print("Opening file " + f_prods + " ...")
prod = {}
i = 0
for r in data:
    p = r[f2i["product_id"]].lower()
    d = r[f2i["department_id"]].lower()

    if (p in prod.keys()):
        prod[p].add(d)
    else:
        prod[p] = {d}

    print("\r [busy] Processing line {}".format(i), end = "")
    i += 1

#-- close the fd (will be reused later)
fd.close()
print("\r [done] Processed {} lines".format(i) + 10 * " ")

#-- check if the file contained useful info and quit if not
if (i == 0):
    print("File \"{}\" had no relevant data! Aborting.".format(f_prods))
    sys.exit(1)

#
# Step 2 -- walk the list of orders and count purchases
#
fd = open(f_ord_prods, mode = "rt", newline = "")
data = csv.reader(fd, delimiter = ",", quotechar = '"')
r = next(data)

#-- again, we don't rely on fixed column order
f2i = _col_idx(r, "product_id", "reordered")

#-- build the "res" dict with results
print("\nOpening file " + f_ord_prods + " ...")
res = {}
i = 0
for r in data:
    p = r[f2i["product_id"]].lower()

    #-- skip unknown product_id
    if (p not in prod.keys()):
        continue

    j = r[f2i["reordered"]]
    
    #-- iterate over departments associated with product "p"
    #print("{} -> {}; {}".format(p, prod[p], j))
    for d in prod[p]:
        if (d in res.keys()):
            res[d][0] += 1
            if (j == "0"):
                res[d][1] += 1
        else:
            res[d] = [1, 0]
            if (j == "0"):
                res[d][1] = 1

    print("\r [busy] Processing line {}".format(i), end = "")
    i += 1

#-- close the fd
fd.close()
print("\r [done] Processed {} lines".format(i) + 10 * " ")

#-- check if the file contained useful info and quit if not
if (i == 0):
    print("File \"{}\" had no relevant data! Aborting.".format(f_prods))
    sys.exit(1)

#
# Step 3 -- sort results and write them to a file or stdout
#
res = {d: res[d] for d in \
        sorted(res.keys(), key = lambda x: int(x), reverse = False)}

#-- report is redirected to stdout
if (f_rep == "-"):
    print("{},{},{},{}".format("department_id", "number_of_orders",
        "number_of_first_orders", "percentage"))
    for d in res.keys():
        print("{},{},{},{:.2f}".format(d, res[d][0], res[d][1],
            res[d][1] / res[d][0]))

    sys.exit(0)

print("\nGenerating report in ", end = "")
fd = open(f_rep, "wt", newline = "")
data = csv.writer(fd, delimiter = ",", quotechar = '"', lineterminator = "\n")

data.writerow(("department_id", "number_of_orders", "number_of_first_orders",
    "percentage"))
for d in res.keys():
    data.writerow((d, res[d][0], res[d][1],
        "{:.2f}".format(res[d][1] / res[d][0])))

#-- close the fd
fd.close()

print(f_rep + "!")
