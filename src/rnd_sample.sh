#!bash
# Generate a random sample of the Instracart datasetwc(1).
# requires wc(1), python3(1) and sed(1)
# Input: filename with the dataset.

set -o errexit

declare -i n_s n_l
declare f x

#
# Number of samples
#
(( n_s = 100 ))

#
# Sanitize the input
#
f="$1"

if [[ -z "$f" || x"$f" == "x-" ]]; then
	# If no file is supplied, or file is "-", read from stdin
        f="/dev/stdin"
else
	# Otherwise, sanitize the filename
	[[ x"${f#-}" != x"$f" || x"${f##*/}" == x"$f" ]] && f="./$f"
fi

# Determine number of lines in the file
read -r n_l x < <(/usr/bin/wc -l "$f")

if (( n_l < n_s )); then
	echo -E "File $f is too short for $n_s samples..."
	exit 1
fi

# Generate a string or random line numbers
x="$(echo -E "import random; print(random.sample(range(2, ${n_l}), ${n_s}))" |\
	/usr/bin/python)"

# Feed the above list to sed(1)
x="${x//, /p;}"
x="${x#\[}"

/usr/bin/sed -n "1p;${x/\]/p}" "$f"
