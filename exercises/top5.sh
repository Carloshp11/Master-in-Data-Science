#!/bin/sh

# Esto es un comentario
Fichero_ENTRADA=$1
echo "el fichero que has indicado se llama $Fichero_ENTRADA"
SIN_CABECERA="tail -n+2 $Fichero_ENTRADA"
#$SIN_CABECERA
CORTAR_2A_COL="cut -d ^ -f 2"
SEG_COL="$SIN_CABECERA | $CORTAR_2A_COL"
$SEG_COL | sort -n -r | uniq -c | sort -g -r | head
