#!/bin/bash
for filename in ./*.csv; do
	original_string="$filename"
	string_to_replace_with=''
	no_dot="${original_string/'./'/$string_to_replace_with}"
    #echo $no_dot
    awk --assign filename="$filename" '{ print $filename ";" $0 }' "$filename" > ./modified_csv/$no_dot

    sed -i "1s/.*/Geo;Id;Fecha;Tmax;HTmax;Tmin;HTmin;Tmed;Racha;HRacha;Vmax;HVmax;TPrec;Prec1;Prec2;Prec3;Prec4/" ./modified_csv/$no_dot
done