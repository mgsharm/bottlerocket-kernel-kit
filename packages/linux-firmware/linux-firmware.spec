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

Source0: https://www.kernel.org/pub/linux/kernel/firmware/linux-firmware-%{version}.tar.xz
Source1: https://www.kernel.org/pub/linux/kernel/firmware/linux-firmware-%{version}.tar.sign
Source2: gpgkey-4CDE8575E547BF835FE15807A31B6BD72486CFD6.asc

# Base package pulls in both firmware subpackages unconditionally
Requires: %{name}-amdgpu
Requires: %{name}-other

%description
%{summary}.

%package licenses
Summary: License files for linux-firmware
License: GPL-1.0-or-later AND GPL-2.0-or-later AND BSD-Source-Code AND LicenseRef-scancode-chelsio-linux-firmware AND LicenseRef-scancode-qlogic-firmware AND LicenseRef-scancode-intel AND LicenseRef-scancode-proprietary-license AND LicenseRef-scancode-free-unknown
URL: https://www.kernel.org/
Requires: %{name}-licenses-amdgpu
Requires: %{name}-licenses-other

%description licenses
%{summary}.

%package licenses-amdgpu
Summary: License files for amdgpu firmware
License: GPL-1.0-or-later AND GPL-2.0-or-later AND BSD-Source-Code
URL: https://www.kernel.org/

%description licenses-amdgpu
%{summary}.

%package licenses-other
Summary: License files for non-amdgpu firmware
License: GPL-1.0-or-later AND GPL-2.0-or-later AND BSD-Source-Code AND LicenseRef-scancode-chelsio-linux-firmware AND LicenseRef-scancode-qlogic-firmware AND LicenseRef-scancode-intel AND LicenseRef-scancode-proprietary-license AND LicenseRef-scancode-free-unknown
URL: https://www.kernel.org/

%description licenses-other
%{summary}.

%package other
Summary: Firmware for non-amdgpu hardware
Requires: %{name}-licenses-other

%description other
%{summary}.

%package amdgpu
Summary: Firmware for amdgpu drivers
Requires: %{name}-licenses-amdgpu

%description amdgpu
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
# Base package is empty - just pulls in dependencies

%files licenses
%{_cross_attribution_file}

%files licenses-amdgpu
%license LICENSE.amdgpu

%files licenses-other
%license LICENCE.* LICENSE.* GPL* WHENCE

%files other
%dir %{fwdir}
%exclude %{fwdir}/amdgpu
%{fwdir}/*

%files amdgpu
%dir %{fwdir}
%{fwdir}/amdgpu
