awk 'BEGIN {getline pattern < "lastVisited.txt"}
   NR == 1, $0 ~ pattern {next}; {print}' < $1
