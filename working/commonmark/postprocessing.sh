#!/bin/sh
sed -E -z 's/<!-- end list -->\n\n//g' -i ./*.md ./*.md
sed -E -z 's/```\n#!highlight ([a-z]+)[^\n]*/```\1/g' -i ./*.md ./*.md
sed -E -e 's/^\|\|/| | | |\n|---|---|---|\n/' -e 's/\|\| \|\|/|\n| /g' -e 's/\|\|/ | /g' -i ./*.md ./*.md
