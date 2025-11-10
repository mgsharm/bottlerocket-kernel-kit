%global debug_package %{nil}

%global fwdir %{_cross_libdir}/firmware

# Many of the firmware files have specialized binary formats that are not supported
# by the strip binary used in __spec_install_post macro. Work around build failures
# by skipping striping.
%global __strip /usr/bin/true

Name: %{_cross_os}linux-firmware
Version: 20251021
Release: 1%{?dist}
Summary: Firmware files used by the Linux kernel
# The following list of SPDX identifiers was constructed with help of scancode
# tooling and has turned up the following licenses for different drivers by
# checking the different LICENCE/LICENSE files and the licenses in WHENCE:
# * BSD-Source-Code - myri10ge
# * LicenseRef-scancode-chelsio-linux-firmware - cxgb4
# * LicenseRef-scancode-qlogic-firmware - netxen_nic
# * LicenseRef-scancode-intel - i915, ice
# * LicenseRef-scancode-proprietary-license - bnx2x, qed
# * LicenseRef-scancode-free-unknown - tg3
License: GPL-1.0-or-later AND GPL-2.0-or-later AND BSD-Source-Code AND LicenseRef-scancode-chelsio-linux-firmware AND LicenseRef-scancode-qlogic-firmware AND LicenseRef-scancode-intel AND LicenseRef-scancode-proprietary-license AND LicenseRef-scancode-free-unknown
URL: https://www.kernel.org/

Source0: https://gitlab.com/kernel-firmware/linux-firmware/-/archive/%{version}/linux-firmware-%{version}.tar.gz

%description
%{summary}.

%prep
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
