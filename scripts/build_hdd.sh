#! /bin/bash
root=$(pwd)
cd ${root}
git_version=$(git rev-parse --short HEAD)

# install picire
cd ${root}/src/picire-21.8
version=$(cat picire/VERSION)
full_version="picire\s+${version}\+git${git_version}"
if pip list | grep -E "$full_version"; then
    echo "$full_version is already installed. Skipping installation."
else
    echo "$full_version is not installed. Installing..."
    pip install .
fi

# install picireny
cd ${root}/src/picireny-21.8
version=$(cat picireny/VERSION)
full_version="picireny\s+${version}\+git${git_version}"
if pip list | grep -E "$full_version"; then
    echo "$full_version is already installed. Skipping installation."
else
    echo "$full_version is not installed. Installing..."
    pip install .
fi

cd ${root}
