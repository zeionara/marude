#!/bin/bash

VERSION="$1"
BASE="$2"

if [ -z "$VERSION" ]; then
    echo "Version is required"
    exit 1
fi

if [ -z "$BASE" ]; then
    echo "Base version is required"
    exit 1
fi

root='assets/baneks'

target_folder="$root/$VERSION"
base_folder="$root/$BASE"

if [ ! -d "$target_folder" ]; then
    mkdir "$target_folder"
fi

target_files=""

for community in anekdotikategoriib baneks baneksbest; do
    echo "Handling community $community..."

    target_file="$target_folder/$community.tsv"
    base_file="$base_folder/$community.tsv"

    if [ -z "$target_files" ]; then
        target_files="$target_file"
    else
        target_files="$target_files $target_file"
    fi

    python -m marude anecdote fetch "$target_file" -a "$base_file" -c "$community"
done

merged_file="$target_folder/merged.tsv"

python -m marude anecdote merge $target_files $merged_file
python -m marude anecdote merge $base_folder/anecdotes.tsv $merged_file $target_folder/anecdotes.tsv -k
