---
title: mac 使用记录
tags: []
id: '623'
categories:
  - - 日常扯淡
date: 2018-09-02 15:33:16
---

# MAC 使用记录--随用随更

#### 输入法

*   长按 caps lock 大写锁定
*   短按切换拼音输入
*   control + 空格 切换输入法

#### 删除键

*   第一种：按 delete 键，实现 Windows 键盘上退格键的功能，也就是删除光标之前的一个字符（默认）；
*   第二种：按 fn+delete 键，删除光标之后的一个字符；
*   第三种：按 option+delete 键，删除光标之前的一个单词（英文有效）；
*   第四种：按 command+delete 键，删除光标之前整行内容；
*   第五种：选中文件后按 command+delete，删除掉该文件。

#### 锁屏

*   ctrl + shift + 电源开关键

#### 复制粘贴

*   由 command 键 替换 linux 和windows的ctrl 键

#### 行首行尾

组合键：Option键+左箭头是Home键；+右箭头是End键。

而在之前的系统中可能使用Command键或者fn键+左/右箭头的组合。

#### 翻页键

fn + 上箭头

fn + 下箭头

#### 修改文件默认打开方式

选定某文件 command + i

#### 将terminal 配置成linux环境

**修改配置文件 .bash\_profile**

```shell
   export LS_OPTIONS='--color=auto' # 如果没有指定，则自动选择颜色
   export CLICOLOR='Yes' #是否输出颜色
   export LSCOLORS='CxfxcxdxbxegedabagGxGx' #指定颜色 
```

#### 安装macOS 缺失的软件包管理器 Homebrew

```shell
#install
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

> [https://brew.sh/index\_zh-cn.html](https://brew.sh/index_zh-cn.html)

#### 安装Linux使用的GNU Coreutils替换Mac的ls命令

> [http://linfan.info/blog/2012/02/27/colorful-terminal-in-mac/](http://linfan.info/blog/2012/02/27/colorful-terminal-in-mac/)

Coreutils提供了配置工具，定义颜色代码更加方便；

Coreutils包含的不仅仅是ls，同时作为Linux用户，我更习惯于使用GNU的各种shell工具。

Coreutils的安装与配置方法如下：

1.  通过[Homebrew](http://linfan.info/blog/2012/02/25/homebrew-installation-and-usage/)安装Coreutils `brew install xz coreutils` 注：Coreutils并不依赖于xz，但它的源码是用xz格式压缩的，安装xz才能解压。
    
2.  生成颜色定义文件 `gdircolors --print-database > ~/.dir_colors`
    
3.  在`~/.bash_profile`配置文件中加入以下代码
    
    ```shell
    if brew list  grep coreutils > /dev/null ; then
      PATH="$(brew --prefix coreutils)/libexec/gnubin:$PATH"
      alias ls='ls -F --show-control-chars --color=auto'
      eval `gdircolors -b $HOME/.dir_colors`
    fi
    ```
    
    gdircolor的作用就是设置ls命令使用的环境变量LS\_COLORS（BSD是LSCOLORS），我们可以修改~/.dir\_colors自定义文件的颜色，此文件中的注释已经包含各种颜色取值的说明。
    

看看默认颜色的显示效果。 ![ls screenshot](http://linfan.info/blog/images/2012-02-27-colorful-terminal-in-mac_ls.png)

**grep高亮显示关键字**

这个很简单，加上`--color`参数就可以了，为了使用方便，可以在`~/.bash_profile`配置文件中加上alias定义。

```shell
alias grep='grep --color'
alias egrep='egrep --color'
alias fgrep='fgrep --color'
```

**Vim语法高亮**

在Vim中输入命令`:syntax on`激活语法高亮，若需要Vim启动时自动激活，在`~/.vimrc`中添加一行`syntax on`即可。

```shell
  colorscheme default     " 设置颜色主题
   
  syntax on               " 语法高亮
  
  filetype on             " 检测文件的类型
  
  set number              " 显示行号
  "set cursorline          " 用浅色高亮当前行
  "autocmd InsertLeave * se nocul
  "autocmd InsertEnter * se cul
  
  set ruler               " 在编辑过程中，在右下角显示光标位置的状态行
  set laststatus=2        " 显示状态栏 (默认值为 1, 无法显示状态栏)
  set statusline=\ %<%F[%1*%M%*%n%R%H]%=\ %y\ %0(%{&fileformat}\ %{&encoding}\ %c:%l/%L%)\
                          " 设置在状态行显示的信息
  
  set tabstop=4           " Tab键的宽度
  set softtabstop=4
  set shiftwidth=4        " 统一缩进为4
  
  set autoindent          " vim使用自动对齐，也就是把当前行的对齐格式应用到下一行(自动缩进)
  set cindent             " (cindent是特别针对 C语言语法自动缩进)
  set smartindent         " 依据上面的对齐格式，智能的选择对齐方式，对于类似C语言编写上有用
  
  set scrolloff=3         " 光标移动到buffer的顶部和底部时保持3行距离
  
  set incsearch           " 输入搜索内容时就显示搜索结果
  set hlsearch            " 搜索时高亮显示被找到的文本
  
  set foldmethod=indent   " 设置缩进折叠
  set foldlevel=99        " 设置折叠层数
  nnoremap <space> @=((foldclosed(line('.')) < 0) ? 'zc' : 'zo')<CR>
                          " 用空格键来开关折叠
  
  " 自动跳转到上次退出的位置
  if has("autocmd")
      au BufReadPost * if line("'\"") > 1 && line("'\"") <= line("$")  exe "normal! g'\""  endif
  endif
```