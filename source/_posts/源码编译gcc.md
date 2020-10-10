---
title: 源码编译GCC
tags: []
id: '1377'
categories:
  - - programming
    - C/C++
  - - tools
    - 系统管理维护
comments: false
date: 2020-08-03 18:46:43
---

### 主要步骤

*   下载源码压缩包

```
wget https://ftp.gnu.org/gnu/gcc/gcc-5.3.0/gcc-5.3.0.tar.gz

tar xzf gcc-5.3.0.tar.gz
```

*   安装依赖

```
./contrib/download_prerequisites

1. 下载这三个包，到 gcc-5.3.0 这个目录里
# Necessary to build GCC.
MPFR=mpfr-2.4.2
GMP=gmp-4.3.2
MPC=mpc-0.8.1
2. 解压
3. 建立软链接，也就是快捷方式。
```

*   配置一下
*   make 命令安装
*   注意，需使用`gcc 4.9.2` 编译

```
  rm -rf build
  mkdir build
  cd build

  ../configure --enable-checking=release --enable-languages=c,c++ --disable-multilib

  make -j8
```

*   make install 安装到系统
*   或者 在 configure时， 加上`--prefix=/path/to/insall`
*   局部装也可以
*   使能 GCC

```
  (tvm.venv) zangchuanqi@n22-145-158:~/workspace/tensorflow$ cat ~/compiler_env.sh
  export PATH=/data01/zangchuanqi/gcc-7.3.0/build/install/bin:$PATH
  export LIBRARY_PATH=/data01/zangchuanqi/gcc-7.3.0/build/install/lib64:$LIBRARY_PATH
```

> https://gcc.gnu.org/onlinedocs/gcc/Environment-Variables.html

#### Reference

> https://gcc.gnu.org/install/index.html
> 
> https://gcc.gnu.org/install/configure.html
> 
> https://stackoverflow.com/questions/9253695/building-gcc-requires-gmp-4-2-mpfr-2-3-1-and-mpc-0-8-0

*   **结构体定义问题**

[https://blog.csdn.net/XCCCCZ/article/details/80958414](https://blog.csdn.net/XCCCCZ/article/details/80958414)

*   hack 一把

```
./md-unwind-support.h: In function ‘x86_64_fallback_frame_state’:
./md-unwind-support.h:65:47: error: dereferencing pointer to incomplete type ‘struct ucontext’
       sc = (struct sigcontext *) (void *) &uc_->uc_mcontext;
```

```
struct ucontext_t * uc_ = context->cfa;
```

*   **文件不存在**

```
../../../../libsanitizer/sanitizer_common/sanitizer_platform_limits_posix.cc:146:23: fatal error: sys/ustat.h: No such file or directory
```

**fixed** add a patch

> https://reviews.llvm.org/D47165

reference

> https://stackoverflow.com/questions/56096060/how-to-fix-the-gcc-compilation-error-sys-ustat-h-no-such-file-or-directory-i