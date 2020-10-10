---
title: LLVM 源码安装
tags: []
id: '1246'
categories:
  - - 工欲善其事必先利其器
comments: false
date: 2020-05-04 11:40:56
---

# 安装依赖

*   cmake 3.13.3 

```
tar xzf *.tar.gz
./bootstrap && gmake && gmake install

export install path bin like
export PATH=/home/lingyao.zcq/cmake-3.13.3/bin:$PATH
```

*   [https://www.cnblogs.com/freeweb/p/5788729.html](https://www.cnblogs.com/freeweb/p/5788729.html)
*   gcc 源码安装

# 下载源码

*   llvm
*   llvm-9.0.0.src.tar.xz
*   clang

*   cfe-9.0.0.src.tar.xz
*   clang-tools-extra-9.0.0.src.tar.xz
*   compiler-rt
*   compiler-rt-9.0.0.src.tar.xz

# 解压 并 整理project对应位置

 tar xJf llvm-9.0.0.src.tar.xz
 tar xJf cfe-9.0.0.src.tar.xz
 tar xJf compiler-rt-9.0.0.src.tar.xz
 tar xJf clang-tools-extra-9.0.0.src.tar.xz
 
 
 mv llvm-9.0.0.src llvm
 mv cfe-9.0.0.src llvm/tools/clang
 mv compiler-rt-9.0.0.src llvm/projects/compiler-rt
 mv clang-tools-extra-9.0.0.src llvm/tools/clang/tools/extra

# 安装

export PATH=/home/lingyao.zcq/cmake-3.13.3/bin:$PATH
export LD\_LIBRARY\_PATH=/lib64:$LD\_LIBRARY\_PATH
export LIBRARY\_PATH=/lib64:$LIBRARY\_PATH
rm -rf llvm\_build
mkdir llvm\_build
cd llvm\_build

cmake -DCMAKE\_BUILD\_TYPE="RELEASE" -DCXXFLAGS="-DDBGLOBALDCE" -DCMAKE\_CXX\_COMPILER=$GCC\_PATH/bin/g++ -DCMAKE\_C\_COMPILER=$GCC\_PATH/bin/gcc  ../llvm
# cmake -DCMAKE\_BUILD\_TYPE="RELEASE" -DCMAKE\_INSTALL\_PREFIX=$PWD/../install -DCMAKE\_CXX\_COMPILER=$GCC\_PATH/bin/g++ -DCMAKE\_C\_COMPILER=$GCC\_PATH/bin/gcc  ../llvm
#cmake -DCMAKE\_BUILD\_TYPE="DEBUG" -DCMAKE\_CXX\_COMPILER=$GCC\_PATH/bin/g++ -DCMAKE\_C\_COMPILER=$GCC\_PATH/bin/gcc  ../llvm
make -j
# make install

[https://blog.csdn.net/u012675539/article/details/51489078](https://blog.csdn.net/u012675539/article/details/51489078)

# clang 链接问题

*   编译llvm 时，需要 export 一下 LD\_LIBRARY\_PATH  和 LIBRARY\_PATH 是为了 链接是正确的链接对应的libc 和 libstdc++ 的库文件，否则会出现  \` `GLIBCXX_3.4.22' not found` 错误。

$ldd clang
./clang: /apsara/alicpp/built/gcc-4.9.2/gcc-4.9.2/lib64/libstdc++.so.6: version \`GLIBCXX\_3.4.22' not found (required by ./clang)
./clang: /apsara/alicpp/built/gcc-4.9.2/gcc-4.9.2/lib64/libstdc++.so.6: version \`GLIBCXX\_3.4.26' not found (required by ./clang)
./clang: /apsara/alicpp/built/gcc-4.9.2/gcc-4.9.2/lib64/libstdc++.so.6: version \`GLIBCXX\_3.4.21' not found (required by ./clang)
    linux-vdso.so.1 =>  (0x0000ffff892c1000)
    libpthread.so.0 => /usr/lib64/libpthread.so.0 (0x0000ffff89280000)
    libz.so.1 => /usr/lib64/libz.so.1 (0x0000ffff8924e000)
    librt.so.1 => /usr/lib64/librt.so.1 (0x0000ffff8922d000)
    libdl.so.2 => /usr/lib64/libdl.so.2 (0x0000ffff8920c000)
    libstdc++.so.6 => /apsara/alicpp/built/gcc-4.9.2/gcc-4.9.2/lib64/libstdc++.so.6 (0x0000ffff890c3000)
    libm.so.6 => /usr/lib64/libm.so.6 (0x0000ffff89012000)
    libgcc\_s.so.1 => /apsara/alicpp/built/gcc-4.9.2/gcc-4.9.2/lib64/libgcc\_s.so.1 (0x0000ffff88fe1000)
    libc.so.6 => /usr/lib64/libc.so.6 (0x0000ffff88e5a000)
    /lib/ld-linux-aarch64.so.1 (0x0000ffff892c2000)

*   在build.sh 中 声明一下 之后，在重新编译，是ok的。

*   `export LD_LIBRARY_PATH=/lib64:$LD_LIBRARY_PATH`
*   `export LIBRARY_PATH=/lib64:$LIBRARY_PATH`

\[lingyao.zcq@rt2d05376.sqa.tbc /home/lingyao.zcq/llvm8\]
$ldd llvm\_build/bin/clang
    linux-vdso.so.1 =>  (0x0000ffffa30b1000)
    libpthread.so.0 => /usr/lib64/libpthread.so.0 (0x0000ffffa3070000)
    libz.so.1 => /usr/lib64/libz.so.1 (0x0000ffffa303e000)
    librt.so.1 => /usr/lib64/librt.so.1 (0x0000ffffa301d000)
    libdl.so.2 => /usr/lib64/libdl.so.2 (0x0000ffffa2ffc000)
    libstdc++.so.6 => /usr/lib64/libstdc++.so.6 (0x0000ffffa2e15000)
    libm.so.6 => /usr/lib64/libm.so.6 (0x0000ffffa2d64000)
    libgcc\_s.so.1 => /usr/lib64/libgcc\_s.so.1 (0x0000ffffa2d33000)
    libc.so.6 => /usr/lib64/libc.so.6 (0x0000ffffa2bac000)
    /lib/ld-linux-aarch64.so.1 (0x0000ffffa30b2000)

然而在运行时，也出现了这个问题，那么

使用全局的 ld\_library\_path 没有生效

sudo vim /etc/ld.so.conf.d/pangu.conf 暂时修改了一下 盘古的 ld config 文件，删除 /apsara/ 的配置 是可以ok的