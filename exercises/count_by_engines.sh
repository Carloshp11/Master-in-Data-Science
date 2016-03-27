#!/bin/sh

Fichero_ENTRADA=$1
Number_engines=$2
Raw_ouput=$(csvgrep -d '^' -c nb_engines -m $Number_engines $Fichero_ENTRADA | wc -l)

echo "el fichero que has indicado se llama $Fichero_ENTRADA. $Number_engines engines"
echo "$(($Raw_ouput - 1))"

