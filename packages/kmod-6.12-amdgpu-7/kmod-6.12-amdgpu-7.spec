Name: %{_cross_os}kmod-6.12-amdgpu-7
Version: 30.10.2
Release: 1%{?dist}
Summary: AMD GPU drivers for the 6.12 kernel
# We use these licences because we only ship our own software in the main package,
# each subpackage includes the LICENSE file provided by the Licenses.toml file
License: Apache-2.0 OR MIT  #TODO: Validate license
URL: https://www.amd.com/

Source0: https://repo.radeon.com/amdgpu/30.10.2/el/10/main/x86_64/amdgpu-dkms-6.14.14-2226257.el10.noarch.rpm

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

# Create DKMS configuration
mkdir -p amd/dkms/config
cat > amd/dkms/config/config.h << 'CONFIG_EOF'
/* config.h - Static configuration for Bottlerocket */
#define PACKAGE_NAME amdgpu-dkms
#define PACKAGE_VERSION 30.10.2
#define HAVE_DMA_RESV_SEQ_BUG 1
#define HAVE_RESERVATION_WW_CLASS_BUG 1
#define HAVE_AMDKCL_FLAGS_TAKE_PATH 1
#define HAVE_KVREALLOC_3ARG 1
#define HAVE_AMDKCL_HMM_MIRROR_ENABLED 1
/* Disable HDCP features - symbols not available in Bottlerocket kernel */
#define HAVE_DRM_CONNECTOR_ATTACH_CONTENT_PROTECTION_PROPERTY 0
#define HAVE_DRM_HDMI_INFOFRAME_SET_HDR_METADATA 0
#define HAVE_DRM_HDCP_UPDATE_CONTENT_PROTECTION 0
/* Additional kernel compatibility defines */
#define HAVE_DRM_DISPLAY_HDCP_HELPER 0
CONFIG_EOF

mkdir -p amd/dkms
cat > amd/dkms/dkms-config.mk << 'DKMS_EOF'
export OS_NAME=bottlerocket
export OS_VERSION=1.0
subdir-ccflags-y += -DOS_NAME_BOTTLEROCKET
subdir-ccflags-y += -DOS_VERSION_MAJOR=1
subdir-ccflags-y += -DOS_VERSION_MINOR=0
subdir-ccflags-y += -DDRM_VER=6 -DDRM_PATCH=12 -DDRM_SUB=0
export CONFIG_HSA_AMD=y
export CONFIG_DRM_AMDGPU_CIK=y
export CONFIG_DRM_AMDGPU_SI=y
export CONFIG_DRM_AMDGPU_USERPTR=y
export CONFIG_DRM_AMD_DC=y
subdir-ccflags-y += -DCONFIG_HSA_AMD
subdir-ccflags-y += -DCONFIG_DRM_AMDGPU_CIK
subdir-ccflags-y += -DCONFIG_DRM_AMDGPU_SI
subdir-ccflags-y += -DCONFIG_DRM_AMDGPU_USERPTR
subdir-ccflags-y += -DCONFIG_DRM_AMD_DC
# Disable HDCP support - not available in Bottlerocket kernel
export CONFIG_DRM_AMD_DC_HDCP=n
subdir-ccflags-y += -DCONFIG_DRM_AMD_DC_HDCP=n
subdir-ccflags-y += -DCONFIG_DRM_HDCP=n
# Prevent linking against HDCP symbols
subdir-ccflags-y += -DDISABLE_HDCP_SUPPORT
DKMS_EOF

# Run configure to set up kernel detection
KERNELVER=6.12.53 amd/dkms/configure --with-linux=%{_cross_usrsrc}/kernels/6.12

popd

%build
pushd amdgpu

# Build using the DKMS Makefile with static configuration
make modules   KERNELVER=6.12.53   kernel_build_dir=%{_cross_usrsrc}/kernels/6.12   CC=%{_cross_target}-gcc   ARCH=%{_cross_karch}   CROSS_COMPILE=%{_cross_target}-   EXTRA_CFLAGS=-DPACKAGE_VERSION=\\\"%{version}\\\"

popd

%install
mkdir -p %{buildroot}%{_cross_libdir}/modules/%{_cross_kver}
install -p -m 644 amdgpu/amd/amdgpu/amdgpu.ko %{buildroot}%{_cross_libdir}/modules/%{_cross_kver}/

%files
%{_cross_licensedir}/kmod-6.12-amdgpu-7/attribution.txt
%{_cross_libdir}/modules/%{_cross_kver}/amdgpu.ko
