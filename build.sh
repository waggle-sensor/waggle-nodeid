#!/bin/bash -e

print_help() {
  echo """
usage: build.sh [-f]

Create the versioned Debian package.

 -f : force the build to proceed (debugging only) without checking for tagged commit
"""
}

FORCE=
while getopts "f?" opt; do
  case $opt in
    f) # force build
      echo "** Force build: ignore tag depth check **"
      FORCE=1
      ;;
    ?|*)
      print_help
      exit 1
      ;;
  esac
done

# determine full version
RELEASE_VERSION=$(git describe --tags --long | cut -c2-)
DIRTY=$([[ -z $(git status -s) ]] || echo '-dirty')
VERSION=${RELEASE_VERSION}${DIRTY}

TAG_DEPTH=$(echo ${RELEASE_VERSION} | cut -d '-' -f 2)
if [[ -z "${FORCE}" && "${TAG_DEPTH}_" != "0_" ]]; then
  echo "Error:"
  echo "  The current git commit has not been tagged. Please create a new tag first to ensure a proper unique version number."
  echo "  Use -f to ignore error (for debugging only)."
  exit 1
fi

docker build -t waggle_nodeid_build .
docker run --rm \
  -v `pwd`:/output/ \
  -e VERSION=$VERSION \
  waggle_nodeid_build ./create_deb.sh
