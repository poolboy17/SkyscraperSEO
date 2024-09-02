{pkgs}: {
  deps = [
    pkgs.openssh
    pkgs.php83Extensions.snmp
    pkgs.python311Packages.mkdocs
  ];
}
