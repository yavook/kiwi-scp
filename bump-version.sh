#!/bin/bash

this="$(readlink -f "${0}")"
this_dir="$(dirname "${this}")"

git_branch="$(git rev-parse --abbrev-ref HEAD)"
git_tag="$(git describe --abbrev=0)"
version_str="${git_branch##*/}"
version_str="0.1.6"

echo "${version_str}" > "${this_dir}/kiwi_scp/data/etc/version_tag"
sed -ri "s/(version\s*:).*$/\1 '${version_str}'/" "${this_dir}/example/kiwi.yml"
sed -ri "s/(version\s*=\s*).*$/\1\"${version_str}\"/" "${this_dir}/pyproject.toml"
