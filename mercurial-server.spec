%define name	mercurial-server
%define version	0.6
%define release %mkrel 1

Summary:	Mercurial authentication and authorization tools
Name:		%{name}
Version:	%{version}
Release:	%{release}
Source0:	%{name}-%{version}.tar.lzma
License:	GPLv2
Group:		Development/Other
Url:		http://hg.opensource.lshift.net/mercurial-server/
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildArch:	noarch
Requires:	mercurial, openssh-server

%description
mercurial-server makes a group of repositories available to the developers
you choose, identified by ssh keys, with easy key and access management
based on hg.

%prep
%setup -q

%install
%__rm -rf %{buildroot}
%__install -d -m 755 %{buildroot}%{py_sitedir}/mercurialserver/
%__install -d -m 755 %{buildroot}%{_datadir}/mercurial-server/init/

%__install -m 755 src/hg-ssh %{buildroot}%{_datadir}/mercurial-server/
%__install -m 755 src/refresh-auth %{buildroot}%{_datadir}/mercurial-server/
%__install -m 755 src/init/hginit %{buildroot}%{_datadir}/mercurial-server/init/
%__install -m 644 src/init/hgadmin-hgrc %{buildroot}%{_datadir}/mercurial-server/init/
%__install -m 755 src/mercurialserver/* %{buildroot}%{py_sitedir}/mercurialserver/

%__install -d -m 755 %{buildroot}%{_sysconfdir}/mercurial-server/keys

%__install -m 644 src/init/conf/remote-hgrc %{buildroot}%{_sysconfdir}/mercurial-server/
%__install -m 644 src/init/conf/access.conf %{buildroot}%{_sysconfdir}/mercurial-server/

%__install -d -m 755 root %{buildroot}%{_sysconfdir}/mercurial-server/keys/root/
%__install -d -m 755 %{buildroot}%{_sysconfdir}/mercurial-server/keys/users/

%__install -m 755 -d %{buildroot}/var/hg

%clean
%__rm -rf %{buildroot}

%pre
# Need to run usermod -U twice to unlock created account:
if ! getent passwd hg 2>&1 > /dev/null; then \
   /usr/sbin/useradd -r -m -d /var/hg -s /bin/bash -c "Mercurial repository server user" hg && \
   /usr/sbin/usermod -U hg && /usr/sbin/usermod -U hg 
fi

%post
[ -d /var/hg ] && [ ! -d /var/hg/repos ] && \
chown -R hg:hg /var/hg && \
/bin/su hg -c "/usr/share/mercurial-server/init/hginit /usr/share/mercurial-server"

cat <<EOF
-------------------------------------------------------------------------------
Place the SSH public key(s) of the user(s) who require access to the repository
in the directory /etc/mercurial-server/keys/root and run 
/usr/share/mercurial-server/refresh-auth while logged in as the user hg.
-------------------------------------------------------------------------------
EOF

%postun
/usr/sbin/userdel -r hg

%files
%defattr(-,root,root)
%doc LICENSE README doc/*
%{_sysconfdir}/mercurial-server/access.conf
%{_sysconfdir}/mercurial-server/remote-hgrc
%{_sysconfdir}/mercurial-server/keys/root/
%{_sysconfdir}/mercurial-server/keys/users/
%{_datadir}/mercurial-server/hg-ssh
%{_datadir}/mercurial-server/refresh-auth
%{_datadir}/mercurial-server/init/hginit
%{_datadir}/mercurial-server/init/hgadmin-hgrc
%{py_sitedir}/mercurialserver/*
/var/hg
