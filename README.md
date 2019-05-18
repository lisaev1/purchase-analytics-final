# purchase-analytics

## Table of Contents
1. Description
2. Approach
3. Usage
4. Thanks
5. License

## Description

This repository contains a solution to the Insight Data Engineering [challenge](https://github.com/InsightDataScience/Purchase-Analytics). See the link for a complete problem description.

## Approach

We adopt a standard approach of manipulating data using python dictionaries. Namely:

1. Read `products.csv` and make a python dictionary "prods" that maps "product_id" -> python set of "department_id", e.g. `prod["123"] = {"4", "17"}` means that product with ID = 123 belongs to depts 4 and 17, while `prod["34"] = {"2"}` means that product 34 belongs only to dept 2.
2. Loop over `order_products.csv` (i.e. over "product_id") and count occurrences of each "department_id" extracted from "prod". Additionally, note if the "reordered" field is = 0, in which case it's a 1st time order. The results are stored in another dictionary of lists, "res" that contains "department_id" as keys and lists of the form "[n_ord, n_ord_1]" for total number of orders and 1st time orders, e.g. `res["4"] = [27, 13]` means that dept. 4 had 27 orders, of which 13 were 1st timers.
3. "res" is sorted and dumped into the `report.csv` database.

## Usage

The above approach is implemented in **python 3** (tested with 3.7.3 on ArchLinux) and **bash > 4** (tested with 5.0.3, also on Arch). The python program is a bit more advanced since it reads filenames from cmdline, while the bash script hard-codes them.

The python script requires only [Python Standard Library](https://docs.python.org/3/library), while the bash program needs bc(1) and sort(1).

The full invocation is:
```
$ python3 src/p.py -h
usage: p.py [-h] [-p FILE] [-o FILE] [-r FILE]

Order statistics by department

optional arguments:
  -h, --help            show this help message and exit
  -p FILE, --prod-db FILE
                        Products database (default: products.csv)
  -o FILE, --order-prod-db FILE
                        Database or orders (default: order_products.csv)
  -r FILE, --report-to FILE
                        Redirect report to this file ["-" for stdout]
                        (default: report.csv)

$ python3 src/p.py -p input/products.csv -o input/order_products.csv \
	-r output/report.csv
```
By default, `p.py` operates on files in current dir, so the above invocation simplifies:
```
python3 src/p.py 
```

For the bash implementation (assuming the default datafiles location in the current director):
```
bash src/p.sh
```

Finally, there is a **bash** and a **python** script, `src/rnd_sample.sh` and `src/rnd_sample.py` respectively, that can be used to produce randomized datasets for testing purposes. Indeed, the original [dataset](https://www.instacart.com/datasets/grocery-shopping-2017) includes 'order_products.csv' files with ~ 10^7 lines (`products.csv` database is a relatively small ~ 5 * 10^4 lines file). To speed up testing, it makes sense to randomly sample the dataset and generate a file with ~ 100 lines. That's what `rnd_sample.??` do. The bash version is faster due to it's use of GNU sed(1) [but both scripts call wc(1)]. The invocations are:
```
$ bash src/rnd_sample.sh ~/instacart_2017_05_01/order_products__train.csv > \
	order_products.csv
```
or
```
$ python3 src/rnd_sample.py -h
usage: rnd_sample.py [-h] [-s SAMPLES] [FILE]

Generate a random sample of a dataset stored in a text file

positional arguments:
  FILE                  Filename with the dataset to sample

optional arguments:
  -h, --help            show this help message and exit
  -s SAMPLES, --samples SAMPLES
                        Sample size (default: 100 lines)

$ python3 src/rnd_sample.py ~/instacart_2017_05_01/order_products__train.csv > \
	order_products.csv
```

**Note:** All external programs like sed(1) are GNU. None of the scripts were tested with BSD implementations, so don't expect them to run natively on MacOS.

## Thanks

1. [BashFAQ](http://mywiki.wooledge.org/BashFAQ) -- scripting best practices;
2. [Arch](https://www.archlinux.org) -- amazing dev environment

## License

No license or copyright.
