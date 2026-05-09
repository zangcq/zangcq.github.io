---
title: "C/C++　main function parameter"
date: 2017-08-07 22:27:45
categories: ["C/C++"]
tags: ["C/C++"]
permalink: "/2017/08/07/cc%e3%80%80main-function-parameter/"
legacy: true
toc: true
classes: wide
---


# Main 函数原型

C/C++ 中的main 函数，经常带有参数 argc，argv，如下：
```

    int main(int argc,char** argv)

    int main(int argc,char* argv[])

    int main(int argc, char* argv[], char* env[] )

```

# Main 函数参数

参数的作用：

`argc` 命令行输入参数的个数（以空白符为分隔）

`argv` 存储了所有命令行参数，以 `NULL` 结束

`env` 环境变量，以 `NULL` 结束

eg

运行 hello 如下：
```

    hello sduer 1

```

那么 argc = 3 argv[] 中 则存储了 "hello.exe" "sduer" "1"这三个字符串 env[] 中存储了系统的环境变量
```

        #include <stdio.h>

        int main(int argc, char ** argv)
        {
            int i;
            for (i=0; i < argc; i++)
                printf("Argument %d is %s.\n", i, argv[i]);
        	for(i = 0; env[i] != NULL; i++)
    	    {
            printf("env[%d]=%s\n",i,env[i]);
    	    }
            return 0;
        }

```

terminal 运行情况如下
```

    ~$ ./hello sduer 1
    Argument 0 is ./hello.
    Argument 1 is sduer.
    Argument 2 is 1.
    env[0]=LC_PAPER=zh_CN.UTF-8
    env[1]=XDG_VTNR=2
    env[2]=LC_ADDRESS=zh_CN.UTF-8
    env[3]=SSH_AGENT_PID=1912
    env[4]=XDG_SESSION_ID=3
    env[5]=CLUTTER_IM_MODULE=xim
    env[6]=LC_MONETARY=zh_CN.UTF-8
    ....

```

# Main 函数 返回值

main函数的返回值是返回给父进程的，父进程调用以下函数来获取子进程的退出码（即main函数的返回值）
```

    pid_t wait(int* status);
    pid_t waitpid(pid_t pid, int* status, int option);

    #include <stdio.h>

    int main(int argc, char* argv[])
    {
        printf("Hello World!\n");
        return 100;
    }

```

在bash在，执行一个命令后（bash里是父进程，命令是子进程），$?里存放的是这个命令的退出码 `./hellowrold ; echo $?`

运行結果： `Hello World!` `100`

# Main 函数不是第一个执行的函数
```

    #include <stdio.h>
    __attribute ((constructor)) void hello_init(void)
    {
        printf("%s\n",__func__);
        return;
    }
    __attribute ((destructor)) void hello_fini(void)
    {
        printf("%s\n",__func__);
        return;
    }
    int main(int argc, char* argv[])
    {
        printf("Hello World!\n");
        return 0;
    }

```

`//运行結果： hello_init Hello World! hello_fini`

后两小节 参考自 Hello World

> <https://blog.csdn.net/ooaven/article/details/6101409>
