---
title: Docker常用速记
tags:
  - Docker
id: '923'
categories:
  - - 工欲善其事必先利其器
  - - tools
    - 系统管理维护
date: 2019-08-18 16:13:41
---

### 0\. docker 安装

nvidia-docker安装步骤

*   卸载nvidia-docker1
*   centos： 加 repo
*   安装nvidia-docker2
*   重启docker服务

```

curl -s -L https://nvidia.github.io/nvidia-docker/centos7/nvidia-docker.repo  sudo tee /etc/yum.repos.d/nvidia-docker.repo

sudo yum install nvidia-docker2
sudo pkill -SIGHUP dockerd
```

[https://github.com/nvidia/nvidia-docker/wiki/Installation-(version-2.0)](https://github.com/nvidia/nvidia-docker/wiki/Installation-(version-2.0))

### 1\. 管理docker服务

```
docker启动命令,docker重启命令,docker关闭命令

启动        systemctl start docker
守护进程重启   sudo systemctl daemon-reload
重启docker服务   systemctl restart  docker
重启docker服务  sudo service docker restart
关闭docker   service docker stop   
关闭docker  systemctl stop docker
```

### 2\. Add user to docker group

> https://askubuntu.com/questions/477551/how-can-i-use-docker-without-sudo

```
# method 1
sudo usermod -aG docker $USER

# logout -> login will be enabled
# method2 
sudo setfacl -m user:$USER:rw /var/run/docker.sock
```

### 3\. 常用命令

#### 镜像管理

##### 查看镜像

```
docker images
```

*   REPOSITORY 所在库
*   TAG 打的标签，latest作为缺省的tag版本。
*   IMAGE ID 镜像编号
*   CREATED 创建时间
*   SIZE 空间大小

##### 镜像拉取

```
docker pull image-source
eg.
docker pull ubuntu
docker pull latest
```

如果pull出现错误，需要重新登录一下。

> [https://hub.docker.com](https://hub.docker.com/)

dockerhub的username和passwd

##### 查看镜像详细信息

```
docker inspect imageid
# eg.
docker inspect bed195a02b9f
```

##### 删除镜像

```
docker rmi imageid
docker rmi repo:tag
# remove all
docker rmi `docker images -q`
```

##### 创建镜像

*   通过容器创建 通常会新增很多东西到容器里，因此可以创建镜像供他人使用。 `docker commit -a "创建者" -m "创建说明" containerID repo:tag`

```
  # eg.
  docker commit -a "chuanqiz" -m "based zesheng caffe_quant-cuda8,for yolov3 generate golden" 5ce4a87d833a  chuanqiz/caffe_yolov3:version1
```

*   通过dockerfile创建

##### 镜像迁移（导入导出）

*   第一组 save/load 从镜像导出镜像

```
  # save image used repo:tag
  docker save -o chuanqiz.tar chuanqiz:v1
  docker save > chuanqiz.tar chuanqiz:v1
  # load
  docker load -i chuanqiz.tar
  docker load < chuanqiz.tar
```

*   第二组export/import 从容器导出镜像

```
  # export used contanerid
  docker export -o ubuntu_run.tar 6ed28165c58c
  # import used new repo:id
   docker import ubuntu_run.tar test/ubuntu1.0
```

##### 镜像发布

```
sudo docker login --username= reg.docker.alibaba-inc.com
sudo docker tag [ImageId] reg.docker.alibaba-inc.com/[仓库名]:[镜像版本号]
sudo docker push reg.docker.alibaba-inc.com/[仓库名]:[镜像版本号]
```

#### 容器管理

##### 容器状态

*   Created 已创建，资源就绪，未运行
*   Running 正在运行
*   Paused 暂停状态
*   Stopped 停止状态
*   Deleted 已删除，所有资源都已释放

##### 创建、启动、进入容器

```
docker run -p 5000:5000 -v /demo:/demo -name=chuanqi -it repo:tag  /bin/bash
```

常用参数说明

*   \-v 挂载文件夹
*   \-p 指定端口；本机端口：容器端口
*   \--name 容器名
*   \-it 以交互方式运行
*   \-d 后台运行
*   /bin/bash 交互方式
*   \--device /dev/nvidia0:/dev/nvidia0 挂载设备
*   \--net=host 网络设置
*   \-u root:root 用户映射
*   \-e 环境设置

##### 查看容器状态

```
# 查看运行状态的容器
docker ps
# 查看所有状态的容器
docker ps -a

Created 已创建，未启动
Up 正在运行
Exited 已退出
```

##### 创建容器

```
docker create --name chuanqiz imageid
```

##### 启动终止容器

```
docker start/stop containerid/name
```

##### 进入容器

```
docker exec -it containerid /bin/bash
```

##### 删除容器

```
docker rm containerid
docker rm `docker ps -q`
```

##### 随用随更

#### Reference

##### 入门文档

> https://docs.docker.com/get-started/
> 
> https://yeasy.gitbooks.io/docker\_practice/
> 
> https://stackoverflow.com/questions/25211198/docker-how-to-change-repository-name-or-rename-image