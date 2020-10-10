---
title: git 常用命令
tags:
  - git
id: '627'
categories:
  - - 工欲善其事必先利其器
date: 2018-09-02 15:47:49
---

#### vim 高亮多余空格

```

" 启用语法高亮
syntax on
" 高亮多余的空白字符及 
Tabhighlight RedundantSpaces ctermbg=red guibg=red
match RedundantSpaces /\s\+$\ \+\ze\t\\t/ 
" 使用 4 个空格，不使用 Tabset 
tabstop=4
set shiftwidth=4
set expandtabset 
softtabstop=4 
" 总是显示 DOS 格式文件中的 ^Mset 
fileformats=unix
```

### git 常用命令

##### 配置git用户名

```shell
 git config --global user.email lingyao.zcq@alibaba-inc.com
 git config --global user.name lingyao.zcq

 git config --local user.email zangcq.com@gmail.com
 git config --local user.name zangcqgit config --global user.name "chuanqi zang"git config --global user.email "zangchuanqi@bytedance.com"
```

**记住密码**

```shell
echo "[credential]" >> .git/config
echo "    helper = store" >> .git/config
#实际上将这两行添加到config文件里
vim .git/config
# add 
[credential]
    helper = store
```

##### 查看项目

*   git status
*   查看状态，有何改动
*   git log
*   查看版本，最新版本是哪个commit

##### 查看分支之间的不同

*   显示出所有有差异的文件列表
    *   git diff branch1 branch2 --stat
*   显示指定文件的详细差异
    *   git diff branch1 branch2 文件名(带路径)
*   显示出所有有差异的文件的详细差异
    *   git diff branch1 branch2

##### 提交项目

*   git add
    *   添加要提交的文件（被修改的）
*   git commit -m " 简要说明"
    *   提交文件到本地库
*   git push 分支
    *   将本地库push到远程库

```shell
 vim test1.py
 #修改文件
 git add test1.py
 #添加修改的文件，即将被commit
 git commit -m "test"
 #准备提交，并进行说明
 git push origin master
 #将本地库push到远程库master
 
 git push origin chuanqi:chuanqi_test
 #将commit(提交)从本地分支【chuanqi】 push(推送到)，远程分支  [chuanqi_test]
```

##### 操作分支

*   新建分支
    *   git branch 分支名
*   查看分支
    *   本地分支
        *   git branch
    *   远程分支
        *   git branch -r
*   切换分支
    *   git checkout 分支名
*   拉取分支
    1.  git fetch origin 远程分支名x:本地分支名x1
        
        ```
        使用该方式会在本地新建分支x，但是不会自动切换到该本地分支x，需要手动checkout
        ```
        
    2.  git checkout -b 本地分支名x origin/远程分支名x使用该方式会在本地新建分支x，并自动切换到该本地分支x

```shell
 #新建分支
 git branch chuanqi_casesfix
 #查看分支
 git branch
 git branch -r

 #切换本地分支
 git checkout chuanqi_casesfix
 #将远程分支拉到本地分支 base，并且切换到base
 git checkout origin/master -b base
```

**注意事项**：

1.  提交自己分支
2.  检查无误后合并到master上

##### 恢复命令

*   恢复单个文件修改
    *   git checkout -- file
*   取消已经暂存的文件。即，撤销先前"git add"的操作
    *   git reset HEAD file
*   修改最后一次提交。用于修改上一次的提交信息，或漏提交文件等情况
    *   git commit --amend
*   回退所有内容到上一个版本
    *   git reset HEAD^
*   回退a.py这个文件的版本到上一个版本
    *   git reset HEAD^ a.py
*   向前回退到第3个版本
    *   git reset –soft HEAD~3
*   将本地的状态回退到和远程的一样
    *   git reset –hard origin/master
*   回退到某个版本
    *   git reset 057d（commit的前几位）
*   回退到上一次提交的状态，按照某一次的commit完全反向的进行一次commit.(代码回滚到上个版本，并提交git)
    *   git revert HEAD

##### git删除远程文件夹或文件的方法

1.  预览将要删除的文件
    
    ```shell
    git rm -r -n --cached 文件/文件夹名称 
    
    加上 -n 这个参数，执行命令时，是不会删除任何文件，而是展示此命令要删除的文件列表预览。
    ```
    
2.  确定无误后删除文件
    
    ```shell
    git rm -r --cached 文件/文件夹名称
    ```
    
3.  提交到本地并推送到远程服务器
    
    ```shell
    git commit -m "提交说明"
    git push origin master
    ```
    

##### git 打补丁

*   diff/patchgit diff 【commit sha1 id】 【commit sha1 id】 > 【diff文件名】
    
    ```shell
    git  diff >patch.diff
    
    git apply --check 【path/to/xxx.diff】
    
    git apply 【path/to/xxx.diff】
    #or
    git  am 【path/to/xxx.patch】
    ```
    

##### git 打标签

*   显示已有标签
    
    ```shell
    git tag
    # -l 选项表示list，后边加想 查找的标签，可以使用正则表达式
    git tag -l 'v1.4.2.*'
    ```
    
*   新建标签主要分两种：轻量级的（lightweight）和含附注的（annotated）
    *   轻量级标签实际上就是一个保存着对应提交对象的校验和信息的文件。直接给名字就可以了。
        
        ```shell
        git tag v1.4-lw
        ```
        
    *   含附注类型的标签非常简单，用 `-a` （译注：取 `annotated` 的首字母）指定标签名字即可
    *   `-m` 选项则指定了对应的标签说明，Git 会将此说明一同保存在标签对象中
        
        ```shell
         git tag -a v1.4 -m 'my version 1.4'
        ```
        
    *   查看附注信息 git show查看相应标签的版本信息，并连同**显示打标签时的提交对象**
        
        ```shell
        git show v1.4
        tag v1.4
        Tagger: 
        Date:   Mon Feb 9 14:45:11 2009 -0800
        ```
        
    *   `-s`如果替换`-a`,则表示签署标签，有自己私钥
*   推送标签默认情况下，`git push` 并不会把标签传送到远端服务器上，只有通过显式命令才能分享标签到远端仓库。其命令格式如同推送分支，运行 `git push origin [tagname]`
    
    ```shell
    #推送所有标签
    git push origin --tags
    #推送单个标签
    git push origin v1.5
    ```
    
*   恢复标签内容直接使用`checkout`命令即可
    
    ```shell
    git checkout v1.5
    ```
    

> [https://blog.csdn.net/qq\_15437667/article/details/51029757](https://blog.csdn.net/qq_15437667/article/details/51029757)
> 
> 作者：yzpyzp [https://blog.csdn.net/yzpbright/article/details/54143129?utm\_source=copy](https://blog.csdn.net/yzpbright/article/details/54143129?utm_source=copy)
> 
> [https://blog.csdn.net/cankingapp/article/details/18312117](https://blog.csdn.net/cankingapp/article/details/18312117)
> 
> 打补丁 [https://juejin.im/post/5b5851976fb9a04f844ad0f4](https://juejin.im/post/5b5851976fb9a04f844ad0f4)
> 
> 廖雪峰 [https://www.liaoxuefeng.com/wiki/0013739516305929606dd18361248578c67b8067c8c017b000/0013758392816224cafd33c44b4451887cc941e6716805c000](https://www.liaoxuefeng.com/wiki/0013739516305929606dd18361248578c67b8067c8c017b000/0013758392816224cafd33c44b4451887cc941e6716805c000)
> 
> Git tag 命令 [https://git-scm.com/book/zh/v1/Git-%E5%9F%BA%E7%A1%80-%E6%89%93%E6%A0%87%E7%AD%BE](https://git-scm.com/book/zh/v1/Git-%E5%9F%BA%E7%A1%80-%E6%89%93%E6%A0%87%E7%AD%BE)