---
title: "git commit 合并信息"
date: 2021-06-25 15:30:31
categories: ["程序人生"]
permalink: "/2021/06/25/git-commit-%e5%90%88%e5%b9%b6%e4%bf%a1%e6%81%af/"
legacy: true
toc: true
classes: wide
---

<https://segmentfault.com/a/1190000007748862>

合并最近两个commits
```
 
    git rebase -i HEAD~2
```

1\. 执行了rebase命令之后，会弹出一个窗口，头几行如下：
```
 
    pick 3ca6ec3   'msg0'
    pick 1b40566   'msg1'
```

2.将pick改为squash或者s,之后保存并关闭文本编辑窗口即可。改完之后文本内容如下：
```
 
    pick 3ca6ec3   'msg0'
    s 1b40566      'msg1'
```

3\. 保存并退出，如果没有冲突，进入下一个弹窗，修改commit massage
```
 
    # commit message 
    msg0 
    msg1
```

4\. 保存退出即可。
