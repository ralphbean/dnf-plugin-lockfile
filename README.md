# Nothing to see here.

Just messing around. See also [copr://ralph/dnf-plugin-lockfile](https://copr.fedorainfracloud.org/coprs/ralph/dnf-plugin-lockfile/).

# Hacking

```bash
# "Install" a development copy where system dnf will find it
❯ sudo ln -s $(pwd)/plugins/lockfile.py /usr/lib/python3.11/site-packages/dnf-plugins/lockfile.py
# Or, get a copr build
❯ sudo dnf copr enable ralph/dnf-plugin-lockfile
❯ sudo dnf install python3-dnf-plugin-lockfile
```

```bash
# Resolve a package
❯ dnf lockfile nethack
❯ cat rpms.txt
nethack-3.6.7-1.fc38
❯ dnf install $(cat rpms.txt)  # Works!
```

```bash
# Include all dependencies
❯ dnf lockfile nethack --recursive
Wrote 193 packages to /home/threebean/devel/dnf-plugin-lockfile/rpms.txt
❯ head rpms.txt
alternatives-1.25-1.fc38
audit-libs-3.1.2-1.fc38
authselect-1.4.2-2.fc38
authselect-libs-1.4.2-2.fc38
basesystem-11-15.fc38
bash-5.2.15-3.fc38
...
nethack-3.6.7-1.fc38
...
```

```bash
# Pin rpms to exactly where they came from. Super precise, but not relocatable
❯ dnf lockfile --format rpmurl nethack
❯ cat rpms.txt
https://nocix.mm.fcix.net/fedora/linux/releases/38/Everything/x86_64/os/Packages/n/nethack-3.6.7-1.fc38.x86_64.rpm
❯ dnf install $(cat rpms.txt)  # Works, but rpmdb has no history of which repo this was.
```

```bash
# Try to generate arguments for dnf. Doesn't really work due to repoid conflicts
❯ dnf lockfile --format repourl nethack
❯ cat rpms.txt
nethack-3.6.7-1.fc38 --repofrompath=fedora,https://nocix.mm.fcix.net/fedora/linux/releases/38/Everything/x86_64/os/
❯ dnf install $(cat rpms.txt)  # Doesn't quite work
```

```bash
# It would be cool if this worked.
❯ dnf lockfile --format metalink nethack
❯ cat rpms.txt
nethack-3.6.7-1.fc38 --metalink=https://mirrors.fedoraproject.org/metalink?repo=fedora-38&arch=x86_64
❯ dnf install $(cat rpms.txt)  # Not even a real dnf argument.
```

```bash
# Other ideas ...
❯ dnf lockfile --format pythonstyle nethack
❯ cat rpms.txt
nethack-3.6.7-1.fc38 @ metalink://https://mirrors.fedoraproject.org/metalink?repo=fedora-38&arch=x86_64
# This kind of syntax only makes sense if we implement a dnf plugin to _read_ rpms.txt
```
