%global srcname lockfile
%global _description %{expand:
This plug-in generates lockfiles provided on the commandline.}

Name:           dnf-plugin-%{srcname}
Version:        1.0
Release:        %autorelease
Summary:        DNF plugin for Performance Metrics
License:        GPLv2
BuildArch:      noarch
URL:            https://github.com/ralphbean/dnf-plugin-lockfile
#Source0:        %{url}/archive/v%{version}/dnf-plugin-%{srcname}-%{version}.tar.gz
Source0:        %{url}/archive/refs/heads/main.tar.gz

BuildRequires:  cmake
BuildRequires:  python3-devel
BuildRequires:  python3-dnf

%description    %{_description}
%package -n     python3-%{name}
Summary:        %{summary}
Requires:       python3-dnf

%description -n python3-%{name} %{_description}

%prep
%autosetup -n dnf-plugin-%{srcname}-%{version} -p1

%build
%cmake
%cmake_build

%install
%cmake_install
install -Ddpm0755 %{buildroot}%{_localstatedir}/log/dnf/lockfile

%files -n       python3-%{name}
%license COPYING
%doc README.md
%{python3_sitelib}/dnf-plugin/%{srcname}.py
%{python3_sitelib}/dnf-plugin/__pycache__/*
%config(noreplace) %{_sysconfdir}/dnf/plugin/%{srcname}.conf
%dir %{_localstatedir}/log/dnf/lockfile

%changelog
%autochangelog