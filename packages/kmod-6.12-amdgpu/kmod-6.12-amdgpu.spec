%global kernel_major 6.12
%global kernel_sources %{_cross_usrsrc}/kernels/%{kernel_major}
%global _cross_kver %{kernel_major}.53
%global _cross_kmoddir %{_cross_libdir}/modules/%{_cross_kver}
%global _ko ko

Name: %{_cross_os}kmod-6.12-amdgpu
Version: 30.10
Release: 1%{?dist}
Summary: AMD GPU drivers for the 6.12 kernel
License: GPL-2.0 WITH Linux-syscall-note
URL: https://www.amd.com/

Source0: https://repo.radeon.com/amdgpu/30.10.2/el/10/main/x86_64/amdgpu-dkms-6.14.14-2226257.el10.noarch.rpm
Source1: COPYING

BuildRequires: %{_cross_os}kernel-6.12-devel
Requires: %{_cross_os}kernel-6.12
Requires: %{_cross_os}linux-firmware-amd

%description
%{summary}.

%prep
# Extract DKMS source from RPM
rpm2cpio %{S:0} | cpio -idmu './usr/src/amdgpu-*'
find usr/src/ -mindepth 1 -maxdepth 1 -type d -exec mv {} amdgpu \;
rm -r usr

# Apply Bottlerocket DKMS configuration
pushd amdgpu

# Configure DKMS
KERNELVER=%{_cross_kver} amd/dkms/configure --with-linux=%{kernel_sources}

popd

%build
pushd amdgpu

# Build using the DKMS Makefile with static configuration
make modules   KERNELVER=6.12.53   kernel_build_dir=%{_cross_usrsrc}/kernels/6.12   CC=%{_cross_target}-gcc   ARCH=%{_cross_karch}   CROSS_COMPILE=%{_cross_target}-   EXTRA_CFLAGS=-DPACKAGE_VERSION=\\\"%{version}\\\"

popd

%install
# Install license file
install -d %{buildroot}%{_cross_licensedir}/%{name}
install -p -m 0644 %{S:1} %{buildroot}%{_cross_licensedir}/%{name}/

# Install AMD GPU kernel modules to correct location
install -d %{buildroot}%{_cross_kmoddir}/kernel/drivers/gpu/drm/amd/amdgpu
install -p -m 644 amdgpu/amd/amdkcl/amdkcl.ko %{buildroot}%{_cross_kmoddir}/kernel/drivers/gpu/drm/amd/amdgpu/
install -p -m 644 amdgpu/ttm/amdttm.ko %{buildroot}%{_cross_kmoddir}/kernel/drivers/gpu/drm/amd/amdgpu/
install -p -m 644 amdgpu/amddrm_ttm_helper.ko %{buildroot}%{_cross_kmoddir}/kernel/drivers/gpu/drm/amd/amdgpu/
install -p -m 644 amdgpu/amddrm_buddy.ko %{buildroot}%{_cross_kmoddir}/kernel/drivers/gpu/drm/amd/amdgpu/
install -p -m 644 amdgpu/amddrm_exec.ko %{buildroot}%{_cross_kmoddir}/kernel/drivers/gpu/drm/amd/amdgpu/
install -p -m 644 amdgpu/scheduler/amd-sched.ko %{buildroot}%{_cross_kmoddir}/kernel/drivers/gpu/drm/amd/amdgpu/
install -p -m 644 amdgpu/amd/amdxcp/amdxcp.ko %{buildroot}%{_cross_kmoddir}/kernel/drivers/gpu/drm/amd/amdgpu/
install -p -m 644 amdgpu/amd/amdgpu/amdgpu.ko %{buildroot}%{_cross_kmoddir}/kernel/drivers/gpu/drm/amd/amdgpu/

%files
%license %{_cross_licensedir}/%{name}/COPYING
%{_cross_attribution_file}
%{_cross_kmoddir}/kernel/drivers/gpu/drm/amd/amdgpu/amdkcl.%{_ko}
%{_cross_kmoddir}/kernel/drivers/gpu/drm/amd/amdgpu/amdttm.%{_ko}
%{_cross_kmoddir}/kernel/drivers/gpu/drm/amd/amdgpu/amddrm_ttm_helper.%{_ko}
%{_cross_kmoddir}/kernel/drivers/gpu/drm/amd/amdgpu/amddrm_buddy.%{_ko}
%{_cross_kmoddir}/kernel/drivers/gpu/drm/amd/amdgpu/amddrm_exec.%{_ko}
%{_cross_kmoddir}/kernel/drivers/gpu/drm/amd/amdgpu/amd-sched.%{_ko}
%{_cross_kmoddir}/kernel/drivers/gpu/drm/amd/amdgpu/amdxcp.%{_ko}
%{_cross_kmoddir}/kernel/drivers/gpu/drm/amd/amdgpu/amdgpu.%{_ko}
