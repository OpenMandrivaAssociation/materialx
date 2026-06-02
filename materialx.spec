%define major 1
%define libname %mklibname materialx
%define devname %mklibname materialx -d
%define oname MaterialX
%bcond openimageio 1
%bcond python 1
# viewer depends on git access to grab submodule dependencies that are not
# included in the tarball, those dependencies have also not made releases in
# a long while
%bcond viewer 0
%bcond tests 1

Name:		materialx
Version:	1.39.5
Release:	1
Summary:	Open standard for the exchange of content across apps & renderers
License:	Apache-2.0
Group:		System/Libraries
URL:		https://materialx.org/
# repo - https://github.com/AcademySoftwareFoundation/MaterialX
Source0:	https://github.com/AcademySoftwareFoundation/MaterialX/releases/download/v%{version}/%{name}-%{version}.tar.gz
Source100:	%{name}.rpmlintrc
Patch0:	materialx-gnuinstalldirs.patch

BuildSystem:	cmake
BuildOption(prep):	-p1
BuildOption:	-DCMAKE_BUILD_TYPE=RelWithDebInfo
BuildOption:	-DCMAKE_INSTALL_PREFIX="%{_prefix}"
BuildOption:	-DCMAKE_INSTALL_LIBDIR="%{_libdir}"
BuildOption:	-DCMAKE_INSTALL_DOCDIR="%{_docdir}/%{name}"
BuildOption:	-DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON
BuildOption:	-DMATERIALX_BUILD_SHARED_LIBS:BOOL=ON
BuildOption:	-DMATERIALX_BUILD_TESTS:BOOL=ON
BuildOption:	-DMATERIALX_BUILD_OIIO:BOOL=ON
BuildOption:	-DMATERIALX_INSTALL_RESOURCES:BOOL=ON
%if %{with python}
BuildOption:	-DMATERIALX_PYTHON_EXECUTABLE="%{__python}"
BuildOption:	-DMATERIALX_PYTHON_VERSION="%{pyver}"
BuildOption:	-DMATERIALX_PYTHON_FOLDER_NAME=%{python_sitelib}/%{name}
BuildOption:	-DMATERIALX_BUILD_PYTHON:BOOL=ON
BuildOption:	-DPYBIND11_FINDPYTHON:BOOL=ON
%endif
%if %{with viewer}
BuildOption:	-DMATERIALX_BUILD_VIEWER:BOOL=ON
BuildOption:	-DMATERIALX_BUILD_GRAPH_EDITOR=ON
%endif

BuildRequires:	cmake
BuildRequires:	cmake(OSL)
BuildRequires:	doxygen
BuildRequires:	help2man
BuildRequires:	ninja
BuildRequires:	OpenImageIO-plugin-osl
BuildRequires:	openshadinglanguage
BuildRequires:	pkgconfig(catch2)
BuildRequires:	pkgconfig(gl)
BuildRequires:	pkgconfig(glfw3)
BuildRequires:	pkgconfig(oslcomp)
BuildRequires:	pkgconfig(wayland-client) >= 0.2.7
BuildRequires:	pkgconfig(wayland-protocols) >= 1.15
BuildRequires:	pkgconfig(xkbcommon)
BuildRequires:	pkgconfig(xrandr)
BuildRequires:	pkgconfig(xcursor)
BuildRequires:	pkgconfig(xi)
BuildRequires:	pkgconfig(xt)
%if %{with openimageio}
BuildRequires:	OpenImageIO
BuildRequires:	pkgconfig(OpenImageIO)
%endif
%if %{with python}
BuildRequires:	pkgconfig(python)
BuildRequires:	pkgconfig(pybind11)
BuildRequires:	python%{pyver}dist(setuptools)
BuildRequires:	python%{pyver}dist(scikit-build-core)
# Required for MaterialXTest
BuildRequires:	python%{pyver}dist(pillow)
%endif
%if %{with viewer}
BuildRequires:	desktop-file-utils
BuildRequires:	hicolor-icon-theme
%endif
Requires:	%{libname} = %{EVRD}
Requires:	%{name}-data = %{EVRD}

%description
MaterialX is an open standard for representing rich material and
look-development content in computer graphics, enabling its
platform-independent description and exchange across applications
and renderers.

%package -n %{libname}
Summary:	Core %{oname} libraries
Group:	System/Libraries

%description -n %{libname}
%{name} examples and resources.

%package -n %{devname}
Summary:	Development files for %{oname}
Group:	Development/C++
Requires:	%{libname} = %{EVRD}
Provides: %{name}-devel = %{EVRD}

%description -n %{devname}
Development files for building applications using %{oname}.

%package data
Summary:	%{oname} examples and resources
BuildArch:	noarch

%description data
%{name} examples and resources.

%if %{with python}
%package -n python-%{name}
Summary:	Python bindings for %{oname}
Requires:	%{name} = %{EVRD}

%description -n python-%{name}
Python bindings for %{oname}.
%endif

%if %{with viewer}
%package viewer
Summary:	%{oname} graphical viewer
Requires:	%{name} = %{EVRD}

%description viewer
Interactive viewer for %{oname} materials.
%endif

%prep -a
# Remove bundled assets
find . -type f \( -name '*.tt[cf]' -o -name '*.ot[cf]' -o -name '*.woff*' \) -delete
# Fix installation path for cmake configuration
sed -i "s|@PACKAGE_CMAKE_INSTALL_PREFIX@/libraries|%{_datadir}/%{name}/libraries/|" \
	cmake/modules/MaterialXConfig.cmake.in
sed -i "s|@PACKAGE_CMAKE_INSTALL_PREFIX@/python|%{python_sitelib}/%{name}/|" \
	cmake/modules/MaterialXConfig.cmake.in
sed -i "s|@PACKAGE_CMAKE_INSTALL_PREFIX@/resources|%{_datadir}/%{name}/resources/|" \
	cmake/modules/MaterialXConfig.cmake.in

# Fix shebangs
find ./python/ -type f -print0 | xargs -0 sed -i 's:^#!/usr/bin/env python:#!%{__python}:'
# Add missing shebang
sed -i '1 i\#!%{__python}' python/Scripts/oiio_loader.py

%install -a
%if %{with python}
install -dp %{buildroot}%{_bindir}
rm %{buildroot}%{_prefix}/python/Scripts/README.md
for file in %{buildroot}%{_prefix}/python/Scripts/*.py; do
	name="${file%.py}"
	chmod +x "$file"
	mv "$file" $name
done
chmod +x %{buildroot}%{_prefix}/python/MaterialX/*.py
mv %{buildroot}%{_prefix}/python/Scripts/* %{buildroot}%{_bindir}
mv %{buildroot}%{_prefix}/python/MaterialX/* %{buildroot}%{python3_sitelib}/%{name}
rm -rf %{buildroot}%{_prefix}/python
rm -rf %{buildroot}%{python_sitelib}/%{name}/%{_prefix}
%endif

# Install licenses
install -Dpm644 LICENSE -t %{buildroot}%{_licensedir}/%{name}/
install -Dpm644 source/MaterialXTest/External/Catch/LICENSE.txt \
	licensepack/BSL-license
install -Dpm644 source/MaterialXRenderGlsl/External/Glad/LICENSE \
	licensepack/MIT-Khronos-old-license
install -Dpm644 source/PyMaterialX/External/PyBind11/LICENSE \
	licensepack/BSD-license
install -Dpm644 source/MaterialXRender/External/Cgltf/LICENSE \
	licensepack/MIT-license

%if %{with viewer}
# Desktop integration
install -Dpm644 documents/Images/MaterialXLogo_200x155.png \
	%{buildroot}%{_datadir}/icons/hicolor/256x256/apps/%{name}.png
# Generate desktop files
for app in viewer graph-editor; do
	desktop-file-install --dir=%{buildroot}%{_datadir}/applications \
	--add-category Graphics \
	--add-category 3DGraphics \
	--set-key Name --set-value "MaterialX ${app%-*}" \
	--set-key Exec --set-value "MaterialX${app//-}" \
	--set-key Icon --set-value "%{name}" \
	--set-key Comment --set-value "MaterialX ${app%-*}" \
	%{name}-${app}.desktop
done
%endif

# Generate and install man pages.
install -d '%{buildroot}%{_mandir}/man1'
for cmd in %{buildroot}%{_bindir}/*
do
	LD_LIBRARY_PATH='%{buildroot}%{_libdir}' \
	help2man \
	--no-info --no-discard-stderr --version-string='%{version}' \
	--output="%{buildroot}%{_mandir}/man1/$(basename "${cmd}").1" \
	"${cmd}"
done

%if %{with tests}
%check
export PYTHONPATH="%{buildroot}%{python_sitelib}"
export LD_LIBRARY_PATH="%{buildroot}%{_libdir}"
# Exclude tests that require a display (GLSL) or have OSL rendering issues
# in mock environment
ctest -V -E "Render_GLSL_TestSuite|GenReference_OSL_Reference|Render_OSL_TestSuite|GenShader_MDL_Shader_Generation|Render_Half_Float" \
	--test-dir=_OMV_rpm_build
%endif

%files
%doc README.md CHANGELOG.md THIRD-PARTY.md
%license LICENSE licensepack/*
%dir %{_datadir}/%{name}
%if %{with openimageio}
%{_bindir}/baketextures
%{_bindir}/comparenodedefs
%{_bindir}/creatematerial
%{_bindir}/generateshader
%{_bindir}/genmdl
%{_bindir}/mx{doc,format,validate}
%{_bindir}/oiio_loader
%{_bindir}/pybind_docs
%{_bindir}/translateshader
%{_bindir}/writenodegraphs
%{_mandir}/man1/baketextures.1*
%{_mandir}/man1/comparenodedefs.1*
%{_mandir}/man1/creatematerial.1*
%{_mandir}/man1/generateshader.1*
%{_mandir}/man1/genmdl.1*
%{_mandir}/man1/mx{doc,format,validate}.1*
%{_mandir}/man1/oiio_loader.1*
%{_mandir}/man1/pybind_docs.1*
%{_mandir}/man1/translateshader.1*
%{_mandir}/man1/writenodegraphs.1*
%endif

%files -n %{libname}
%{_libdir}/lib%{oname}*.so.{%{major},%{version}}

%files -n %{devname}
%{_includedir}/%{oname}*
%{_libdir}/lib%{oname}*.so
%{_libdir}/cmake/%{oname}

%files data
%{_datadir}/%{name}/

%if %{with python}
%files -n python-%{name}
%{python_sitelib}/%{name}
%endif

%if %{with viewer}
%files viewer
%{_bindir}/%{oname}{View,GraphEditor}
%{_datadir}/icons/hicolor/*/apps/%{name}.png
%{_datadir}/applications/%{name}-{graph-editor,viewer}.desktop
%endif
