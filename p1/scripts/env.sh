#!/usr/bin/env bash

cd $(dirname -- "$0")/..

print_help() {
    echo "Usage: $0 [OPTION]..."
    echo "Creates or deletes the project's virtual environment."
    echo
    echo "Options:"
    echo "  -d, --delete    delete instead of create"
    echo "  -h, --help      print this help menu"
}

create_env() {
    if [[ -d .venv ]]; then
        echo "Error: directory .venv already exists" >&2
        exit 1
    fi

    python -mvenv .venv
}

delete_env() {
    if [[ ! -d .venv ]]; then
        echo "Error: directory .venv does not exist" >&2
        exit 1
    fi

    rm -r .venv
}

action="create"

while [[ $# -gt 0 ]]; do
    case "$1" in
        -d|--delete)
            action="delete"
            shift
            ;;

        -h|--help)
            print_help
            exit
            ;;

        *)
            echo "Unknown option: $1" >&2
            print_help
            exit 1
            ;;
    esac
done

case "$action" in
    create)
        create_env
        ;;
    delete)
        delete_env
        ;;
esac

