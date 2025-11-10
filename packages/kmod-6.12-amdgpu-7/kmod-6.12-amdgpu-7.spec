%global kernel_major 6.12
%global kernel_sources %{_cross_usrsrc}/kernels/%{kernel_major}
%global _cross_kver %{kernel_major}.53
%global _cross_kmoddir %{_cross_libdir}/modules/%{_cross_kver}

Name: %{_cross_os}kmod-6.12-amdgpu-7
Version: 30.10
Release: 1%{?dist}
Summary: AMD GPU drivers for the 6.12 kernel
License: Apache-2.0 OR MIT
URL: https://www.amd.com/

Source0: https://repo.radeon.com/amdgpu/30.10.2/el/10/main/x86_64/amdgpu-dkms-6.14.14-2226257.el10.noarch.rpm
Source103: amdgpu-modules-load.conf

BuildRequires: %{_cross_os}kernel-6.12-devel

%description
%{summary}.

%prep
# Extract DKMS source from RPM
rpm2cpio %{S:0} | cpio -idmu './usr/src/amdgpu-*'
find usr/src/ -mindepth 1 -maxdepth 1 -type d -exec mv {} amdgpu \;
rm -r usr

# Apply Bottlerocket DKMS configuration
pushd amdgpu

# Create HDCP stub functions
mkdir -p amd/amdkcl
cat > amd/amdkcl/kcl_hdcp_stubs.c << 'HDCP_EOF'
/*
 * HDCP stub functions for Bottlerocket
 * These symbols are not available in the Bottlerocket kernel
 */

#include <linux/module.h>
#include <drm/drm_connector.h>

/* Stub implementation for missing HDCP symbols */
int drm_connector_attach_content_protection_property(struct drm_connector *connector)
{
	/* HDCP not supported in Bottlerocket kernel */
	return 0;
}
EXPORT_SYMBOL(drm_connector_attach_content_protection_property);

void drm_hdcp_update_content_protection(struct drm_connector *connector, u64 val)
{
	/* HDCP not supported in Bottlerocket kernel */
}
EXPORT_SYMBOL(drm_hdcp_update_content_protection);

int drm_hdmi_infoframe_set_hdr_metadata(void *frame, void *conn_state)
{
	/* HDR metadata not supported without HDCP in Bottlerocket kernel */
	return -ENODEV;
}
EXPORT_SYMBOL(drm_hdmi_infoframe_set_hdr_metadata);
HDCP_EOF

# Modify the amdkcl Makefile to include HDCP stubs
echo 'amdkcl-y += kcl_hdcp_stubs.o' >> amd/amdkcl/Makefile

# Configure DKMS
KERNELVER=%{_cross_kver} amd/dkms/configure --with-linux=%{kernel_sources}

popd

%build
pushd amdgpu

# Build using the DKMS Makefile with static configuration
make modules   KERNELVER=6.12.53   kernel_build_dir=%{_cross_usrsrc}/kernels/6.12   CC=%{_cross_target}-gcc   ARCH=%{_cross_karch}   CROSS_COMPILE=%{_cross_target}-   EXTRA_CFLAGS=-DPACKAGE_VERSION=\\\"%{version}\\\"

popd

%install
# Install AMD GPU kernel modules to correct location
install -d %{buildroot}%{_cross_kmoddir}/extra
install -p -m 644 amdgpu/amd/amdkcl/amdkcl.ko %{buildroot}%{_cross_kmoddir}/extra/
install -p -m 644 amdgpu/ttm/amdttm.ko %{buildroot}%{_cross_kmoddir}/extra/
install -p -m 644 amdgpu/amddrm_ttm_helper.ko %{buildroot}%{_cross_kmoddir}/extra/
install -p -m 644 amdgpu/amddrm_buddy.ko %{buildroot}%{_cross_kmoddir}/extra/
install -p -m 644 amdgpu/amddrm_exec.ko %{buildroot}%{_cross_kmoddir}/extra/
install -p -m 644 amdgpu/scheduler/amd-sched.ko %{buildroot}%{_cross_kmoddir}/extra/
install -p -m 644 amdgpu/amd/amdxcp/amdxcp.ko %{buildroot}%{_cross_kmoddir}/extra/
install -p -m 644 amdgpu/amd/amdgpu/amdgpu.ko %{buildroot}%{_cross_kmoddir}/extra/

# Install modules-load.d configuration for automatic module loading
install -d %{buildroot}%{_cross_libdir}/modules-load.d
install -m 0644 %{S:103} %{buildroot}%{_cross_libdir}/modules-load.d/amdgpu.conf

# Create attribution.txt file
install -d %{buildroot}%{_cross_licensedir}/kmod-6.12-amdgpu-7
echo "AMD GPU DKMS drivers version %{version}-%{release}" > %{buildroot}%{_cross_licensedir}/kmod-6.12-amdgpu-7/attribution.txt
echo "Source: %{url}" >> %{buildroot}%{_cross_licensedir}/kmod-6.12-amdgpu-7/attribution.txt

%files
%{_cross_licensedir}/kmod-6.12-amdgpu-7/attribution.txt
%{_cross_kmoddir}/extra/amdkcl.ko
%{_cross_kmoddir}/extra/amdttm.ko
%{_cross_kmoddir}/extra/amddrm_ttm_helper.ko
%{_cross_kmoddir}/extra/amddrm_buddy.ko
%{_cross_kmoddir}/extra/amddrm_exec.ko
%{_cross_kmoddir}/extra/amd-sched.ko
%{_cross_kmoddir}/extra/amdxcp.ko
%{_cross_kmoddir}/extra/amdgpu.ko
%{_cross_libdir}/modules-load.d/amdgpu.conf
