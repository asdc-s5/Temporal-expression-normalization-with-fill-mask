#!/bin/bash
LC_CTYPE=en_US.utf8
# Check if the correct number of command-line arguments is provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 arg1 arg2"
    exit 1
fi

# Extract command-line arguments
anchor="$1"
type="$2"
string="$3"
#vir="$4"

#echo "ARGS: $arg1 $arg2"

# Call the Python script and capture the returned value in a variable
cir=$(python timex_normalization.py "$type" "$string")
#python timex_normalization_prueba.py "$arg1" "$arg2"

#Poner la ruta relativa del jar en base a dónde esté este script
result=$(java -jar Annotador-master/out/artifacts/annotador_core_jar/annotador-core.jar $anchor $type $string $cir |  sed -n '2p')

# Print the result or use it as needed
echo "Result from Python script: $result"
