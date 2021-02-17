%global solana_suffix testnet

%global solana_user   solana-%{solana_suffix}
%global solana_group  solana-%{solana_suffix}
%global solana_home   %{_localstatedir}/lib/solana/%{solana_suffix}/
%global solana_etc    %{_sysconfdir}/solana/%{solana_suffix}/

Name:       solana-%{solana_suffix}
Epoch:      0
Version:    1.5.8
Release:    1%{?dist}
Summary:    Solana blockchain software (%{solana_suffix} version)

License:    Apache-2.0
URL:        https://github.com/solana-labs/solana/
Source0:    https://github.com/solana-labs/solana/archive/v%{version}/solana-%{version}.tar.gz

# cargo vendor --offline
Source1:    solana-%{version}.cargo-vendor.tar.xz
Source2:    config.toml

Source3:    activate
Source4:    solana-validator.service
Source5:    solana-validator
Source6:    solana-sys-tuner.service
Source7:    solana-watchtower.service
Source8:    solana-watchtower

ExclusiveArch:  %{rust_arches}

BuildRequires:  rust-packaging
BuildRequires:  systemd-rpm-macros
BuildRequires:  gcc
BuildRequires:  clang
BuildRequires:  make
BuildRequires:  pkgconf-pkg-config
BuildRequires:  openssl-devel
BuildRequires:  zlib-devel

# libudev-devel
BuildRequires:  systemd-devel


%description
Web-Scale Blockchain for fast, secure, scalable, decentralized apps and marketplaces.
Version for %{solana_suffix}.


%package common
Summary: Solana common files (%{solana_suffix} version)


%description common
Solana common files (%{solana_suffix} version).


%package cli
Summary: Solana RPC CLI (%{solana_suffix} version)
Requires: %{name}-common = %{epoch}:%{version}-%{release}


%description cli
Solana RPC CLI (%{solana_suffix} version).


%package utils
Summary: Solana local utilities (%{solana_suffix} version)
Requires: %{name}-common = %{epoch}:%{version}-%{release}


%description utils
Solana local utilities (%{solana_suffix} version).


%package deps
Summary: Solana dependency libraries (%{solana_suffix} version)


%description deps
Solana dependency libraries (%{solana_suffix} version).


%package daemons
Summary: Solana daemons (%{solana_suffix} version)
Requires: %{name}-common = %{epoch}:%{version}-%{release}
Requires: %{name}-cli = %{epoch}:%{version}-%{release}
Requires: %{name}-utils = %{epoch}:%{version}-%{release}
Requires: %{name}-deps = %{epoch}:%{version}-%{release}
Requires: solana-perf-libs-%{solana_suffix}
Requires(pre): shadow-utils
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd


%description daemons
Solana daemons (%{solana_suffix} version).


%package bpf-utils
Summary: Solana BPF utilities (%{solana_suffix} version)
Requires: %{name}-common = %{epoch}:%{version}-%{release}


%description bpf-utils
Solana BPF utilities (%{solana_suffix} version).


%package tests
Summary: Solana tests and benchmarks (%{solana_suffix} version)
Requires: %{name}-common = %{epoch}:%{version}-%{release}
Requires: %{name}-deps = %{epoch}:%{version}-%{release}
Requires: solana-perf-libs-%{solana_suffix}


%description tests
Solana tests and benchmarks (%{solana_suffix} version).


%prep
%autosetup -b0 -n solana-%{version}
%autosetup -N -b1 -n solana-%{version}

mkdir .cargo
cp %{SOURCE2} .cargo/


%build
%{__cargo} build %{?_smp_mflags} -Z avoid-dev-deps --frozen --release

sed 's,__SUFFIX__,%{solana_suffix},g' \
        <%{SOURCE3} \
        >activate
sed 's,__SUFFIX__,%{solana_suffix},g' \
        <%{SOURCE4} \
        >solana-validator.service
sed 's,__SUFFIX__,%{solana_suffix},g' \
        <%{SOURCE5} \
        >solana-validator
sed 's,__SUFFIX__,%{solana_suffix},g' \
        <%{SOURCE6} \
        >solana-sys-tuner.service
sed 's,__SUFFIX__,%{solana_suffix},g' \
        <%{SOURCE7} \
        >solana-watchtower.service
sed 's,__SUFFIX__,%{solana_suffix},g' \
        <%{SOURCE8} \
        >solana-watchtower


%install
mkdir -p %{buildroot}/opt/solana/%{solana_suffix}/bin/deps
mkdir -p %{buildroot}/%{_unitdir}
mkdir -p %{buildroot}%{solana_home}
mkdir -p %{buildroot}%{solana_etc}
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig

mv activate \
        %{buildroot}/opt/solana/%{solana_suffix}/
mv solana-validator.service \
        %{buildroot}/%{_unitdir}/solana-validator-%{solana_suffix}.service
mv solana-validator \
        %{buildroot}%{_sysconfdir}/sysconfig/solana-validator-%{solana_suffix}
mv solana-sys-tuner.service \
        %{buildroot}/%{_unitdir}/solana-sys-tuner-%{solana_suffix}.service
mv solana-watchtower.service \
        %{buildroot}/%{_unitdir}/solana-watchtower-%{solana_suffix}.service
mv solana-watchtower \
        %{buildroot}%{_sysconfdir}/sysconfig/solana-watchtower-%{solana_suffix}

find target/release -mindepth 1 -maxdepth 1 -type d -exec rm -r "{}" \;
rm target/release/*.d
rm target/release/*.rlib
# Excluded because we do not need installers.
rm target/release/solana-install target/release/solana-install-init target/release/solana-ledger-udev
# Excluded. 
# TODO: Why? Official binary release does not contain these, only libsolana_*_program.so installed.
rm target/release/libsolana_frozen_abi_macro.so target/release/libsolana_ownable.so target/release/libsolana_sdk_macro.so

mv target/release/*.so \
        %{buildroot}/opt/solana/%{solana_suffix}/bin/deps/
mv target/release/* \
        %{buildroot}/opt/solana/%{solana_suffix}/bin/


%files common
/opt/solana/%{solana_suffix}/activate


%files cli
/opt/solana/%{solana_suffix}/bin/solana
/opt/solana/%{solana_suffix}/bin/solana-gossip
/opt/solana/%{solana_suffix}/bin/solana-ip-address
/opt/solana/%{solana_suffix}/bin/solana-stake-accounts
/opt/solana/%{solana_suffix}/bin/solana-stake-monitor
/opt/solana/%{solana_suffix}/bin/solana-stake-o-matic
/opt/solana/%{solana_suffix}/bin/solana-tokens


%files utils
/opt/solana/%{solana_suffix}/bin/solana-csv-to-validator-infos
/opt/solana/%{solana_suffix}/bin/solana-keygen
/opt/solana/%{solana_suffix}/bin/solana-log-analyzer
/opt/solana/%{solana_suffix}/bin/solana-ledger-tool
/opt/solana/%{solana_suffix}/bin/solana-genesis
/opt/solana/%{solana_suffix}/bin/solana-store-tool
/opt/solana/%{solana_suffix}/bin/solana-upload-perf
/opt/solana/%{solana_suffix}/bin/solana-net-shaper


%files deps
/opt/solana/%{solana_suffix}/bin/deps/libsolana_budget_program.so
/opt/solana/%{solana_suffix}/bin/deps/libsolana_exchange_program.so
/opt/solana/%{solana_suffix}/bin/deps/libsolana_failure_program.so
/opt/solana/%{solana_suffix}/bin/deps/libsolana_noop_program.so


%files daemons
/opt/solana/%{solana_suffix}/bin/solana-faucet
/opt/solana/%{solana_suffix}/bin/solana-ip-address-server
/opt/solana/%{solana_suffix}/bin/solana-sys-tuner
/opt/solana/%{solana_suffix}/bin/solana-validator
/opt/solana/%{solana_suffix}/bin/solana-watchtower

%{_unitdir}/solana-validator-%{solana_suffix}.service
%{_unitdir}/solana-sys-tuner-%{solana_suffix}.service
%{_unitdir}/solana-watchtower-%{solana_suffix}.service
%attr(0640,root,%{solana_group}) %config(noreplace) %{_sysconfdir}/sysconfig/solana-validator-%{solana_suffix}
%attr(0640,root,%{solana_group}) %config(noreplace) %{_sysconfdir}/sysconfig/solana-watchtower-%{solana_suffix}

%attr(0750,root,%{solana_group}) %dir %{solana_etc}
%attr(0750,%{solana_user},%{solana_group}) %dir %{solana_home}


%files bpf-utils
/opt/solana/%{solana_suffix}/bin/cargo-build-bpf
/opt/solana/%{solana_suffix}/bin/cargo-test-bpf


%files tests
/opt/solana/%{solana_suffix}/bin/solana-accounts-bench
/opt/solana/%{solana_suffix}/bin/solana-banking-bench
/opt/solana/%{solana_suffix}/bin/solana-bench-exchange
/opt/solana/%{solana_suffix}/bin/solana-bench-streamer
/opt/solana/%{solana_suffix}/bin/solana-bench-tps
/opt/solana/%{solana_suffix}/bin/solana-dos
/opt/solana/%{solana_suffix}/bin/solana-merkle-root-bench
/opt/solana/%{solana_suffix}/bin/solana-poh-bench
/opt/solana/%{solana_suffix}/bin/solana-test-validator
/opt/solana/%{solana_suffix}/bin/solana-ramp-tps


%pre daemons
# TODO: Separate user for each daemon.
getent group %{solana_group} >/dev/null || groupadd -r %{solana_group}
getent passwd %{solana_user} >/dev/null || \
        useradd -r -s /sbin/nologin -d %{solana_home} -M \
        -c 'Solana (%{solana_suffix})' -g %{solana_group} %{solana_user}
exit 0


%post daemons
%systemd_post solana-validator-%{solana_suffix}.service
%systemd_post solana-sys-tuner-%{solana_suffix}.service
%systemd_post solana-watchtower-%{solana_suffix}.service


%preun daemons
%systemd_preun solana-validator-%{solana_suffix}.service
%systemd_preun solana-sys-tuner-%{solana_suffix}.service
%systemd_preun solana-watchtower-%{solana_suffix}.service


%postun daemons
%systemd_postun_with_restart solana-validator-%{solana_suffix}.service
%systemd_postun_with_restart solana-sys-tuner-%{solana_suffix}.service
%systemd_postun_with_restart solana-watchtower-%{solana_suffix}.service


%changelog
* Wed Feb 17 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.5.8-1
- Update to 1.5.8

* Sat Feb 13 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.5.7-1
- Initial packaging
