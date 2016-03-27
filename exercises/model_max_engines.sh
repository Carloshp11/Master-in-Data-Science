#!/bin/sh


Fichero_ENTRADA=$1
#Model_max_engines="$(csvcut -d '^' -c model,nb_engines optd_aircraft.csv | head -2 | tail -n+2)"
echo "el fichero que has indicado se llama $Fichero_ENTRADA"
echo "$(csvcut -d '^' -c model,nb_engines $Fichero_ENTRADA | csvsort -c nb_engines -r  | csvcut -d ',' -c model | head -2 | tail -n+2)"

