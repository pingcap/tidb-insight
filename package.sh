#!/bin/sh

# make a release tarball

if [ -z $1 ]; then
  RELVER=`git describe --tags`
else
  RELVER=$1
fi
RELPATH=tidb-insight-${RELVER}

GO_RELEASE_BIN=go1.10.3.linux-amd64

BUILD_ROOT="`pwd`/.build"
mkdir -p ${BUILD_ROOT}
cd ${BUILD_ROOT}

if [ ! -f ${GO_RELEASE_BIN}.tar.gz ]; then
  wget https://dl.google.com/go/${GO_RELEASE_BIN}.tar.gz
  tar zxf ${GO_RELEASE_BIN}.tar.gz
fi

GOROOT="${BUILD_ROOT}/go"
GOPATH="${BUILD_ROOT}/.go"
export GOROOT GOPATH

# clean exist binaries
rm -rf ${BUILD_ROOT}/tidb-insight-*
mkdir -p ${BUILD_ROOT}/${RELPATH}/
cp -rf ${BUILD_ROOT}/../* ${BUILD_ROOT}/${RELPATH}/

cd ${BUILD_ROOT}/${RELPATH}/collector/

# prepare dependencies
GOBIN=${GOROOT}/bin/go make deps
# compile a static binary
GOBIN=${GOROOT}/bin/go make static

# clean unecessary files
cd ${BUILD_ROOT}/${RELPATH}
rm -rf collector docs tests Makefile package.sh *.log
find ${BUILD_ROOT}/${RELPATH} -name "*.pyc" | xargs rm

# make tarball archive
cd ${BUILD_ROOT}
tar zcf ${RELPATH}.tar.gz ${RELPATH}
