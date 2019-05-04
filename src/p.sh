#!bash

export LC_ALL=C
set -o errexit

# This is bash version of "p.py". Python is only useful because of its "csv"
# module. However, for this dataset one can simply split lines based on ","
# because in "products.csv" "department_id" is te last field, so its OK if we
# don't parse product description properly.

# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------

# Find an index of a given field into the row.
# Input:
#   $1 = key to look for
#   $2 = row from the database
# Output:
#   Integer index

_index() {
        local -i i j
        local -a a

        IFS="," read -ra a <<< "$2"

        for (( i = 0; i < ${#a[@]}; ++i )); do
                if [[ x"${a[i]}" == x"$1" ]]; then
                        (( j = i ))
                        break
                fi
        done

        echo -nE "${j:-"a"}"
}

# -----------------------------------------------------------------------------
# Main program
# -----------------------------------------------------------------------------

declare f_ord_prods f_prods p d r
declare -i i j
declare -A prod res
declare -a idx row a

f_prods="products.csv"
f_ord_prods="order_products.csv"

#
# Parse "products.csv" and build the "prod" array that maps "product_id" to a
# string of @-separated "department_id", e.g. prop["123"]="13@3@53".
#
IFS="," read -r r < "$f_prods"

idx=()
for p in "product_id" "department_id"; do
	idx+=("$(_index "$p" "$r")")
done

#-- read "products.csv" for real, skipping 1st line
{
	#-- check that "product_id" / "department_id" are 1st / last fields
	IFS="," read -ra row
	(( idx[1] - ${#row[@]} + 1 )) && echo -E \
		"WARNING: \"department_id\" is NOT the last field. Results might be incorrect!"
	(( idx[0] )) && echo -E \
		"WARNING: \"product_id\" is NOT the first field. Results might be incorrect!"

	(( idx[1] = -1 ))
	while IFS="," read -ra row; do
		p="${row[idx[0]]}"
		d="${row[idx[1]]}"

		if [[ -v prod["$p"] ]]; then
			prod["$p"]+="@$d"
		else
			prod["$p"]="$d"
		fi
	done
} < "$f_prods"

#
# Parse "order_products.csv" and 
#
IFS="," read -r r < "$f_ord_prods"

idx=()
for p in "product_id" "reordered"; do
	idx+=("$(_index "$p" "$r")")
done

#-- read "order_products.csv" for real, skipping 1st line
{
	#-- check that "product_id" / "department_id" is indeed the last field
	IFS="," read -ra row
	(( idx[1] - ${#row[@]} + 1 )) && echo -E \
		"WARNING: \"reordered\" is NOT the last field. Results might be incorrect!"
	(( idx[0] )) && echo -E \
		"WARNING: \"product_id\" is NOT the first field. Results might be incorrect!"

	(( idx[1] = -1 ))
	while IFS="," read -ra row; do
		p="${row[idx[0]]}"

		#-- skip unknown "product_id"
		[[ -v prod["$p"] ]] || continue

		r="${row[idx[1]]}"

		#-- iterate over departments associated with product "p"
		IFS="@" read -ra a <<< "${prod["$p"]}"

		for d in "${a[@]}"; do
			if [[ -v res["$d"] ]]; then
				IFS="@" read -r i j <<< "${res["$d"]}"

				[[ x"$r" == "x0" ]] && (( ++j ))
				res["$d"]="$(( ++i ))@$j"
			else
				if [[ x"$r" == "x0" ]]; then
					res["$d"]="1@1"
				else
					res["$d"]="1@0"
				fi
			fi
		done
	done
} < "$f_ord_prods"

#
# Print sorted results
#
for d in "${!res[@]}"; do
	IFS="@" read -ra a <<< "${res["$d"]}"
	echo -E "$d ${a[@]} $(echo -E "scale = 3; ${a[1]} / ${a[0]}" | /usr/bin/bc -l)"
done | /usr/bin/sort -nk 1