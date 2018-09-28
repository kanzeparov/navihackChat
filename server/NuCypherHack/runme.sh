#!/bin/sh

set -e

# Directory name may end with '\n', and $(...) drops *all* the trailing '\n's.
# Work around that (older dirname versions don't have -z).
dirx=$(dirname -- "$0" && echo x)
newline_x='
x'
cd -- "${dirx%"$newline_x"}"

pause() {
    echo -n 'Press ENTER to continue...'
    read -r unused
    exit
}

usage() {
    echo >&2 'Wrong usage. Just run me without arguments.'
    exit 2
}

if [ "$#" -ne 0 ]; then
    if [ "$#" -ne 1 ]; then
        usage
    fi
    case "$1" in
        --server)
            ./chat.py bob-output carol-output < alice-input &
            ./chat.py alice-output carol-output < bob-input &
            ./chat.py alice-output bob-output < carol-input &
            wait
            pause
            ;;
        --alice)
            ./typewriter.py alice-output alice-input || true
            pause
            ;;
        --bob)
            ./typewriter.py bob-output bob-input || true
            pause
            ;;
        --carol)
            ./typewriter.py carol-output carol-input || true
            pause
            ;;
        *)
            usage
            ;;
    esac
fi

rm -f alice-input alice-output bob-input bob-output carol-input carol-output
mkfifo -m600 alice-input alice-output bob-input bob-output carol-input carol-output

exec env --unset=TMUX tmux \
    start-server \; \
    new-session ./runme.sh --server \; \
    split-window -h ./runme.sh --alice \; \
    split-window ./runme.sh --bob \; \
    split-window ./runme.sh --carol \; \
    rename-window chat
