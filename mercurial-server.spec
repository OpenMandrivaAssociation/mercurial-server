%define name	mercurial-server
%define version	1.2
%define release %mkrel 2

Summary:	Mercurial authentication and authorization tools
Name:		%{name}
Version:	%{version}
Release:	%{release}
Source0:	http://dev.lshift.net/paul/%{name}/%{name}_%{version}.tar.gz
License:	GPLv2
Group:		Development/Other
Url:		http://www.lshift.net/mercurial-server.html
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildArch:	noarch
Requires:	mercurial, openssh-server
BuildRequires:	xsltproc, docbook-style-xsl

%description
mercurial-server gives your developers remote read/write access to centralized
Mercurial repositories using SSH public key authentication; it provides
convenient and fine-grained key management and access control. 

%prep
%setup -q -n %{name}_%{version}.orig

%install
%__rm -rf %{buildroot}

%__install -d -m 755 %{buildroot}%{_sysconfdir}/mercurial-server/keys/root
%__install -d -m 755 %{buildroot}%{_sysconfdir}/mercurial-server/keys/users
%__install -m 644 src/init/conf/access.conf %{buildroot}%{_sysconfdir}/mercurial-server/

%__install -d -m 755 %{buildroot}%{_sysconfdir}/remote-hgrc.d
%__install -m 644 src/init/conf/remote-hgrc.d/* %{buildroot}%{_sysconfdir}/remote-hgrc.d

PYTHONDONTWRITEBYTECODE= %__python setup.py install --root=%{buildroot} --install-scripts=%{_datadir}/%{name} --install-data=%{_datadir}/%{name} --record=FILE_LIST

%__install -m 755 -d %{buildroot}/var/hg

pushd doc
xsltproc --nonet -o ../manual.html /usr/share/sgml/docbook/xsl-stylesheets/html/docbook.xsl manual.docbook

%clean
%__rm -rf %{buildroot}

%pre
# Need to run usermod -U twice to unlock created account:
if ! getent passwd hg 2>&1 > /dev/null; then \
   /usr/sbin/useradd -r -m -d /var/hg -s /bin/bash -c "Mercurial repository server user" hg && \
   /usr/sbin/usermod -U hg && /usr/sbin/usermod -U hg
fi

# .mercurial-server needs to be in the hg user directory:
[ ! -e ~hg/.mercurial-server ] && /bin/su hg -c "install -m 600 /etc/mercurial-server/init/dot-mercurial-server ~hg/.mercurial-server" 

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

%files -f FILE_LIST
%defattr(-,root,root)
%doc CREDITS LICENSE NEWS README manual.html
%config(noreplace) %{_sysconfdir}/mercurial-server/
%{_sysconfdir}/mercurial-server/access.conf
%{_sysconfdir}/remote-hgrc.d/access.rc
%{_sysconfdir}/remote-hgrc.d/logging.rc
/var/hg
