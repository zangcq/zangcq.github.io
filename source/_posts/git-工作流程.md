---
title: git 工作流程 (转载)
tags: []
id: '798'
categories:
  - - 工欲善其事必先利其器
date: 2019-05-12 15:15:05
---

这里对常用的 git 工作流进行梳理和简化

#### 分支命名规则

*   git 仓库命名为 `origin`。
*   主分支为 `master` ，存放正式发布版本的代码。该分支上的代码可以随时部署到正式环境。
*   默认分支和开发分支为 `develop` ，存放日常工作的最新代码。
*   发布版本的分支命名为 `release/xxx`，其中 `xxx` 是对应的版本号。在这个分支上只进行 bugfix，并且当版本发布完成后，相应的分支上的修改就会合并到 `master` 和 `develop`，并将该分支删除。
*   发布版本的 tag 命名为 `vxxx` ，其中 `xxx` 是对应的版本号。
*   功能分支为 `feature/xxx` ，其中 `xxx` 是简明的功能点描述，由小写字母、数字和下划线构成。例如： `feature/ota` 或 `feature/remote_debug`。当功能成功发布后，相应的分支删除。
*   bug 修复分支为 `bugfix/xxx` ，其中 `xxx` 是简明的 bug 描述，由小写字母、数字和下划线构成，例如：`bugfix/data_mismatch` 。如果修复的是缺陷管理系统中已有的缺陷，则 `xxx` 的值为对应缺陷的唯一编号，如 `bugfix/442`。当缺陷已确认修复后，相应的分支删除。

#### 开发流程

1.  项目初始化
2.  开发者将相应的项目 `clone` 到本地并定期与远端保持更新

 git clone https://xxx.xxx/xxx.git  
 git checkout -b develop origin/develop

1.  准备进行开发工作之前，开发者基于最新的 `master` 或 `develop` 建立相应的分支

 git pull  
 git checkout -b feature/xxx develop

1.  开发者在本地分支上进行修改及 `commit`。
2.  到达一定程度后（建议每半天到一天，或者修改的代码数量达到一定程度后），将本地分支 `push` 到 `origin`。
3.  功能开发完成后，从 `origin` 获取最新的开发进度，进行合并，并 `push` 到 `origin`。 （这个步骤在团队规模扩大后变更为 PR ）

 # 切换到 develop 分支  
 git rebase develop  
 ​  
 # https://www.git-tower.com/learn/git/ebook/cn/command-line/advanced-topics/rebase  
 # 如果有冲突则手动合并  
 git mergetool  
 git rebase --continue  
 ​  
 # 获取最新进度  
 git pull origin develop  
 ​  
 # 合并分支  
 git merge feature/xxx  
 ​  
 # 推送到远端  
 git push  
 ​  
 # 删除本地分支  
 git branch -d feature/xxx

1.  发布版本

 git checkout -b release/0.0.1 develop  
 ​  
 # 这里可能会有 bugfix  
 ​  
 # 将 release 合并到 master 。这里一定是没有冲突的。  
 git checkout master  
 git merge release/0.0.1  
 git push  
 ​  
 # 将 release 合并到 develop  
 git checkout develop  
 git merge release/0.0.1  
 git push  
 ​  
 # 在 master 上打版本的 tag  
 git tag -a v0.0.1 -m "0.0.1 版本" master  
 git push --tags

1.  bugfix 分支

 # 建立 bugfix 分支  
 git checkout -b bugfix/001 release/0.0.1(或其他相应有缺陷的分支)  
 ​  
 # 修改和 commit 略过  
 ​  
 # 合并到有缺陷的分支  
 git checkout release/0.0.1  
 git merge bugfix/001  
 git push

#### 关于 commit message

对 commit message 提出下面的要求：

*   Summary 需要能看出来简单的内容，不能简单写成 `bugfix` 或者 `日常修改` 之类。如果有未解决的问题则需要使用 `[未完成]` 等标注清楚。
*   Descriptions 可以不写，如果写就一定要写清楚。

commit message 建议遵循如下规范：

 type: subject \[tag\]  
 <br>  
 body

其中 `type` 的取值和 `subject` 的建议写法为：

*   `feature` 表明新功能，例如： `feature: 保存日志`
*   `bugfix` 表明对缺陷的修改，例如： `bugfix: #001, #002`
*   `docs` 表明修改文档，例如： `docs: 补充安装说明`
*   `refactor` 表明进行代码重构，例如： `refactor: 调整了 chart.state 的结构`
*   `perf` 表明进行了优化，例如： `perf: 日志内容改为每秒刷新一次`
*   `build` 表明修改了构建工具，例如： `build: 升级到 webpack4`
*   `revert` 表明用于撤销之前的某次 `commit` ，需要注明具体是哪一个，例如： `revert: 撤销了 8cef3a 尝试修改死机问题`
*   `style` 表明样式的修改，例如： `style: 首页导航栏现在更有动感`
*   `ci` 表明涉及到持续集成工具的修改，例如： `ci: 加入 jenkins 的配置`
*   `test` 表明测试用例的修改，例如： `test: 增加对 FileUtils 的几个单元测试`
*   `chore` 表明修改了其他的不影响业务的东西

如果一个 `commit` 对应修改了多个缺陷，则在 `body` 中具体描述，例如：

 fixed #13175 【管理端】【采购订单】修改采购订单页面，修改供应商后，保存报错  
 fixed #446 总是死机的问题

#### 版本更新日志

*   版本更新日志应当手动维护
*   版本更新日志应当命名为 `CHANGELOG.md`
*   类型包括： `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed` 和 `Security`。

#### 参考文档

*   [有关 git 的学习资料 by xirong](https://github.com/xirong/my-git/blob/master/git-workflow-tutorial.md)
*   [Git 使用规范流程 by 阮一峰](http://www.ruanyifeng.com/blog/2015/08/git-use-process.html)
*   [Git流程及规范 by 77irclout](https://github.com/77ircloud/FET/wiki/Git%E6%B5%81%E7%A8%8B%E5%8F%8A%E8%A7%84%E8%8C%83)
*   [git 团队开发流程规范 by 醒着的码者](https://www.jianshu.com/p/9801b98c1de4)
*   [如何维护更新日志](https://keepachangelog.com/zh-CN/1.0.0/)