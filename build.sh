#!/bin/bash -e

rm -rf ~/rpmbuild/SOURCES/*
rm -rf ~/rpmbuild/SRPMS/*
tar -czvf ~/rpmbuild/SOURCES/dnf-plugin-lockfile-1.0.tar.gz *
rpmbuild -bs ./dnf-plugin-lockfile.spec
copr build ralph/dnf-plugin-lockfile ~/rpmbuild/SRPMS/dnf-plugin-lockfile-1.0-1.fc38.src.rpm