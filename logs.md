root@gzpeite:/opt/rk3568/deploy# sudo ./deploy.sh
sudo: 无法解析主机：gzpeite: 未知的名称或服务
================================================
  RK3568 智能视觉识别系统 - 一键部署
================================================
项目目录: /opt/rk3568
虚拟环境: /opt/rk3568/.venv
================================================

==== 第 1 步: 配置国内镜像源 ====
[INFO] 系统版本: Ubuntu 22.04 (jammy)
[INFO] 系统架构: arm64, 使用镜像路径: ubuntu-ports
[INFO] 配置阿里云 apt 镜像源...
[INFO] 阿里云镜像源配置完成

==== 第 2 步: 更新系统并安装基础依赖 ====
[INFO] 更新 apt...
获取:1 http://mirrors.aliyun.com/ubuntu-ports jammy InRelease [270 kB]
获取:2 http://mirrors.aliyun.com/ubuntu-ports jammy-security InRelease [129 kB]
获取:3 http://mirrors.aliyun.com/ubuntu-ports jammy-updates InRelease [128 kB]
获取:4 http://mirrors.aliyun.com/ubuntu-ports jammy-backports InRelease [127 kB]
获取:5 http://mirrors.aliyun.com/ubuntu-ports jammy/main arm64 Packages [1,369 kB]
获取:6 http://mirrors.aliyun.com/ubuntu-ports jammy/main Translation-zh_CN [114 kB]
获取:7 http://mirrors.aliyun.com/ubuntu-ports jammy/main Translation-en [510 kB]
获取:8 http://mirrors.aliyun.com/ubuntu-ports jammy/main arm64 DEP-11 Metadata [423 kB]
获取:9 http://mirrors.aliyun.com/ubuntu-ports jammy/main DEP-11 48x48 Icons [100.0 kB]
获取:10 http://mirrors.aliyun.com/ubuntu-ports jammy/main DEP-11 64x64 Icons [148 kB]
获取:11 http://mirrors.aliyun.com/ubuntu-ports jammy/main DEP-11 64x64@2 Icons [15.8 kB]
获取:12 http://mirrors.aliyun.com/ubuntu-ports jammy/restricted arm64 Packages [19.6 kB]
获取:13 http://mirrors.aliyun.com/ubuntu-ports jammy/restricted Translation-en [18.6 kB]
获取:14 http://mirrors.aliyun.com/ubuntu-ports jammy/restricted Translation-zh_CN [748 B]
获取:15 http://mirrors.aliyun.com/ubuntu-ports jammy/universe arm64 Packages [13.9 MB]
获取:16 http://mirrors.aliyun.com/ubuntu-ports jammy/universe Translation-zh_CN [454 kB]
获取:17 http://mirrors.aliyun.com/ubuntu-ports jammy/universe Translation-en [5,652 kB]
获取:18 http://mirrors.aliyun.com/ubuntu-ports jammy/universe arm64 DEP-11 Metadata [3,360 kB]
获取:19 http://mirrors.aliyun.com/ubuntu-ports jammy/universe DEP-11 48x48 Icons [3,447 kB]
获取:20 http://mirrors.aliyun.com/ubuntu-ports jammy/universe DEP-11 64x64 Icons [7,609 kB]
获取:21 http://mirrors.aliyun.com/ubuntu-ports jammy/universe DEP-11 64x64@2 Icons [69.3 kB]
获取:22 http://mirrors.aliyun.com/ubuntu-ports jammy/multiverse arm64 Packages [184 kB]
获取:23 http://mirrors.aliyun.com/ubuntu-ports jammy/multiverse Translation-en [112 kB]
获取:24 http://mirrors.aliyun.com/ubuntu-ports jammy/multiverse Translation-zh_CN [4,440 B]
获取:25 http://mirrors.aliyun.com/ubuntu-ports jammy/multiverse arm64 DEP-11 Metadata [38.8 kB]
获取:26 http://mirrors.aliyun.com/ubuntu-ports jammy/multiverse DEP-11 48x48 Icons [42.7 kB]
获取:27 http://mirrors.aliyun.com/ubuntu-ports jammy/multiverse DEP-11 64x64 Icons [193 kB]
获取:28 http://mirrors.aliyun.com/ubuntu-ports jammy/multiverse DEP-11 64x64@2 Icons [214 B]
获取:29 http://mirrors.aliyun.com/ubuntu-ports jammy-security/main arm64 Packages [3,083 kB]
获取:30 http://mirrors.aliyun.com/ubuntu-ports jammy-security/main Translation-en [453 kB]
获取:31 http://mirrors.aliyun.com/ubuntu-ports jammy-security/main arm64 DEP-11 Metadata [54.5 kB]
获取:32 http://mirrors.aliyun.com/ubuntu-ports jammy-security/main DEP-11 48x48 Icons [20.3 kB]
获取:33 http://mirrors.aliyun.com/ubuntu-ports jammy-security/main DEP-11 64x64 Icons [31.6 kB]
获取:34 http://mirrors.aliyun.com/ubuntu-ports jammy-security/main DEP-11 64x64@2 Icons [29 B]
获取:35 http://mirrors.aliyun.com/ubuntu-ports jammy-security/restricted arm64 Packages [5,774 kB]
获取:36 http://mirrors.aliyun.com/ubuntu-ports jammy-security/restricted Translation-en [1,090 kB]
获取:37 http://mirrors.aliyun.com/ubuntu-ports jammy-security/restricted arm64 DEP-11 Metadata [208 B]
获取:38 http://mirrors.aliyun.com/ubuntu-ports jammy-security/restricted DEP-11 48x48 Icons [29 B]
获取:39 http://mirrors.aliyun.com/ubuntu-ports jammy-security/restricted DEP-11 64x64 Icons [29 B]
获取:40 http://mirrors.aliyun.com/ubuntu-ports jammy-security/restricted DEP-11 64x64@2 Icons [29 B]
获取:41 http://mirrors.aliyun.com/ubuntu-ports jammy-security/universe arm64 Packages [1,087 kB]
获取:42 http://mirrors.aliyun.com/ubuntu-ports jammy-security/universe Translation-en [227 kB]
获取:43 http://mirrors.aliyun.com/ubuntu-ports jammy-security/universe arm64 DEP-11 Metadata [125 kB]
获取:44 http://mirrors.aliyun.com/ubuntu-ports jammy-security/universe DEP-11 48x48 Icons [82.0 kB]
获取:45 http://mirrors.aliyun.com/ubuntu-ports jammy-security/universe DEP-11 64x64 Icons [122 kB]
获取:46 http://mirrors.aliyun.com/ubuntu-ports jammy-security/universe DEP-11 64x64@2 Icons [29 B]
获取:47 http://mirrors.aliyun.com/ubuntu-ports jammy-security/multiverse arm64 Packages [34.6 kB]
获取:48 http://mirrors.aliyun.com/ubuntu-ports jammy-security/multiverse Translation-en [10.5 kB]
获取:49 http://mirrors.aliyun.com/ubuntu-ports jammy-security/multiverse arm64 DEP-11 Metadata [208 B]
获取:50 http://mirrors.aliyun.com/ubuntu-ports jammy-security/multiverse DEP-11 48x48 Icons [29 B]
获取:51 http://mirrors.aliyun.com/ubuntu-ports jammy-security/multiverse DEP-11 64x64 Icons [29 B]
获取:52 http://mirrors.aliyun.com/ubuntu-ports jammy-security/multiverse DEP-11 64x64@2 Icons [29 B]
获取:53 http://mirrors.aliyun.com/ubuntu-ports jammy-updates/main arm64 Packages [3,366 kB]
获取:54 http://mirrors.aliyun.com/ubuntu-ports jammy-updates/main Translation-en [527 kB]
获取:55 http://mirrors.aliyun.com/ubuntu-ports jammy-updates/main arm64 DEP-11 Metadata [114 kB]
获取:56 http://mirrors.aliyun.com/ubuntu-ports jammy-updates/main DEP-11 48x48 Icons [37.0 kB]
获取:57 http://mirrors.aliyun.com/ubuntu-ports jammy-updates/main DEP-11 64x64 Icons [56.3 kB]
获取:58 http://mirrors.aliyun.com/ubuntu-ports jammy-updates/main DEP-11 64x64@2 Icons [29 B]
获取:59 http://mirrors.aliyun.com/ubuntu-ports jammy-updates/restricted arm64 Packages [6,068 kB]
获取:60 http://mirrors.aliyun.com/ubuntu-ports jammy-updates/restricted Translation-en [1,139 kB]
获取:61 http://mirrors.aliyun.com/ubuntu-ports jammy-updates/restricted arm64 DEP-11 Metadata [212 B]
获取:62 http://mirrors.aliyun.com/ubuntu-ports jammy-updates/restricted DEP-11 48x48 Icons [29 B]
获取:63 http://mirrors.aliyun.com/ubuntu-ports jammy-updates/restricted DEP-11 64x64 Icons [29 B]
获取:64 http://mirrors.aliyun.com/ubuntu-ports jammy-updates/restricted DEP-11 64x64@2 Icons [29 B]
获取:65 http://mirrors.aliyun.com/ubuntu-ports jammy-updates/universe arm64 Packages [1,322 kB]
获取:66 http://mirrors.aliyun.com/ubuntu-ports jammy-updates/universe Translation-en [316 kB]
获取:67 http://mirrors.aliyun.com/ubuntu-ports jammy-updates/universe arm64 DEP-11 Metadata [356 kB]
获取:68 http://mirrors.aliyun.com/ubuntu-ports jammy-updates/universe DEP-11 48x48 Icons [253 kB]
获取:69 http://mirrors.aliyun.com/ubuntu-ports jammy-updates/universe DEP-11 64x64 Icons [410 kB]
获取:70 http://mirrors.aliyun.com/ubuntu-ports jammy-updates/universe DEP-11 64x64@2 Icons [29 B]
获取:71 http://mirrors.aliyun.com/ubuntu-ports jammy-updates/multiverse arm64 Packages [52.0 kB]
获取:72 http://mirrors.aliyun.com/ubuntu-ports jammy-updates/multiverse Translation-en [15.5 kB]
获取:73 http://mirrors.aliyun.com/ubuntu-ports jammy-updates/multiverse arm64 DEP-11 Metadata [212 B]
获取:74 http://mirrors.aliyun.com/ubuntu-ports jammy-updates/multiverse DEP-11 48x48 Icons [1,867 B]
获取:75 http://mirrors.aliyun.com/ubuntu-ports jammy-updates/multiverse DEP-11 64x64 Icons [2,497 B]
获取:76 http://mirrors.aliyun.com/ubuntu-ports jammy-updates/multiverse DEP-11 64x64@2 Icons [29 B]
获取:77 http://mirrors.aliyun.com/ubuntu-ports jammy-backports/main arm64 Packages [69.8 kB]
获取:78 http://mirrors.aliyun.com/ubuntu-ports jammy-backports/main Translation-en [11.4 kB]
获取:79 http://mirrors.aliyun.com/ubuntu-ports jammy-backports/main arm64 DEP-11 Metadata [3,568 B]
获取:80 http://mirrors.aliyun.com/ubuntu-ports jammy-backports/main DEP-11 48x48 Icons [9,535 B]
获取:81 http://mirrors.aliyun.com/ubuntu-ports jammy-backports/main DEP-11 64x64 Icons [11.3 kB]
获取:82 http://mirrors.aliyun.com/ubuntu-ports jammy-backports/main DEP-11 64x64@2 Icons [29 B]
获取:83 http://mirrors.aliyun.com/ubuntu-ports jammy-backports/restricted arm64 DEP-11 Metadata [212 B]
获取:84 http://mirrors.aliyun.com/ubuntu-ports jammy-backports/restricted DEP-11 48x48 Icons [29 B]
获取:85 http://mirrors.aliyun.com/ubuntu-ports jammy-backports/restricted DEP-11 64x64 Icons [29 B]
获取:86 http://mirrors.aliyun.com/ubuntu-ports jammy-backports/restricted DEP-11 64x64@2 Icons [29 B]
获取:87 http://mirrors.aliyun.com/ubuntu-ports jammy-backports/universe arm64 Packages [29.2 kB]
获取:88 http://mirrors.aliyun.com/ubuntu-ports jammy-backports/universe Translation-en [16.9 kB]
获取:89 http://mirrors.aliyun.com/ubuntu-ports jammy-backports/universe arm64 DEP-11 Metadata [12.0 kB]
获取:90 http://mirrors.aliyun.com/ubuntu-ports jammy-backports/universe DEP-11 48x48 Icons [19.7 kB]
获取:91 http://mirrors.aliyun.com/ubuntu-ports jammy-backports/universe DEP-11 64x64 Icons [28.2 kB]
获取:92 http://mirrors.aliyun.com/ubuntu-ports jammy-backports/universe DEP-11 64x64@2 Icons [29 B]
获取:93 http://mirrors.aliyun.com/ubuntu-ports jammy-backports/multiverse arm64 DEP-11 Metadata [212 B]
获取:94 http://mirrors.aliyun.com/ubuntu-ports jammy-backports/multiverse DEP-11 48x48 Icons [29 B]
获取:95 http://mirrors.aliyun.com/ubuntu-ports jammy-backports/multiverse DEP-11 64x64 Icons [29 B]
获取:96 http://mirrors.aliyun.com/ubuntu-ports jammy-backports/multiverse DEP-11 64x64@2 Icons [29 B]
已下载 64.9 MB，耗时 23秒 (2,767 kB/s)
正在读取软件包列表... 完成
[INFO] 安装基础依赖...
正在读取软件包列表... 完成
正在分析软件包的依赖关系树... 完成
正在读取状态信息... 完成
libsm6 已经是最新版 (2:1.2.3-1build2)。
libsm6 已设置为手动安装。
libxext6 已经是最新版 (2:1.3.4-1build1)。
libxext6 已设置为手动安装。
libxrender-dev 已经是最新版 (1:0.9.10-1build4)。
lsb-release 已经是最新版 (11.1.0ubuntu4)。
lsb-release 已设置为手动安装。
libopencv-dev 已经是最新版 (4.5.4+dfsg-9ubuntu4)。
将会同时安装下列软件：
  gcc-12-base gnome-shell gnome-shell-common javascript-common libatomic1 libavdevice58 libcc1-0 libcurl4 libcurl4-openssl-dev libgcc-s1
  libgfortran5 libglib2.0-bin libglib2.0-dev libglib2.0-dev-bin libhwasan0 libitm1 libjs-jquery libjs-sphinxdoc libjs-underscore liblsan0
  libobjc4 libpython3-dev libpython3-stdlib libpython3.10 libpython3.10-dev libpython3.10-minimal libpython3.10-stdlib libstdc++6 libubsan1
  python3-dev python3-minimal python3-pip-whl python3-pkg-resources python3-setuptools python3-setuptools-whl python3-wheel python3.10
  python3.10-dev python3.10-minimal python3.10-venv
建议安装：
  ffmpeg-doc gir1.2-malcontent-0 gir1.2-telepathyglib-0.12 gir1.2-telepathylogger-0.2 gnome-backgrounds gnome-shell-extension-prefs
  chrome-gnome-shell apache2 | lighttpd | httpd libcurl4-doc libidn11-dev libkrb5-dev libldap2-dev librtmp-dev libssh2-1-dev libssl-dev
  libgirepository1.0-dev libglib2.0-doc python3-doc python3-tk python-setuptools-doc python3.10-doc
下列【新】软件包将被安装：
  curl ffmpeg javascript-common libavdevice58 libgl1-mesa-glx libjs-jquery libjs-sphinxdoc libjs-underscore libpython3-dev libpython3.10-dev
  python3-dev python3-pip python3-pip-whl python3-setuptools python3-setuptools-whl python3-venv python3-wheel python3.10-dev python3.10-venv
下列软件包将被升级：
  gcc-12-base gnome-shell gnome-shell-common libatomic1 libcc1-0 libcurl4 libcurl4-openssl-dev libgcc-s1 libgfortran5 libglib2.0-0 libglib2.0-bin
  libglib2.0-dev libglib2.0-dev-bin libgomp1 libhwasan0 libitm1 liblsan0 libobjc4 libpython3-stdlib libpython3.10 libpython3.10-minimal
  libpython3.10-stdlib libstdc++6 libubsan1 net-tools python3 python3-minimal python3-pkg-resources python3.10 python3.10-minimal wget
升级了 31 个软件包，新安装了 19 个软件包， 要卸载 0 个软件包，有 553 个软件包未被升级。
需要下载 29.8 MB 的归档。
解压缩后会消耗 36.2 MB 的额外空间。
获取:1 http://mirrors.aliyun.com/ubuntu-ports jammy-updates/main arm64 python3-minimal arm64 3.10.6-1~22.04.1 [24.3 kB]
获取:2 http://mirrors.aliyun.com/ubuntu-ports jammy-updates/main arm64 python3 arm64 3.10.6-1~22.04.1 [22.8 kB]
获取:3 http://mirrors.aliyun.com/ubuntu-ports jammy-security/main arm64 libpython3.10 arm64 3.10.12-1~22.04.15 [1,890 kB]
获取:4 http://mirrors.aliyun.com/ubuntu-ports jammy-security/main arm64 python3.10 arm64 3.10.12-1~22.04.15 [508 kB]
获取:5 http://mirrors.aliyun.com/ubuntu-ports jammy-security/main arm64 libpython3.10-stdlib arm64 3.10.12-1~22.04.15 [1,847 kB]
获取:6 http://mirrors.aliyun.com/ubuntu-ports jammy-security/main arm64 python3.10-minimal arm64 3.10.12-1~22.04.15 [2,246 kB]
获取:7 http://mirrors.aliyun.com/ubuntu-ports jammy-security/main arm64 libpython3.10-minimal arm64 3.10.12-1~22.04.15 [814 kB]
获取:8 http://mirrors.aliyun.com/ubuntu-ports jammy-updates/main arm64 libpython3-stdlib arm64 3.10.6-1~22.04.1 [6,812 B]
获取:9 http://mirrors.aliyun.com/ubuntu-ports jammy-security/main arm64 libatomic1 arm64 12.3.0-1ubuntu1~22.04.3 [10.7 kB]
获取:10 http://mirrors.aliyun.com/ubuntu-ports jammy-security/main arm64 libubsan1 arm64 12.3.0-1ubuntu1~22.04.3 [967 kB]
获取:11 http://mirrors.aliyun.com/ubuntu-ports jammy-security/main arm64 gcc-12-base arm64 12.3.0-1ubuntu1~22.04.3 [216 kB]
获取:12 http://mirrors.aliyun.com/ubuntu-ports jammy-security/main arm64 libstdc++6 arm64 12.3.0-1ubuntu1~22.04.3 [661 kB]
获取:13 http://mirrors.aliyun.com/ubuntu-ports jammy-security/universe arm64 libobjc4 arm64 12.3.0-1ubuntu1~22.04.3 [46.1 kB]
获取:14 http://mirrors.aliyun.com/ubuntu-ports jammy-security/main arm64 liblsan0 arm64 12.3.0-1ubuntu1~22.04.3 [1,038 kB]
获取:15 http://mirrors.aliyun.com/ubuntu-ports jammy-security/main arm64 libitm1 arm64 12.3.0-1ubuntu1~22.04.3 [28.5 kB]
获取:16 http://mirrors.aliyun.com/ubuntu-ports jammy-security/main arm64 libhwasan0 arm64 12.3.0-1ubuntu1~22.04.3 [1,120 kB]
获取:17 http://mirrors.aliyun.com/ubuntu-ports jammy-security/main arm64 libgomp1 arm64 12.3.0-1ubuntu1~22.04.3 [124 kB]
获取:18 http://mirrors.aliyun.com/ubuntu-ports jammy-security/main arm64 libgfortran5 arm64 12.3.0-1ubuntu1~22.04.3 [417 kB]
获取:19 http://mirrors.aliyun.com/ubuntu-ports jammy-security/main arm64 libcc1-0 arm64 12.3.0-1ubuntu1~22.04.3 [45.0 kB]
获取:20 http://mirrors.aliyun.com/ubuntu-ports jammy-security/main arm64 libgcc-s1 arm64 12.3.0-1ubuntu1~22.04.3 [39.7 kB]
获取:21 http://mirrors.aliyun.com/ubuntu-ports jammy-updates/main arm64 gnome-shell arm64 42.9-0ubuntu2.3 [862 kB]
获取:22 http://mirrors.aliyun.com/ubuntu-ports jammy-updates/main arm64 gnome-shell-common all 42.9-0ubuntu2.3 [183 kB]
获取:23 http://mirrors.aliyun.com/ubuntu-ports jammy-security/main arm64 libglib2.0-dev arm64 2.72.4-0ubuntu2.9 [1,828 kB]
获取:24 http://mirrors.aliyun.com/ubuntu-ports jammy-security/main arm64 libglib2.0-dev-bin arm64 2.72.4-0ubuntu2.9 [116 kB]
获取:25 http://mirrors.aliyun.com/ubuntu-ports jammy-security/main arm64 libglib2.0-bin arm64 2.72.4-0ubuntu2.9 [79.7 kB]
获取:26 http://mirrors.aliyun.com/ubuntu-ports jammy-security/main arm64 libglib2.0-0 arm64 2.72.4-0ubuntu2.9 [1,435 kB]
获取:27 http://mirrors.aliyun.com/ubuntu-ports jammy-security/main arm64 python3-pkg-resources all 59.6.0-1.2ubuntu0.22.04.3 [133 kB]
获取:28 http://mirrors.aliyun.com/ubuntu-ports jammy-security/main arm64 wget arm64 1.21.2-2ubuntu1.1 [334 kB]
获取:29 http://mirrors.aliyun.com/ubuntu-ports jammy-security/main arm64 libcurl4-openssl-dev arm64 7.81.0-1ubuntu1.24 [393 kB]
获取:30 http://mirrors.aliyun.com/ubuntu-ports jammy-security/main arm64 libcurl4 arm64 7.81.0-1ubuntu1.24 [285 kB]
获取:31 http://mirrors.aliyun.com/ubuntu-ports jammy-security/main arm64 curl arm64 7.81.0-1ubuntu1.24 [190 kB]
获取:32 http://mirrors.aliyun.com/ubuntu-ports jammy-security/universe arm64 libavdevice58 arm64 7:4.4.2-0ubuntu0.22.04.1 [85.2 kB]
获取:33 http://mirrors.aliyun.com/ubuntu-ports jammy-security/universe arm64 ffmpeg arm64 7:4.4.2-0ubuntu0.22.04.1 [1,693 kB]
获取:34 http://mirrors.aliyun.com/ubuntu-ports jammy/main arm64 javascript-common all 11+nmu1 [5,936 B]
获取:35 http://mirrors.aliyun.com/ubuntu-ports jammy-updates/universe arm64 libgl1-mesa-glx arm64 23.0.4-0ubuntu1~22.04.1 [5,584 B]
获取:36 http://mirrors.aliyun.com/ubuntu-ports jammy/main arm64 libjs-jquery all 3.6.0+dfsg+~3.5.13-1 [321 kB]
获取:37 http://mirrors.aliyun.com/ubuntu-ports jammy/main arm64 libjs-underscore all 1.13.2~dfsg-2 [118 kB]
获取:38 http://mirrors.aliyun.com/ubuntu-ports jammy/main arm64 libjs-sphinxdoc all 4.3.2-1 [139 kB]
获取:39 http://mirrors.aliyun.com/ubuntu-ports jammy-security/main arm64 libpython3.10-dev arm64 3.10.12-1~22.04.15 [4,666 kB]
获取:40 http://mirrors.aliyun.com/ubuntu-ports jammy-updates/main arm64 libpython3-dev arm64 3.10.6-1~22.04.1 [7,064 B]
获取:41 http://mirrors.aliyun.com/ubuntu-ports jammy-security/main arm64 net-tools arm64 1.60+git20181103.0eebece-1ubuntu5.4 [208 kB]
获取:42 http://mirrors.aliyun.com/ubuntu-ports jammy-security/main arm64 python3.10-dev arm64 3.10.12-1~22.04.15 [508 kB]
获取:43 http://mirrors.aliyun.com/ubuntu-ports jammy-updates/main arm64 python3-dev arm64 3.10.6-1~22.04.1 [26.0 kB]
获取:44 http://mirrors.aliyun.com/ubuntu-ports jammy-security/main arm64 python3-setuptools all 59.6.0-1.2ubuntu0.22.04.3 [340 kB]
获取:45 http://mirrors.aliyun.com/ubuntu-ports jammy-security/universe arm64 python3-wheel all 0.37.1-2ubuntu0.22.04.1 [32.0 kB]
获取:46 http://mirrors.aliyun.com/ubuntu-ports jammy-security/universe arm64 python3-pip all 22.0.2+dfsg-1ubuntu0.7 [1,306 kB]
获取:47 http://mirrors.aliyun.com/ubuntu-ports jammy-security/universe arm64 python3-pip-whl all 22.0.2+dfsg-1ubuntu0.7 [1,683 kB]
获取:48 http://mirrors.aliyun.com/ubuntu-ports jammy-security/universe arm64 python3-setuptools-whl all 59.6.0-1.2ubuntu0.22.04.3 [789 kB]
获取:49 http://mirrors.aliyun.com/ubuntu-ports jammy-security/universe arm64 python3.10-venv arm64 3.10.12-1~22.04.15 [5,714 B]
获取:50 http://mirrors.aliyun.com/ubuntu-ports jammy-updates/universe arm64 python3-venv arm64 3.10.6-1~22.04.1 [1,042 B]
已下载 29.8 MB，耗时 10秒 (2,942 kB/s)
debconf: 无法初始化前端界面：Dialog
debconf: (没有安装任何可用的对话框类程序，所以无法使用基于此种形式的界面。 at /usr/share/perl5/Debconf/FrontEnd/Dialog.pm line 78, <> line 50.)
debconf: 返回前端界面：Readline
正在从软件包中解出模板：100%
(正在读取数据库 ... 系统当前共安装有 140570 个文件和目录。)
准备解压 .../python3-minimal_3.10.6-1~22.04.1_arm64.deb  ...
正在解压 python3-minimal (3.10.6-1~22.04.1) 并覆盖 (3.10.6-1~22.04) ...
正在设置 python3-minimal (3.10.6-1~22.04.1) ...
(正在读取数据库 ... 系统当前共安装有 140570 个文件和目录。)
准备解压 .../0-python3_3.10.6-1~22.04.1_arm64.deb  ...
running python pre-rtupdate hooks for python3.10...
正在解压 python3 (3.10.6-1~22.04.1) 并覆盖 (3.10.6-1~22.04) ...
准备解压 .../1-libpython3.10_3.10.12-1~22.04.15_arm64.deb  ...
正在解压 libpython3.10:arm64 (3.10.12-1~22.04.15) 并覆盖 (3.10.6-1~22.04.2ubuntu1.1) ...
准备解压 .../2-python3.10_3.10.12-1~22.04.15_arm64.deb  ...
正在解压 python3.10 (3.10.12-1~22.04.15) 并覆盖 (3.10.6-1~22.04.2ubuntu1.1) ...
准备解压 .../3-libpython3.10-stdlib_3.10.12-1~22.04.15_arm64.deb  ...
正在解压 libpython3.10-stdlib:arm64 (3.10.12-1~22.04.15) 并覆盖 (3.10.6-1~22.04.2ubuntu1.1) ...
准备解压 .../4-python3.10-minimal_3.10.12-1~22.04.15_arm64.deb  ...
正在解压 python3.10-minimal (3.10.12-1~22.04.15) 并覆盖 (3.10.6-1~22.04.2ubuntu1.1) ...
准备解压 .../5-libpython3.10-minimal_3.10.12-1~22.04.15_arm64.deb  ...
正在解压 libpython3.10-minimal:arm64 (3.10.12-1~22.04.15) 并覆盖 (3.10.6-1~22.04.2ubuntu1.1) ...
准备解压 .../6-libpython3-stdlib_3.10.6-1~22.04.1_arm64.deb  ...
正在解压 libpython3-stdlib:arm64 (3.10.6-1~22.04.1) 并覆盖 (3.10.6-1~22.04) ...
准备解压 .../7-libatomic1_12.3.0-1ubuntu1~22.04.3_arm64.deb  ...
正在解压 libatomic1:arm64 (12.3.0-1ubuntu1~22.04.3) 并覆盖 (12.1.0-2ubuntu1~22.04) ...
准备解压 .../8-libubsan1_12.3.0-1ubuntu1~22.04.3_arm64.deb  ...
正在解压 libubsan1:arm64 (12.3.0-1ubuntu1~22.04.3) 并覆盖 (12.1.0-2ubuntu1~22.04) ...
准备解压 .../9-gcc-12-base_12.3.0-1ubuntu1~22.04.3_arm64.deb  ...
正在解压 gcc-12-base:arm64 (12.3.0-1ubuntu1~22.04.3) 并覆盖 (12.1.0-2ubuntu1~22.04) ...
正在设置 gcc-12-base:arm64 (12.3.0-1ubuntu1~22.04.3) ...
(正在读取数据库 ... 系统当前共安装有 140572 个文件和目录。)
准备解压 .../libstdc++6_12.3.0-1ubuntu1~22.04.3_arm64.deb  ...
正在解压 libstdc++6:arm64 (12.3.0-1ubuntu1~22.04.3) 并覆盖 (12.1.0-2ubuntu1~22.04) ...
正在设置 libstdc++6:arm64 (12.3.0-1ubuntu1~22.04.3) ...
(正在读取数据库 ... 系统当前共安装有 140572 个文件和目录。)
准备解压 .../0-libobjc4_12.3.0-1ubuntu1~22.04.3_arm64.deb  ...
正在解压 libobjc4:arm64 (12.3.0-1ubuntu1~22.04.3) 并覆盖 (12.1.0-2ubuntu1~22.04) ...
准备解压 .../1-liblsan0_12.3.0-1ubuntu1~22.04.3_arm64.deb  ...
正在解压 liblsan0:arm64 (12.3.0-1ubuntu1~22.04.3) 并覆盖 (12.1.0-2ubuntu1~22.04) ...
准备解压 .../2-libitm1_12.3.0-1ubuntu1~22.04.3_arm64.deb  ...
正在解压 libitm1:arm64 (12.3.0-1ubuntu1~22.04.3) 并覆盖 (12.1.0-2ubuntu1~22.04) ...
准备解压 .../3-libhwasan0_12.3.0-1ubuntu1~22.04.3_arm64.deb  ...
正在解压 libhwasan0:arm64 (12.3.0-1ubuntu1~22.04.3) 并覆盖 (12.1.0-2ubuntu1~22.04) ...
准备解压 .../4-libgomp1_12.3.0-1ubuntu1~22.04.3_arm64.deb  ...
正在解压 libgomp1:arm64 (12.3.0-1ubuntu1~22.04.3) 并覆盖 (12.1.0-2ubuntu1~22.04) ...
准备解压 .../5-libgfortran5_12.3.0-1ubuntu1~22.04.3_arm64.deb  ...
正在解压 libgfortran5:arm64 (12.3.0-1ubuntu1~22.04.3) 并覆盖 (12.1.0-2ubuntu1~22.04) ...
准备解压 .../6-libcc1-0_12.3.0-1ubuntu1~22.04.3_arm64.deb  ...
正在解压 libcc1-0:arm64 (12.3.0-1ubuntu1~22.04.3) 并覆盖 (12.1.0-2ubuntu1~22.04) ...
准备解压 .../7-libgcc-s1_12.3.0-1ubuntu1~22.04.3_arm64.deb  ...
正在解压 libgcc-s1:arm64 (12.3.0-1ubuntu1~22.04.3) 并覆盖 (12.1.0-2ubuntu1~22.04) ...
正在设置 libgcc-s1:arm64 (12.3.0-1ubuntu1~22.04.3) ...
(正在读取数据库 ... 系统当前共安装有 140572 个文件和目录。)
准备解压 .../00-gnome-shell_42.9-0ubuntu2.3_arm64.deb  ...
正在解压 gnome-shell (42.9-0ubuntu2.3) 并覆盖 (42.9-0ubuntu2) ...
准备解压 .../01-gnome-shell-common_42.9-0ubuntu2.3_all.deb  ...
正在解压 gnome-shell-common (42.9-0ubuntu2.3) 并覆盖 (42.9-0ubuntu2) ...
准备解压 .../02-libglib2.0-dev_2.72.4-0ubuntu2.9_arm64.deb  ...
正在解压 libglib2.0-dev:arm64 (2.72.4-0ubuntu2.9) 并覆盖 (2.72.4-0ubuntu2.2) ...
准备解压 .../03-libglib2.0-dev-bin_2.72.4-0ubuntu2.9_arm64.deb  ...
正在解压 libglib2.0-dev-bin (2.72.4-0ubuntu2.9) 并覆盖 (2.72.4-0ubuntu2.2) ...
准备解压 .../04-libglib2.0-bin_2.72.4-0ubuntu2.9_arm64.deb  ...
正在解压 libglib2.0-bin (2.72.4-0ubuntu2.9) 并覆盖 (2.72.4-0ubuntu2.2) ...
准备解压 .../05-libglib2.0-0_2.72.4-0ubuntu2.9_arm64.deb  ...
正在解压 libglib2.0-0:arm64 (2.72.4-0ubuntu2.9) 并覆盖 (2.72.4-0ubuntu2.2) ...
准备解压 .../06-python3-pkg-resources_59.6.0-1.2ubuntu0.22.04.3_all.deb  ...
正在解压 python3-pkg-resources (59.6.0-1.2ubuntu0.22.04.3) 并覆盖 (59.6.0-1.2ubuntu0.22.04.1) ...
准备解压 .../07-wget_1.21.2-2ubuntu1.1_arm64.deb  ...
正在解压 wget (1.21.2-2ubuntu1.1) 并覆盖 (1.21.2-2ubuntu1) ...
准备解压 .../08-libcurl4-openssl-dev_7.81.0-1ubuntu1.24_arm64.deb  ...
正在解压 libcurl4-openssl-dev:arm64 (7.81.0-1ubuntu1.24) 并覆盖 (7.81.0-1ubuntu1.13) ...
准备解压 .../09-libcurl4_7.81.0-1ubuntu1.24_arm64.deb  ...
正在解压 libcurl4:arm64 (7.81.0-1ubuntu1.24) 并覆盖 (7.81.0-1ubuntu1.13) ...
正在选中未选择的软件包 curl。
准备解压 .../10-curl_7.81.0-1ubuntu1.24_arm64.deb  ...
正在解压 curl (7.81.0-1ubuntu1.24) ...
正在选中未选择的软件包 libavdevice58:arm64。
准备解压 .../11-libavdevice58_7%3a4.4.2-0ubuntu0.22.04.1_arm64.deb  ...
正在解压 libavdevice58:arm64 (7:4.4.2-0ubuntu0.22.04.1) ...
正在选中未选择的软件包 ffmpeg。
准备解压 .../12-ffmpeg_7%3a4.4.2-0ubuntu0.22.04.1_arm64.deb  ...
正在解压 ffmpeg (7:4.4.2-0ubuntu0.22.04.1) ...
正在选中未选择的软件包 javascript-common。
准备解压 .../13-javascript-common_11+nmu1_all.deb  ...
正在解压 javascript-common (11+nmu1) ...
正在选中未选择的软件包 libgl1-mesa-glx:arm64。
准备解压 .../14-libgl1-mesa-glx_23.0.4-0ubuntu1~22.04.1_arm64.deb  ...
正在解压 libgl1-mesa-glx:arm64 (23.0.4-0ubuntu1~22.04.1) ...
正在选中未选择的软件包 libjs-jquery。
准备解压 .../15-libjs-jquery_3.6.0+dfsg+~3.5.13-1_all.deb  ...
正在解压 libjs-jquery (3.6.0+dfsg+~3.5.13-1) ...
正在选中未选择的软件包 libjs-underscore。
准备解压 .../16-libjs-underscore_1.13.2~dfsg-2_all.deb  ...
正在解压 libjs-underscore (1.13.2~dfsg-2) ...
正在选中未选择的软件包 libjs-sphinxdoc。
准备解压 .../17-libjs-sphinxdoc_4.3.2-1_all.deb  ...
正在解压 libjs-sphinxdoc (4.3.2-1) ...
正在选中未选择的软件包 libpython3.10-dev:arm64。
准备解压 .../18-libpython3.10-dev_3.10.12-1~22.04.15_arm64.deb  ...
正在解压 libpython3.10-dev:arm64 (3.10.12-1~22.04.15) ...
正在选中未选择的软件包 libpython3-dev:arm64。
准备解压 .../19-libpython3-dev_3.10.6-1~22.04.1_arm64.deb  ...
正在解压 libpython3-dev:arm64 (3.10.6-1~22.04.1) ...
准备解压 .../20-net-tools_1.60+git20181103.0eebece-1ubuntu5.4_arm64.deb  ...
正在解压 net-tools (1.60+git20181103.0eebece-1ubuntu5.4) 并覆盖 (1.60+git20181103.0eebece-1ubuntu5) ...
正在选中未选择的软件包 python3.10-dev。
准备解压 .../21-python3.10-dev_3.10.12-1~22.04.15_arm64.deb  ...
正在解压 python3.10-dev (3.10.12-1~22.04.15) ...
正在选中未选择的软件包 python3-dev。
准备解压 .../22-python3-dev_3.10.6-1~22.04.1_arm64.deb  ...
正在解压 python3-dev (3.10.6-1~22.04.1) ...
正在选中未选择的软件包 python3-setuptools。
准备解压 .../23-python3-setuptools_59.6.0-1.2ubuntu0.22.04.3_all.deb  ...
正在解压 python3-setuptools (59.6.0-1.2ubuntu0.22.04.3) ...
正在选中未选择的软件包 python3-wheel。
准备解压 .../24-python3-wheel_0.37.1-2ubuntu0.22.04.1_all.deb  ...
正在解压 python3-wheel (0.37.1-2ubuntu0.22.04.1) ...
正在选中未选择的软件包 python3-pip。
准备解压 .../25-python3-pip_22.0.2+dfsg-1ubuntu0.7_all.deb  ...
正在解压 python3-pip (22.0.2+dfsg-1ubuntu0.7) ...
正在选中未选择的软件包 python3-pip-whl。
准备解压 .../26-python3-pip-whl_22.0.2+dfsg-1ubuntu0.7_all.deb  ...
正在解压 python3-pip-whl (22.0.2+dfsg-1ubuntu0.7) ...
正在选中未选择的软件包 python3-setuptools-whl。
准备解压 .../27-python3-setuptools-whl_59.6.0-1.2ubuntu0.22.04.3_all.deb  ...
正在解压 python3-setuptools-whl (59.6.0-1.2ubuntu0.22.04.3) ...
正在选中未选择的软件包 python3.10-venv。
准备解压 .../28-python3.10-venv_3.10.12-1~22.04.15_arm64.deb  ...
正在解压 python3.10-venv (3.10.12-1~22.04.15) ...
正在选中未选择的软件包 python3-venv。
准备解压 .../29-python3-venv_3.10.6-1~22.04.1_arm64.deb  ...
正在解压 python3-venv (3.10.6-1~22.04.1) ...
正在设置 javascript-common (11+nmu1) ...
正在设置 net-tools (1.60+git20181103.0eebece-1ubuntu5.4) ...
正在设置 python3-setuptools-whl (59.6.0-1.2ubuntu0.22.04.3) ...
正在设置 wget (1.21.2-2ubuntu1.1) ...
正在设置 python3-pip-whl (22.0.2+dfsg-1ubuntu0.7) ...
正在设置 libglib2.0-0:arm64 (2.72.4-0ubuntu2.9) ...
正在设置 libglib2.0-bin (2.72.4-0ubuntu2.9) ...
正在设置 gnome-shell-common (42.9-0ubuntu2.3) ...
正在设置 libobjc4:arm64 (12.3.0-1ubuntu1~22.04.3) ...
正在设置 libgomp1:arm64 (12.3.0-1ubuntu1~22.04.3) ...
正在设置 libatomic1:arm64 (12.3.0-1ubuntu1~22.04.3) ...
正在设置 libpython3.10-minimal:arm64 (3.10.12-1~22.04.15) ...
正在设置 libavdevice58:arm64 (7:4.4.2-0ubuntu0.22.04.1) ...
正在设置 libgfortran5:arm64 (12.3.0-1ubuntu1~22.04.3) ...
正在设置 libubsan1:arm64 (12.3.0-1ubuntu1~22.04.3) ...
正在设置 libgl1-mesa-glx:arm64 (23.0.4-0ubuntu1~22.04.1) ...
正在设置 libhwasan0:arm64 (12.3.0-1ubuntu1~22.04.3) ...
正在设置 libcurl4:arm64 (7.81.0-1ubuntu1.24) ...
正在设置 curl (7.81.0-1ubuntu1.24) ...
正在设置 ffmpeg (7:4.4.2-0ubuntu0.22.04.1) ...
正在设置 libjs-jquery (3.6.0+dfsg+~3.5.13-1) ...
正在设置 libcc1-0:arm64 (12.3.0-1ubuntu1~22.04.3) ...
正在设置 liblsan0:arm64 (12.3.0-1ubuntu1~22.04.3) ...
正在设置 libitm1:arm64 (12.3.0-1ubuntu1~22.04.3) ...
正在设置 libjs-underscore (1.13.2~dfsg-2) ...
正在设置 python3.10-minimal (3.10.12-1~22.04.15) ...
正在设置 libpython3.10-stdlib:arm64 (3.10.12-1~22.04.15) ...
正在设置 libcurl4-openssl-dev:arm64 (7.81.0-1ubuntu1.24) ...
正在设置 libjs-sphinxdoc (4.3.2-1) ...
正在设置 libpython3-stdlib:arm64 (3.10.6-1~22.04.1) ...
正在设置 libpython3.10:arm64 (3.10.12-1~22.04.15) ...
正在设置 python3.10 (3.10.12-1~22.04.15) ...
正在设置 python3 (3.10.6-1~22.04.1) ...
running python rtupdate hooks for python3.10...
running python post-rtupdate hooks for python3.10...
正在设置 python3-wheel (0.37.1-2ubuntu0.22.04.1) ...
正在设置 libpython3.10-dev:arm64 (3.10.12-1~22.04.15) ...
正在设置 gnome-shell (42.9-0ubuntu2.3) ...
正在设置 python3.10-dev (3.10.12-1~22.04.15) ...
正在设置 python3-pkg-resources (59.6.0-1.2ubuntu0.22.04.3) ...
正在设置 libglib2.0-dev-bin (2.72.4-0ubuntu2.9) ...
正在设置 libpython3-dev:arm64 (3.10.6-1~22.04.1) ...
正在设置 python3.10-venv (3.10.12-1~22.04.15) ...
正在设置 python3-setuptools (59.6.0-1.2ubuntu0.22.04.3) ...
正在设置 python3-venv (3.10.6-1~22.04.1) ...
正在设置 libglib2.0-dev:arm64 (2.72.4-0ubuntu2.9) ...
正在设置 python3-dev (3.10.6-1~22.04.1) ...
正在设置 python3-pip (22.0.2+dfsg-1ubuntu0.7) ...
正在处理用于 desktop-file-utils (0.26-1ubuntu3) 的触发器 ...
正在处理用于 hicolor-icon-theme (0.17-2) 的触发器 ...
正在处理用于 gnome-menus (3.36.0-1ubuntu3) 的触发器 ...
正在处理用于 libc-bin (2.35-0ubuntu3.1) 的触发器 ...
正在处理用于 man-db (2.10.2-1) 的触发器 ...
正在处理用于 mailcap (3.70+nmu1ubuntu1) 的触发器 ...
[INFO] 基础依赖安装完成

==== 第 3 步: 安装 RKNN NPU 运行时 ====
[INFO] NPU 驱动已加载: v0.9.0
[INFO] librknnrt.so 已安装，跳过

==== 第 4 步: 创建 Python 虚拟环境 ====
[INFO] Python 版本: 3.10
[INFO] 创建虚拟环境...
[INFO] 虚拟环境创建完成
[INFO] 配置 pip 清华大学镜像源...
[INFO] pip 镜像源配置完成

==== 第 5 步: 安装 Python 依赖 ====
[INFO] 升级 pip...
Looking in indexes: https://pypi.tuna.tsinghua.edu.cn/simple
Requirement already satisfied: pip in /opt/rk3568/.venv/lib/python3.10/site-packages (22.0.2)
Collecting pip
  Downloading https://pypi.tuna.tsinghua.edu.cn/packages/3a/eb/fea4d1d51c49832120f7f285d07306db3960f423a2612c6057caf3e8196f/pip-26.1.1-py3-none-any.whl (1.8 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.8/1.8 MB 5.1 MB/s eta 0:00:00
Installing collected packages: pip
  Attempting uninstall: pip
    Found existing installation: pip 22.0.2
    Uninstalling pip-22.0.2:
      Successfully uninstalled pip-22.0.2
Successfully installed pip-26.1.1
[INFO] 安装核心依赖...
Looking in indexes: https://pypi.tuna.tsinghua.edu.cn/simple
Collecting numpy
  Downloading numpy-2.2.6-cp310-cp310-manylinux_2_17_aarch64.manylinux2014_aarch64.whl (14.3 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 14.3/14.3 MB 11.6 MB/s  0:00:01
Collecting opencv-python-headless
  Downloading opencv_python_headless-4.13.0.92-cp37-abi3-manylinux_2_28_aarch64.whl (35.0 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 35.0/35.0 MB 11.7 MB/s  0:00:02
Collecting pyyaml
  Downloading pyyaml-6.0.3-cp310-cp310-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl (740 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 740.6/740.6 kB 17.9 MB/s  0:00:00
Collecting websockets
  Downloading websockets-16.0-cp310-cp310-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl (185 kB)
Installing collected packages: websockets, pyyaml, numpy, opencv-python-headless
Successfully installed numpy-2.2.6 opencv-python-headless-4.13.0.92 pyyaml-6.0.3 websockets-16.0
[INFO] 核心依赖安装完成

==== 第 6 步: 安装 RKNNLite2 ====
[INFO] 安装 rknnlite2...
Looking in indexes: https://pypi.tuna.tsinghua.edu.cn/simple
ERROR: Could not find a version that satisfies the requirement rknnlite2 (from versions: none)
ERROR: No matching distribution found for rknnlite2
[WARN] pip 安装 rknnlite2 失败，尝试从 GitHub 安装...
Looking in indexes: https://pypi.tuna.tsinghua.edu.cn/simple
[ERROR] rknnlite2 安装失败，请手动安装
[ERROR] 下载地址: https://github.com/rockchip-linux/rknpu2

==== 第 7 步: 安装 AI 推理库 (PaddleOCR + HyperLPR3) ====
[INFO] 安装 PaddlePaddle (ARM64 版本)...
[INFO] 注意: PaddlePaddle ARM 版本需要从百度镜像下载
Looking in indexes: https://pypi.tuna.tsinghua.edu.cn/simple
Collecting paddlepaddle
  Downloading paddlepaddle-3.2.2-cp310-cp310-manylinux2014_aarch64.whl (88.2 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 88.2/88.2 MB 11.7 MB/s  0:00:07
Collecting httpx (from paddlepaddle)
  Downloading httpx-0.28.1-py3-none-any.whl (73 kB)
Requirement already satisfied: numpy>=1.21 in /opt/rk3568/.venv/lib/python3.10/site-packages (from paddlepaddle) (2.2.6)
Collecting protobuf>=3.20.2 (from paddlepaddle)
  Downloading protobuf-7.34.1-cp310-abi3-manylinux2014_aarch64.whl (325 kB)
Collecting Pillow (from paddlepaddle)
  Downloading pillow-12.2.0-cp310-cp310-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl (6.4 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 6.4/6.4 MB 11.9 MB/s  0:00:00
Collecting opt-einsum==3.3.0 (from paddlepaddle)
  Downloading opt_einsum-3.3.0-py3-none-any.whl (65 kB)
Collecting networkx (from paddlepaddle)
  Downloading networkx-3.4.2-py3-none-any.whl (1.7 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.7/1.7 MB 11.4 MB/s  0:00:00
Collecting typing-extensions (from paddlepaddle)
  Downloading typing_extensions-4.15.0-py3-none-any.whl (44 kB)
Collecting safetensors>=0.6.0 (from paddlepaddle)
  Downloading safetensors-0.7.0-cp38-abi3-manylinux_2_17_aarch64.manylinux2014_aarch64.whl (491 kB)
Collecting anyio (from httpx->paddlepaddle)
  Downloading anyio-4.13.0-py3-none-any.whl (114 kB)
Collecting certifi (from httpx->paddlepaddle)
  Downloading certifi-2026.4.22-py3-none-any.whl (135 kB)
Collecting httpcore==1.* (from httpx->paddlepaddle)
  Downloading httpcore-1.0.9-py3-none-any.whl (78 kB)
Collecting idna (from httpx->paddlepaddle)
  Downloading idna-3.15-py3-none-any.whl (72 kB)
Collecting h11>=0.16 (from httpcore==1.*->httpx->paddlepaddle)
  Downloading h11-0.16.0-py3-none-any.whl (37 kB)
Collecting exceptiongroup>=1.0.2 (from anyio->httpx->paddlepaddle)
  Downloading exceptiongroup-1.3.1-py3-none-any.whl (16 kB)
Installing collected packages: typing-extensions, safetensors, protobuf, Pillow, opt-einsum, networkx, idna, h11, certifi, httpcore, exceptiongroup, anyio, httpx, paddlepaddle
Successfully installed Pillow-12.2.0 anyio-4.13.0 certifi-2026.4.22 exceptiongroup-1.3.1 h11-0.16.0 httpcore-1.0.9 httpx-0.28.1 idna-3.15 networkx-3.4.2 opt-einsum-3.3.0 paddlepaddle-3.2.2 protobuf-7.34.1 safetensors-0.7.0 typing-extensions-4.15.0
[INFO] 安装 PaddleOCR...
Looking in indexes: https://pypi.tuna.tsinghua.edu.cn/simple
Collecting paddleocr
  Downloading paddleocr-3.5.0-py3-none-any.whl (120 kB)
Collecting paddlex<3.6.0,>=3.5.0 (from paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading paddlex-3.5.2-py3-none-any.whl (2.2 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.2/2.2 MB 11.5 MB/s  0:00:00
Requirement already satisfied: PyYAML>=6 in /opt/rk3568/.venv/lib/python3.10/site-packages (from paddleocr) (6.0.3)
Collecting requests (from paddleocr)
  Downloading requests-2.34.2-py3-none-any.whl (73 kB)
Requirement already satisfied: typing-extensions>=4.12 in /opt/rk3568/.venv/lib/python3.10/site-packages (from paddleocr) (4.15.0)
Collecting aistudio-sdk>=0.3.5 (from paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading aistudio_sdk-0.3.8-py3-none-any.whl (62 kB)
Collecting chardet (from paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading chardet-7.4.3-cp310-cp310-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl (876 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 876.6/876.6 kB 13.0 MB/s  0:00:00
Collecting colorlog (from paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading colorlog-6.10.1-py3-none-any.whl (11 kB)
Collecting filelock (from paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading filelock-3.29.0-py3-none-any.whl (39 kB)
Collecting huggingface-hub (from paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading huggingface_hub-1.15.0-py3-none-any.whl (663 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 663.6/663.6 kB 15.1 MB/s  0:00:00
Collecting modelscope>=1.28.0 (from paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading modelscope-1.37.0-py3-none-any.whl (6.1 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 6.1/6.1 MB 10.6 MB/s  0:00:00
Requirement already satisfied: numpy<2.4,>=1.24 in /opt/rk3568/.venv/lib/python3.10/site-packages (from paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr) (2.2.6)
Collecting packaging (from paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading packaging-26.2-py3-none-any.whl (100 kB)
Collecting pandas>=1.3 (from paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading pandas-2.3.3-cp310-cp310-manylinux_2_24_aarch64.manylinux_2_28_aarch64.whl (12.1 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 12.1/12.1 MB 11.7 MB/s  0:00:01
Requirement already satisfied: pillow in /opt/rk3568/.venv/lib/python3.10/site-packages (from paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr) (12.2.0)
Collecting prettytable (from paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading prettytable-3.17.0-py3-none-any.whl (34 kB)
Collecting py-cpuinfo (from paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading py_cpuinfo-9.0.0-py3-none-any.whl (22 kB)
Collecting pydantic>=2 (from paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading pydantic-2.13.4-py3-none-any.whl (472 kB)
Collecting PyYAML>=6 (from paddleocr)
  Downloading PyYAML-6.0.2-cp310-cp310-manylinux_2_17_aarch64.manylinux2014_aarch64.whl (718 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 718.5/718.5 kB 14.5 MB/s  0:00:00
Collecting ruamel.yaml (from paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading ruamel_yaml-0.19.1-py3-none-any.whl (118 kB)
Collecting ujson (from paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading ujson-5.12.1-cp310-cp310-manylinux_2_24_aarch64.manylinux_2_28_aarch64.whl (59 kB)
Collecting imagesize (from paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading imagesize-2.0.0-py2.py3-none-any.whl (9.4 kB)
Collecting opencv-contrib-python==4.10.0.84 (from paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading opencv_contrib_python-4.10.0.84-cp37-abi3-manylinux_2_17_aarch64.manylinux2014_aarch64.whl (47.4 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 47.4/47.4 MB 10.9 MB/s  0:00:04
Collecting pyclipper (from paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading pyclipper-1.4.0-cp310-cp310-manylinux_2_24_aarch64.manylinux_2_28_aarch64.whl (943 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 943.3/943.3 kB 11.0 MB/s  0:00:00
Collecting pypdfium2>=4 (from paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading pypdfium2-5.8.0-py3-none-manylinux_2_17_aarch64.manylinux2014_aarch64.whl (3.6 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 3.6/3.6 MB 10.6 MB/s  0:00:00
Collecting python-bidi (from paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading python_bidi-0.6.10-cp310-cp310-manylinux_2_17_aarch64.manylinux2014_aarch64.whl (296 kB)
Collecting shapely (from paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading shapely-2.1.2-cp310-cp310-manylinux2014_aarch64.manylinux_2_17_aarch64.whl (3.0 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 3.0/3.0 MB 11.0 MB/s  0:00:00
Collecting psutil (from aistudio-sdk>=0.3.5->paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading psutil-7.2.2-cp36-abi3-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl (156 kB)
Collecting tqdm (from aistudio-sdk>=0.3.5->paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading tqdm-4.67.3-py3-none-any.whl (78 kB)
Collecting bce-python-sdk (from aistudio-sdk>=0.3.5->paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading bce_python_sdk-0.9.71-py3-none-any.whl (417 kB)
Collecting click (from aistudio-sdk>=0.3.5->paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading click-8.3.3-py3-none-any.whl (110 kB)
Requirement already satisfied: setuptools in /opt/rk3568/.venv/lib/python3.10/site-packages (from modelscope>=1.28.0->paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr) (59.6.0)
Collecting urllib3>=1.26 (from modelscope>=1.28.0->paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading urllib3-2.7.0-py3-none-any.whl (131 kB)
Collecting python-dateutil>=2.8.2 (from pandas>=1.3->paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading python_dateutil-2.9.0.post0-py2.py3-none-any.whl (229 kB)
Collecting pytz>=2020.1 (from pandas>=1.3->paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading pytz-2026.2-py2.py3-none-any.whl (510 kB)
Collecting tzdata>=2022.7 (from pandas>=1.3->paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading tzdata-2026.2-py2.py3-none-any.whl (349 kB)
Collecting annotated-types>=0.6.0 (from pydantic>=2->paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading annotated_types-0.7.0-py3-none-any.whl (13 kB)
Collecting pydantic-core==2.46.4 (from pydantic>=2->paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading pydantic_core-2.46.4-cp310-cp310-manylinux_2_17_aarch64.manylinux2014_aarch64.whl (2.0 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.0/2.0 MB 12.2 MB/s  0:00:00
Collecting typing-inspection>=0.4.2 (from pydantic>=2->paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading typing_inspection-0.4.2-py3-none-any.whl (14 kB)
Collecting six>=1.5 (from python-dateutil>=2.8.2->pandas>=1.3->paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading six-1.17.0-py2.py3-none-any.whl (11 kB)
Collecting charset_normalizer<4,>=2 (from requests->paddleocr)
  Downloading charset_normalizer-3.4.7-cp310-cp310-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl (209 kB)
Requirement already satisfied: idna<4,>=2.5 in /opt/rk3568/.venv/lib/python3.10/site-packages (from requests->paddleocr) (3.15)
Requirement already satisfied: certifi>=2023.5.7 in /opt/rk3568/.venv/lib/python3.10/site-packages (from requests->paddleocr) (2026.4.22)
Collecting pycryptodome>=3.8.0 (from bce-python-sdk->aistudio-sdk>=0.3.5->paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading pycryptodome-3.23.0-cp37-abi3-manylinux_2_17_aarch64.manylinux2014_aarch64.whl (2.2 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.2/2.2 MB 12.4 MB/s  0:00:00
Collecting future>=0.6.0 (from bce-python-sdk->aistudio-sdk>=0.3.5->paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading future-1.0.0-py3-none-any.whl (491 kB)
Collecting crc32c>=2.2.post0 (from bce-python-sdk->aistudio-sdk>=0.3.5->paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading crc32c-2.8-cp310-cp310-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl (80 kB)
Collecting fsspec>=2023.5.0 (from huggingface-hub->paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading fsspec-2026.4.0-py3-none-any.whl (203 kB)
Collecting hf-xet<2.0.0,>=1.4.3 (from huggingface-hub->paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading hf_xet-1.5.0-cp37-abi3-manylinux_2_28_aarch64.whl (4.3 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.3/4.3 MB 12.0 MB/s  0:00:00
Requirement already satisfied: httpx<1,>=0.23.0 in /opt/rk3568/.venv/lib/python3.10/site-packages (from huggingface-hub->paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr) (0.28.1)
Collecting typer>=0.20.0 (from huggingface-hub->paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading typer-0.25.1-py3-none-any.whl (58 kB)
Requirement already satisfied: anyio in /opt/rk3568/.venv/lib/python3.10/site-packages (from httpx<1,>=0.23.0->huggingface-hub->paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr) (4.13.0)
Requirement already satisfied: httpcore==1.* in /opt/rk3568/.venv/lib/python3.10/site-packages (from httpx<1,>=0.23.0->huggingface-hub->paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr) (1.0.9)
Requirement already satisfied: h11>=0.16 in /opt/rk3568/.venv/lib/python3.10/site-packages (from httpcore==1.*->httpx<1,>=0.23.0->huggingface-hub->paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr) (0.16.0)
Collecting shellingham>=1.3.0 (from typer>=0.20.0->huggingface-hub->paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading shellingham-1.5.4-py2.py3-none-any.whl (9.8 kB)
Collecting rich>=13.8.0 (from typer>=0.20.0->huggingface-hub->paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading rich-15.0.0-py3-none-any.whl (310 kB)
Collecting annotated-doc>=0.0.2 (from typer>=0.20.0->huggingface-hub->paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading annotated_doc-0.0.4-py3-none-any.whl (5.3 kB)
Collecting markdown-it-py>=2.2.0 (from rich>=13.8.0->typer>=0.20.0->huggingface-hub->paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading markdown_it_py-4.2.0-py3-none-any.whl (91 kB)
Collecting pygments<3.0.0,>=2.13.0 (from rich>=13.8.0->typer>=0.20.0->huggingface-hub->paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading pygments-2.20.0-py3-none-any.whl (1.2 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.2/1.2 MB 15.1 MB/s  0:00:00
Collecting mdurl~=0.1 (from markdown-it-py>=2.2.0->rich>=13.8.0->typer>=0.20.0->huggingface-hub->paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading mdurl-0.1.2-py3-none-any.whl (10.0 kB)
Requirement already satisfied: exceptiongroup>=1.0.2 in /opt/rk3568/.venv/lib/python3.10/site-packages (from anyio->httpx<1,>=0.23.0->huggingface-hub->paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr) (1.3.1)
Collecting wcwidth (from prettytable->paddlex<3.6.0,>=3.5.0->paddlex[ocr-core]<3.6.0,>=3.5.0->paddleocr)
  Downloading wcwidth-0.7.0-py3-none-any.whl (110 kB)
Installing collected packages: pytz, py-cpuinfo, wcwidth, urllib3, ujson, tzdata, typing-inspection, tqdm, six, shellingham, shapely, ruamel.yaml, PyYAML, python-bidi, pypdfium2, pygments, pydantic-core, pycryptodome, pyclipper, psutil, packaging, opencv-contrib-python, mdurl, imagesize, hf-xet, future, fsspec, filelock, crc32c, colorlog, click, charset_normalizer, chardet, annotated-types, annotated-doc, requests, python-dateutil, pydantic, prettytable, markdown-it-py, bce-python-sdk, rich, pandas, modelscope, aistudio-sdk, typer, huggingface-hub, paddlex, paddleocr
  Attempting uninstall: PyYAML
    Found existing installation: PyYAML 6.0.3
    Uninstalling PyYAML-6.0.3:
      Successfully uninstalled PyYAML-6.0.3
Successfully installed PyYAML-6.0.2 aistudio-sdk-0.3.8 annotated-doc-0.0.4 annotated-types-0.7.0 bce-python-sdk-0.9.71 chardet-7.4.3 charset_normalizer-3.4.7 click-8.3.3 colorlog-6.10.1 crc32c-2.8 filelock-3.29.0 fsspec-2026.4.0 future-1.0.0 hf-xet-1.5.0 huggingface-hub-1.15.0 imagesize-2.0.0 markdown-it-py-4.2.0 mdurl-0.1.2 modelscope-1.37.0 opencv-contrib-python-4.10.0.84 packaging-26.2 paddleocr-3.5.0 paddlex-3.5.2 pandas-2.3.3 prettytable-3.17.0 psutil-7.2.2 py-cpuinfo-9.0.0 pyclipper-1.4.0 pycryptodome-3.23.0 pydantic-2.13.4 pydantic-core-2.46.4 pygments-2.20.0 pypdfium2-5.8.0 python-bidi-0.6.10 python-dateutil-2.9.0.post0 pytz-2026.2 requests-2.34.2 rich-15.0.0 ruamel.yaml-0.19.1 shapely-2.1.2 shellingham-1.5.4 six-1.17.0 tqdm-4.67.3 typer-0.25.1 typing-inspection-0.4.2 tzdata-2026.2 ujson-5.12.1 urllib3-2.7.0 wcwidth-0.7.0
[INFO] 安装 HyperLPR3...
Looking in indexes: https://pypi.tuna.tsinghua.edu.cn/simple
Collecting hyperlpr3
  Downloading hyperlpr3-0.1.3-py3-none-any.whl (23 kB)
Collecting opencv-python (from hyperlpr3)
  Downloading opencv_python-4.13.0.92-cp37-abi3-manylinux_2_28_aarch64.whl (46.7 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 46.7/46.7 MB 10.5 MB/s  0:00:04
Collecting onnxruntime (from hyperlpr3)
  Downloading onnxruntime-1.23.2-cp310-cp310-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl (15.2 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 15.2/15.2 MB 10.4 MB/s  0:00:01
Requirement already satisfied: tqdm in /opt/rk3568/.venv/lib/python3.10/site-packages (from hyperlpr3) (4.67.3)
Requirement already satisfied: requests in /opt/rk3568/.venv/lib/python3.10/site-packages (from hyperlpr3) (2.34.2)
Collecting fastapi (from hyperlpr3)
  Downloading fastapi-0.136.1-py3-none-any.whl (117 kB)
Collecting uvicorn (from hyperlpr3)
  Downloading uvicorn-0.47.0-py3-none-any.whl (71 kB)
Collecting python-multipart (from hyperlpr3)
  Downloading python_multipart-0.0.28-py3-none-any.whl (29 kB)
Collecting loguru (from hyperlpr3)
  Downloading loguru-0.7.3-py3-none-any.whl (61 kB)
Collecting starlette>=0.46.0 (from fastapi->hyperlpr3)
  Downloading starlette-1.0.0-py3-none-any.whl (72 kB)
Requirement already satisfied: pydantic>=2.9.0 in /opt/rk3568/.venv/lib/python3.10/site-packages (from fastapi->hyperlpr3) (2.13.4)
Requirement already satisfied: typing-extensions>=4.8.0 in /opt/rk3568/.venv/lib/python3.10/site-packages (from fastapi->hyperlpr3) (4.15.0)
Requirement already satisfied: typing-inspection>=0.4.2 in /opt/rk3568/.venv/lib/python3.10/site-packages (from fastapi->hyperlpr3) (0.4.2)
Requirement already satisfied: annotated-doc>=0.0.2 in /opt/rk3568/.venv/lib/python3.10/site-packages (from fastapi->hyperlpr3) (0.0.4)
Requirement already satisfied: annotated-types>=0.6.0 in /opt/rk3568/.venv/lib/python3.10/site-packages (from pydantic>=2.9.0->fastapi->hyperlpr3) (0.7.0)
Requirement already satisfied: pydantic-core==2.46.4 in /opt/rk3568/.venv/lib/python3.10/site-packages (from pydantic>=2.9.0->fastapi->hyperlpr3) (2.46.4)
Requirement already satisfied: anyio<5,>=3.6.2 in /opt/rk3568/.venv/lib/python3.10/site-packages (from starlette>=0.46.0->fastapi->hyperlpr3) (4.13.0)
Requirement already satisfied: exceptiongroup>=1.0.2 in /opt/rk3568/.venv/lib/python3.10/site-packages (from anyio<5,>=3.6.2->starlette>=0.46.0->fastapi->hyperlpr3) (1.3.1)
Requirement already satisfied: idna>=2.8 in /opt/rk3568/.venv/lib/python3.10/site-packages (from anyio<5,>=3.6.2->starlette>=0.46.0->fastapi->hyperlpr3) (3.15)
Collecting coloredlogs (from onnxruntime->hyperlpr3)
  Downloading coloredlogs-15.0.1-py2.py3-none-any.whl (46 kB)
Collecting flatbuffers (from onnxruntime->hyperlpr3)
  Downloading flatbuffers-25.12.19-py2.py3-none-any.whl (26 kB)
Requirement already satisfied: numpy>=1.21.6 in /opt/rk3568/.venv/lib/python3.10/site-packages (from onnxruntime->hyperlpr3) (2.2.6)
Requirement already satisfied: packaging in /opt/rk3568/.venv/lib/python3.10/site-packages (from onnxruntime->hyperlpr3) (26.2)
Requirement already satisfied: protobuf in /opt/rk3568/.venv/lib/python3.10/site-packages (from onnxruntime->hyperlpr3) (7.34.1)
Collecting sympy (from onnxruntime->hyperlpr3)
  Downloading sympy-1.14.0-py3-none-any.whl (6.3 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 6.3/6.3 MB 2.8 MB/s  0:00:02
Collecting humanfriendly>=9.1 (from coloredlogs->onnxruntime->hyperlpr3)
  Downloading humanfriendly-10.0-py2.py3-none-any.whl (86 kB)
Requirement already satisfied: charset_normalizer<4,>=2 in /opt/rk3568/.venv/lib/python3.10/site-packages (from requests->hyperlpr3) (3.4.7)
Requirement already satisfied: urllib3<3,>=1.26 in /opt/rk3568/.venv/lib/python3.10/site-packages (from requests->hyperlpr3) (2.7.0)
Requirement already satisfied: certifi>=2023.5.7 in /opt/rk3568/.venv/lib/python3.10/site-packages (from requests->hyperlpr3) (2026.4.22)
Collecting mpmath<1.4,>=1.1.0 (from sympy->onnxruntime->hyperlpr3)
  Downloading mpmath-1.3.0-py3-none-any.whl (536 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 536.2/536.2 kB 2.8 MB/s  0:00:00
Requirement already satisfied: click>=7.0 in /opt/rk3568/.venv/lib/python3.10/site-packages (from uvicorn->hyperlpr3) (8.3.3)
Requirement already satisfied: h11>=0.8 in /opt/rk3568/.venv/lib/python3.10/site-packages (from uvicorn->hyperlpr3) (0.16.0)
Installing collected packages: mpmath, flatbuffers, uvicorn, sympy, python-multipart, opencv-python, loguru, humanfriendly, coloredlogs, starlette, onnxruntime, fastapi, hyperlpr3
Successfully installed coloredlogs-15.0.1 fastapi-0.136.1 flatbuffers-25.12.19 humanfriendly-10.0 hyperlpr3-0.1.3 loguru-0.7.3 mpmath-1.3.0 onnxruntime-1.23.2 opencv-python-4.13.0.92 python-multipart-0.0.28 starlette-1.0.0 sympy-1.14.0 uvicorn-0.47.0
[INFO] AI 推理库安装完成

==== 第 8 步: 验证安装 ====
[INFO] 检查 Python 依赖...
[WARN] 系统检查脚本执行失败（部分依赖可能未安装）
=== 核心依赖 ===
  ✓ NumPy
  ✓ OpenCV
  ✓ PyYAML
  ✓ WebSockets
=== AI 依赖 ===
  ✗ RKNNLite2 (未安装)
  ✓ PaddleOCR
Pull: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████| 11.9M/11.9M [00:01<00:00, 10.1MiB/s]
  ✓ HyperLPR3

==== 第 9 步: 配置 systemd 开机自启服务 ====
[INFO] 安装 systemd 服务...
[INFO] systemd 服务安装完成
[INFO] 启动服务: sudo systemctl start rk3568-vision
[INFO] 开机自启: sudo systemctl enable rk3568-vision
[INFO] 查看日志: sudo journalctl -u rk3568-vision -f

================================================
[INFO] 🎉 部署完成！
================================================

下一步操作:

  1. 检查配置文件:
     vi /opt/rk3568/config/config.yaml

  2. 手动运行测试:
     cd /opt/rk3568
     source .venv/bin/activate
     python3 src/main.py

  3. 启动后台服务:
     sudo systemctl start rk3568-vision
     sudo systemctl enable rk3568-vision  # 开机自启

  4. 查看运行日志:
     sudo journalctl -u rk3568-vision -f

  5. PC 端连接:
     python pc_client/client.py --host <RK3568的IP>

================================================
