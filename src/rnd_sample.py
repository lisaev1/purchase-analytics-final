#!python3
import random, argparse, os, subprocess, sys

# Generate a random sample of the Instracart dataset (needs wc(1) and python3).
# Input:
#   filename with the dataset
# Output:
#   A random sample of the above dataset printed to stdout

#-- cmdline options
ap = argparse.ArgumentParser(description =
        "Generate a random sample of a dataset stored in a text file")
ap.add_argument("data", type = str, default = "-", metavar = "FILE",
   nargs = "?", help = "Filename with the dataset to sample")
ap.add_argument("-s", "--samples", type = int, default = 100,
        help = "Sample size (default: 100 lines)", metavar = "SAMPLES")
args = ap.parse_args()

#-- check that the file exists
if (not os.path.isfile(args.data)):
    print("File \"{}\" does not exist! Aborting.".format(args.data))
    sys.exit(1)
n_s = args.samples

#-- compute number of lines [we use wc(1) from coreutils because it gives about
#-- 10x performance boost compared to a pure python approach]
n_l = int(subprocess.check_output(["wc", "-l", "--",
    args.data]).decode().split(" ")[0])

if (n_l < n_s):
    print("File \"{}\" is too short for {} samples! Aborting.".format(args.data, n_s))
    sys.exit(1)

#-- generate samples
samp = random.sample(range(2, n_l), n_s)
samp.sort()

#-- open the file
fd = open(args.data, mode = "rt", newline = "")
for i, l in enumerate(fd, 1):
    if ((i in samp) or (i == 1)):
        print(l[:-1])

#-- close the fd
fd.close()
