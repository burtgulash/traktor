#!/bin/bash

COMMANDS="try test run"

command=${1}
shift


with_pythonpath () {
    old_pythonpath=${PYTHONPATH}
    export PYTHONPATH=${PYTHONPATH}:$(pwd)
    python3 $1
    export PYTHONPATH=${old_pythonpath}
}


case ${command} in
"test")
    python3 -m pytest test ;;

"try")
    with_pythonpath examples/try.py
    ;;

"run")
    with_pythonpath $1
    ;;


*)
    echo "No command given! Use one of following:"
    for c in $(echo ${COMMANDS} | tr ' ' "\n" | sort)
    do
        echo "  $c"
    done

    exit 1
    ;;
esac
