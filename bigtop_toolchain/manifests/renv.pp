# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

class bigtop_toolchain::renv {

  require bigtop_toolchain::packages

  case $operatingsystem{
    /(?i:(centos|fedora|redhat|amazon|rocky))/: {
      $pkgs = [
        "R",
        "R-devel",
        "pandoc"
      ]
    }
    /(?i:(SLES|opensuse))/: {
      $pkgs = [
        "R-base",
        "R-base-devel",
        "pandoc"
      ]
    }
    /(Ubuntu|Debian)/: {
      $pkgs = [
        "r-base",
        "r-base-dev",
        "pandoc",
      ]
    }
    default: {
      $pkgs = []
    }
  }

  package { $pkgs:
    ensure => installed,
    before => [Exec["install_r_packages"]]
  }

  #BIGTOP-3967: openEuler not support PowerPC currently.
  if ($operatingsystem == 'openEuler'){
    if ($architecture == "aarch64") {
        $pandocurl = "https://github.com/jgm/pandoc/releases/download/2.19.2/pandoc-2.19.2-linux-arm64.tar.gz"
        $pandoctar = "pandoc-2.19.2-linux-arm64.tar.gz"
    } else{
        $pandocurl = "https://github.com/jgm/pandoc/releases/download/2.19.2/pandoc-2.19.2-linux-amd64.tar.gz"
        $pandoctar = "pandoc-2.19.2-linux-amd64.tar.gz"
    }

    exec {"down_pandoc":
      cwd => "/usr/src",
      command => "/usr/bin/wget $pandocurl && /bin/tar -xvzf $pandoctar && ln -s /usr/src/pandoc-2.19.2/bin/pandoc /usr/bin/pandoc",
    }

    $rurl = "https://cran.r-project.org/src/base/R-4/"
    $rfile = "R-4.4.3.tar.gz"
    $rdir = "R-4.4.3"

    exec { "download_R":
      cwd  => "/usr/src",
      command => "/usr/bin/wget $rurl/$rfile && mkdir -p $rdir && /bin/tar -xvzf $rfile -C $rdir --strip-components=1 && cd $rdir",
      creates => "/usr/src/$rdir",
    }

    package { "cairo-devel":
      ensure => installed,
    }

    exec { "install_R":
      cwd => "/usr/src/$rdir",
      command => "/usr/src/$rdir/configure --with-recommended-packages=yes --without-x --with-cairo --with-libpng --with-libtiff --with-jpeglib --with-tcltk --with-blas --with-lapack --enable-R-shlib --prefix=/usr/local && /usr/bin/make && /usr/bin/make install && /sbin/ldconfig",
      creates => "/usr/local/bin/R",
      require => [Exec["download_R"], Package["cairo-devel"]],
      timeout => 3000
    }

    exec { "install_r_packages" :
      cwd     => "/usr/local/bin",
      command => '/usr/local/bin/R -e \'pkgs <- c("devtools", "evaluate", "rmarkdown", "knitr", "roxygen2", "testthat", "e1071"); install.packages(pkgs, repo="https://cran.r-project.org/"); for (pkg in pkgs[pkgs != "devtools"]) if (!library(pkg, character.only=TRUE, logical.return=TRUE)) q(save="no", status=1)\'',
      require => [Exec["install_R"]],
      timeout => 6000
    }
  } else {
    exec { "install_r_packages" :
      cwd     => "/usr/bin",
      command => '/usr/bin/R -e \'pkgs <- c("devtools", "evaluate", "rmarkdown", "knitr", "roxygen2", "testthat", "e1071"); install.packages(pkgs, repo="https://cran.r-project.org/"); for (pkg in pkgs[pkgs != "devtools"]) if (!library(pkg, character.only=TRUE, logical.return=TRUE)) q(save="no", status=1)\'',
      timeout => 6000
    }
  }
}
