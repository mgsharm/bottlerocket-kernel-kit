%global debug_package %{nil}

%global fwdir %{_cross_libdir}/firmware

# Many of the firmware files have specialized binary formats that are not supported
# by the strip binary used in __spec_install_post macro. Work around build failures
# by skipping striping.
%global __strip /usr/bin/true

Name: %{_cross_os}linux-firmware-amd
Version: 20251021
Release: 1%{?dist}
Summary: AMD GPU firmware files for the Linux kernel
License: Redistributable
URL: https://www.kernel.org/

Source0: https://www.kernel.org/pub/linux/kernel/firmware/linux-firmware-%{version}.tar.xz
Source1: https://www.kernel.org/pub/linux/kernel/firmware/linux-firmware-%{version}.tar.sign
Source2: gpgkey-4CDE8575E547BF835FE15807A31B6BD72486CFD6.asc

%description
%{summary}.

%prep
%{gpgverify} --data=<(xzcat %{S:0}) --signature=%{S:1} --keyring=%{S:2}
%autosetup -n linux-firmware-%{version} -p1

%build

%install
mkdir -p %{buildroot}/%{fwdir}
mkdir -p %{buildroot}/%{fwdir}/updates

# Use zstd compression for firmware files to reduce size on disk. This relies on
# kernel support through FW_LOADER_COMPRESS (and FW_LOADER_COMPRESS_ZSTD for kernels >=5.19)
install -d %{buildroot}/%{fwdir}
./copy-firmware.sh --zstd --ignore-duplicates %{buildroot}/%{fwdir}

%files
%dir %{fwdir}
%{fwdir}/*
%license LICENCE.* LICENSE.* GPL* WHENCE
%{_cross_attribution_file}
