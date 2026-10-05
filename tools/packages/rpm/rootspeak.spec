# RootSpeak - Advanced Messaging System for Linux
# The rpm package, one for the Fedora, RHEL and SUSE families: the files are
# already in the stage folder (tools/packages/make-package.sh), nothing is built here.
Name:           rootspeak
Version:        @VERSION@
Release:        @REL@
Summary:        @SUMMARY@
License:        LicenseRef-RootSpeak-Source-Available
URL:            https://rootspeak.nicfio.it/
ExclusiveArch:  x86_64
# the programs are already built and stripped by tools/release.sh
%global debug_package %{nil}
%global __brp_strip %{nil}
Requires:       systemd
Requires:       sudo
Requires:       /usr/bin/pkill
Recommends:     zenity
Suggests:       libnotify

%description
RootSpeak - Advanced Messaging System for Linux. The administrators of a Linux
machine send messages to its users, in every terminal and on the desktop, and
see for each user whether the message was delivered and confirmed.
Administrators use the rspeak command; users get the messages automatically.

%install
cp -a %{stage}/. %{buildroot}/

%post
/usr/lib/rootspeak/rootspeak-setup configure

%preun
# only when removing, not on upgrades
if [ $1 -eq 0 ]; then
	/usr/lib/rootspeak/rootspeak-setup unconfigure || :
fi

%files
# the group of rspeak is the administrators' one, set by rootspeak-setup
%attr(0750,root,root) /usr/bin/rspeak
/usr/lib/rootspeak
%dir /etc/rootspeak
%config(noreplace) /etc/rootspeak/rootspeak.conf
/etc/profile.d/rootspeak.sh
/etc/fish/conf.d/rootspeak.fish
/etc/xdg/autostart/rootspeak-agent.desktop
%doc /usr/share/doc/rootspeak
/usr/share/icons/hicolor/scalable/apps/rootspeak.svg
/usr/share/icons/hicolor/48x48/apps/rootspeak.png
/usr/share/icons/hicolor/128x128/apps/rootspeak.png
/usr/share/icons/hicolor/256x256/apps/rootspeak.png
/usr/share/metainfo/it.nicfio.rootspeak.metainfo.xml
