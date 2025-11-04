Name: %{_cross_os}kmod-6.12-amdgpu-7
Version: 30.10.2
Release: 1%{?dist}
Summary: AMD GPU drivers for the 6.12 kernel
# We use these licences because we only ship our own software in the main package,
# each subpackage includes the LICENSE file provided by the Licenses.toml file
License: Apache-2.0 OR MIT  #TODO: Validate license
URL: https://www.amd.com/

Source0: https://repo.radeon.com/amdgpu/30.10.2/el/10/main/x86_64/amdgpu-dkms-6.14.14-2226257.el10.noarch.rpm
Patch001: 0001-add-bottlerocket-dkms-config.patch

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
%patch -P 1 -p1
# Run configure to set up kernel detection
KERNELVER=6.12.53 amd/dkms/configure --with-linux=%{_cross_usrsrc}/kernels/6.12

# Build using the DKMS Makefile with static configuration
make modules \
  KERNELVER=6.12.53 \
  kernel_build_dir=%{_cross_usrsrc}/kernels/6.12 \
  CC=%{_cross_target}-gcc \
  ARCH=%{_cross_karch} \
  CROSS_COMPILE=%{_cross_target}- \
  EXTRA_CFLAGS="-DPACKAGE_VERSION=\\\"%{version}\\\""
popd

%install

%files
