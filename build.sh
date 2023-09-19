#!/bin/bash -e

old=$(grep Release: dnf-plugin-lockfile.spec| awk ' { print $2 } ')
new=$(echo "$old"+1 | bc)
sed -i "s/Release:        $old/Release:        $new/" ./dnf-plugin-lockfile.spec

git commit -a -m "Bump release from $old to $new"

rm -rf ~/rpmbuild/SOURCES/*
rm -rf ~/rpmbuild/SRPMS/*
tar -czvf ~/rpmbuild/SOURCES/dnf-plugin-lockfile-1.0.tar.gz --transform 's,^,dnf-plugin-lockfile-1.0/,' *
rpmbuild -bs ./dnf-plugin-lockfile.spec
copr build ralph/dnf-plugin-lockfile ~/rpmbuild/SRPMS/dnf-plugin-lockfile-1.0-$new.src.rpm