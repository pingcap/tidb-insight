#!/bin/sh

# make a release tarball
PKGNAME=tidb-insight

git submodule update --init --recursive
if [ -z $1 ]; then
  RELVER=`git describe --tags`
else
  RELVER=$1
fi
RELPATH=${PKGNAME}-${RELVER}

GO_RELEASE_BIN=go1.10.3.linux-amd64

BUILD_ROOT="`pwd`/.build"
mkdir -p ${BUILD_ROOT}
cd ${BUILD_ROOT}

if [ ! -f ${GO_RELEASE_BIN}.tar.gz ]; then
  wget https://dl.google.com/go/${GO_RELEASE_BIN}.tar.gz
  tar zxf ${GO_RELEASE_BIN}.tar.gz
fi

# clean exist binaries
rm -rf ${BUILD_ROOT}/${PKGNAME} ${BUILD_ROOT}/${PKGNAME}-*.tar.gz
mkdir -p ${BUILD_ROOT}/${PKGNAME}
cp -rf ${BUILD_ROOT}/../* ${BUILD_ROOT}/${PKGNAME}/

# prepare dependencies
GOROOT="${BUILD_ROOT}/go"
GOPATH="${BUILD_ROOT}/${PKGNAME}"
export GOROOT GOPATH

cd ${BUILD_ROOT}/${PKGNAME}
ln -sfv vendor src

# compile a static binary
cd ${BUILD_ROOT}/${PKGNAME}/collector/
GOBIN=${GOROOT}/bin/go make static || exit 1

# compile other tools
cd ${BUILD_ROOT}/${PKGNAME}/tools/vmtouch
LDFLAGS="-static" make || exit 1
install -Dsm755 vmtouch ${BUILD_ROOT}/${PKGNAME}/bin/

# clean unecessary files
cd ${BUILD_ROOT}/${PKGNAME}/
rm -rf collector tools docs tests src vendor pkg Makefile package.sh Gopkg.* *.log
find ${BUILD_ROOT}/${PKGNAME}/ -name "*.pyc" | xargs rm 2>/dev/null

# make tarball archive
cd ${BUILD_ROOT}
tar zcf ${RELPATH}.tar.gz ${PKGNAME}
