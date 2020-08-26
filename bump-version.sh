#!/bin/bash

this="$(readlink -f "${0}")"
this_dir="$(dirname "${this}")"

git_branch="$(git rev-parse --abbrev-ref HEAD)"
version_str="${git_branch##*/}"

echo "${version_str}" > "${this_dir}/src/etc/version_tag"
sed -ri "s/(version\s*:).*$/\1 '${version_str}'/" "${this_dir}/example/kiwi.yml"
