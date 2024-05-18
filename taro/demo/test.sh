#!/bin/bash
changesize() {
#read -p "$1:"
printf '\033]50;#%s\007' "$1"
#read -p "done!"
printf "aha"
}
changesize "+1"
changesize "+1"
changesize "-2"
changesize "+4"
changesize "-4"
