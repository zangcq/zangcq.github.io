---
title: ubuntu搭建ftp服务器
tags: []
id: '563'
categories:
  - - tools
    - 系统管理维护
date: 2018-01-02 22:26:44
---

## `ubuntu`搭建`ftp`服务器

`windows`开启服务

> [https://jingyan.baidu.com/article/0bc808fc408fa91bd585b94f.html](https://jingyan.baidu.com/article/0bc808fc408fa91bd585b94f.html)

### 1.安装`vsftpd`

*   查看是否安装

 `vsftpd -version`

*   如果未安装 则执行一下命令
    
    ```shell
    sudo apt-get install vsftpd
    ```
    

### 2.新建共享文件夹以及用户

1.  新建文件夹 或者 用已经存在的文件也行
    
    ```shell
    mkdir share
    #修改文件夹权限
    
    #修改可写权限
    chmod 777 share/
    ```
    
2.  新建`ftp`用户 `jack`
    
    ```shell
    
    sudo useradd -d ~/share -s /bin/bash jack
    ```
    
3.  为`jack`设置密码
    
    ```shell
    
    passwd jack
    ```
    

### 3.FTP配置文件

1.  修改`/etc/vsftpd.conf`根据需求,参考注释来修改配置,以下为主要配置参数
    
    ```shell
    
    #默认设置 禁止匿名访问
    # Allow anonymous FTP? (Disabled by default).
    anonymous_enable=NO
    #是否允许本地用户登录
    # Uncomment this to allow local users to log in.
    local_enable=YES
    #用户是否有写权限,可否新建或者上传文件
    # Uncomment this to enable any form of FTP write command.
    write_enable=YES
    ```
    
2.  无法登录 出现 530错误修改 `/etc/pam.d/vsftpd`
    
    ```shell
    
    sudo vim /etc/pam.d/vsftpd 
    ```
    
    ```shell
    
    # Standard behaviour for ftpd(8).
    #auth   required        pam_listfile.so item=user sense=deny file=/etc/ftpusers onerr=succeed
    
    # Note: vsftpd handles anonymous logins on its own. Do not enable pam_ftp.so.
    # Standard pam includes
    @include common-account
    @include common-session
    @include common-auth
    #auth   required        pam_shells.so
    ```
    

### 4.`vsftpd` 重启/状态查看

```shell

#重启服务
sudo service vsftpd restart

#查看状态
service vsftpd status
```

### 5.reference

> [http://www.cnblogs.com/CSGrandeur/p/3754126.html](http://www.cnblogs.com/CSGrandeur/p/3754126.html) [https://www.jianshu.com/p/d8e43ed427cc](https://www.jianshu.com/p/d8e43ed427cc) [https://cndaqiang.github.io/2017/09/27/ubuntu-vsftps/](https://cndaqiang.github.io/2017/09/27/ubuntu-vsftps/) [https://segmentfault.com/a/1190000005072142](https://segmentfault.com/a/1190000005072142) [http://blog.csdn.net/bingyu9875/article/details/52764491](http://blog.csdn.net/bingyu9875/article/details/52764491) [http://blog.csdn.net/zuosifengli/article/details/7086793](http://blog.csdn.net/zuosifengli/article/details/7086793)