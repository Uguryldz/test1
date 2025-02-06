{pkgs}: {
  deps = [
    pkgs.postgresql
    pkgs.unixODBC
    pkgs.glibcLocales
  ];
}
