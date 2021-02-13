%global solana_suffix testnet

%global solana_user   solana-%{solana_suffix}
%global solana_group  solana-%{solana_suffix}
%global solana_home   %{_localstatedir}/lib/solana/%{solana_suffix}/
%global solana_etc    %{_sysconfdir}/solana/%{solana_suffix}/

Name:       solana-%{solana_suffix}
Version:    1.5.7
Release:    1%{?dist}
Summary:    Web-Scale Blockchain for fast, secure, scalable, decentralized apps and marketplaces

License:    Apache-2.0
URL:        https://github.com/solana-labs/solana/
Source0:    https://github.com/solana-labs/solana/archive/v%{version}/solana-%{version}.tar.gz

# cargo vendor --locked
Source1:    solana-%{version}.cargo-vendor.tar.xz
Source2:    config.toml

Source3:    activate
Source4:    solana-validator.service
Source5:    solana-validator
Source6:    solana-sys-tuner.service

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

Requires: solana-perf-libs-%{solana_suffix}


%description
Web-Scale Blockchain for fast, secure, scalable, decentralized apps and marketplaces.


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


%install
mkdir -p %{buildroot}/opt/solana/%{solana_suffix}/bin/deps
mkdir -p %{buildroot}/%{_unitdir}
mkdir -p %{buildroot}%{solana_home}
mkdir -p %{buildroot}%{solana_etc}
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig

cp -p \
        activate \
        %{buildroot}/opt/solana/%{solana_suffix}/
cp -p \
        solana-validator.service \
        %{buildroot}/%{_unitdir}/solana-validator-%{solana_suffix}.service
cp -p \
        solana-validator \
        %{buildroot}%{_sysconfdir}/sysconfig/solana-validator-%{solana_suffix}
cp -p \
        solana-sys-tuner.service \
        %{buildroot}/%{_unitdir}/solana-sys-tuner-%{solana_suffix}.service

cd target/release

# Excluded:
#     solana-install
#     solana-install-init
cp -p \
        cargo-build-bpf \
        cargo-test-bpf \
        solana \
        solana-bench-exchange \
        solana-bench-tps \
        solana-dos \
        solana-faucet \
        solana-genesis \
        solana-gossip \
        solana-keygen \
        solana-ledger-tool \
        solana-log-analyzer \
        solana-net-shaper \
        solana-stake-accounts \
        solana-stake-monitor \
        solana-stake-o-matic \
        solana-sys-tuner \
        solana-test-validator \
        solana-tokens \
        solana-validator \
        solana-watchtower \
        %{buildroot}/opt/solana/%{solana_suffix}/bin/

# Excluded (TODO: why? official binary release does not contain these)
#     libsolana_frozen_abi_macro.so
#     libsolana_ownable.so
#     libsolana_sdk_macro.so
cp -p \
        libsolana_budget_program.so \
        libsolana_exchange_program.so \
        libsolana_failure_program.so \
        libsolana_noop_program.so \
        %{buildroot}/opt/solana/%{solana_suffix}/bin/deps/


%files
/opt/solana/%{solana_suffix}
%{_unitdir}/solana-validator-%{solana_suffix}.service
%{_unitdir}/solana-sys-tuner-%{solana_suffix}.service
%attr(0640,root,%{solana_group}) %config(noreplace) %{_sysconfdir}/sysconfig/solana-validator-%{solana_suffix}

%attr(0750,root,%{solana_group}) %dir %{solana_etc}
%attr(0750,%{solana_user},%{solana_group}) %dir %{solana_home}


%pre
getent group %{solana_group} >/dev/null || groupadd -r %{solana_group}
getent passwd %{solana_user} >/dev/null || \
        useradd -r -s /sbin/nologin -d %{solana_home} -M \
        -c 'Solana (%{solana_suffix})' -g %{solana_group} %{solana_user}
exit 0


%post
%systemd_post solana-validator-%{solana_suffix}.service
%systemd_post solana-sys-tuner-%{solana_suffix}.service


%preun
%systemd_preun solana-validator-%{solana_suffix}.service
%systemd_preun solana-sys-tuner-%{solana_suffix}.service


%postun
%systemd_postun_with_restart solana-validator-%{solana_suffix}.service
%systemd_postun_with_restart solana-sys-tuner-%{solana_suffix}.service


%changelog
* Sat Feb 13 2021 Ivan Mironov <mironov.ivan@gmail.com> - 1.5.7-1
- Initial packaging
