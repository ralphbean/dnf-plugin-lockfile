# Nothing to see here.

Just messing around. See also [copr://ralph/dnf-plugin-lockfile](https://copr.fedorainfracloud.org/coprs/ralph/dnf-plugin-lockfile/).

# Hacking

```bash
# "Install" a development copy where system dnf will find it
❯ sudo ln -s $(pwd)/plugins/lockfile.py /usr/lib/python3.11/site-packages/dnf-plugins/lockfile.py

# Resolve a package
❯ dnf lockfile nethack
❯ cat rpms.txt
nethack-3.6.7-1.fc38

# Install those rpms
❯ dnf install $(cat rpms.txt)

# Pin more information about where the rpm came from
❯ dnf lockfile nethack --namespaced
❯ cat rpms.txt
nethack-3.6.7-1.fc38 @ metalink://https://mirrors.fedoraproject.org/metalink?repo=fedora-38&arch=x86_64

# But, we don't know what to do with that information yet...
❯ dnf install ...
```
