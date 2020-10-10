---
title: Linux日常 之 搭建微型服务器
tags:
  - Linux
id: '470'
categories:
  - - tools
    - 系统管理维护
date: 2017-11-20 08:58:15
---

搭建微型服务器

如何把自己的电脑做成一个微型的服务器呢?

目前知道两种方法

*   `Python`
    
    ```shell
    
    python -m SimpleHTTPServer #Python2
    python -m http.server #python3
    ```
    
    默认端口8000,这是单线程访问.
    
    *   使用方法
        
        1.浏览器直接 输入你的本机IP地址,加上端口号8000
        
        `111.222.3.1:8000`
        
        2.传输文件的话,也可以用`wget` 命令
        
        `wget 111.222.3.1:8000/yourfile`
        
*   `ngix`
    
    *   安装`ngix`
        
        `sudo apt install ngix`
        
    *   配置ngix
        
        *   找到 `ngix`安装目录 然后 在`/etc/nginx/sites-available/default` 文件修改`server`字段中的内容如下:
        
        ```shell
        
                location / {
                        # First attempt to serve request as file, then
                        # as directory, then fall back to displaying a 404.
                        autoindex on; #新添加的,自动index
                        try_files $uri $uri/ =404;
                }
        ```
        
    *   使用方法
        
        我们可以将要分享的东西放在某个文件夹,然后通过软链接到 `/var/www/html`这个目录下.
        
        例如 我在`home`目录下,新建一个文件夹shared,然后链接到上面那个目录下
        
        $$ sudo ln -s /home/yourdir/Shared/ share$$
        
        那么效果如下
        
    
    1.  你本机中的shared 文件夹
    
    ![这里写图片描述](http://img.blog.csdn.net/20171120083954417?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvZGFyazU2Njk=/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)
    
    1.  经过软链接之后,你可以在浏览器输入你的电脑的IP地址,然后可见
    
    ![这里写图片描述](http://img.blog.csdn.net/20171120084112793?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvZGFyazU2Njk=/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)