---
title: Perl regex 快速入门
tags:
  - perl
id: '76'
categories:
  - - programming
    - Perl
  - - 程序人生
date: 2017-06-09 15:11:35
---

\[TOC\]

## Perl 正则表达式 快速入门

### Simple word matching

#### 简单的字符匹配

*   最简单的正则表达式就是一个字符，或者字符串的匹配。 举个例子：

```perl

    "Hello World" =~ /World/;  # matches
```

说明： 右边的 `World` 是一个正则表达式，双斜杠`//`作为分隔符 ，将正则表达式包含进去`/World/`，告诉perl 这是要匹配的内容。 中间的`=~`is the operator testing a regular expression match. 是联系字符串 和 正则表达式 的 运算符。 如果匹配的话，产生一个 真 值，否则 false 。 左边的 可以是变量，可以是常量，就是你要跟 正则表达式 来进行匹配的。 在这例子中，`World` 匹配`"Hello World"`中第二个单词，所以表达式返回 true。

*   除了 `=~`，还可用 `!~`表示逆向操作。
    
    ```perl
        print "It doesn't match\n" if "Hello World" !~ /World/;
    ```
    
*   正则表达式也可以用变量 替换
    
    ```perl
     $greeting = "World";
        print "It matches\n" if "Hello World" =~ /$greeting/;
    ```
    
*   如果 要与 `$_`匹配的话，`$_ =~`可以被省略
    
    ```perl
      $_ = "Hello World";
        print "It matches\n" if /World/;
    ```
    
*   `//` 分隔符可以用 `m` 进行改变
    
    ```perl
     "Hello World" =~ m!World!;   # matches, delimited by '!'
     "Hello World" =~ m{World};   # matches, note the matching '{}'
     "/usr/bin/perl" =~ m"/perl"; # matches after '/usr/bin',
                                     # '/' becomes an ordinary char
    ```
    
*   正则表达式必须完整的匹配 ，也就是说 右边是 左边的真子集。
    
    ```perl
    "Hello World" =~ /world/;  # doesn't match, case sensitive
    "Hello World" =~ /o W/;    # matches, ' ' is an ordinary char
    "Hello World" =~ /World /; # doesn't match, no ' ' at end
    ```
    
*   perl 总是匹配最先出现的字符
    
    ```perl
     "Hello World" =~ /o/;       # matches 'o' in 'Hello'
     "That hat is red" =~ /hat/; # matches 'hat' in 'That'
    ```
    

#### 元字符

*   不是所有的字符都可以作为 as is 来进行匹配，例如元字符。

```perl
   {}[]()^$.*+?\
```

代码

说明

在字符集可以代表

.

匹配除换行符以外的任意字符

\\w

匹配字母或数字或下划线或汉字

`[0-9a-zA-Z_]`

\\s

匹配任意的空白符

`[\ \t\r\n\f]`

\\d

匹配数字

`[0-9]`

\\b

匹配单词的开始或结束

^

匹配字符串的开始

$

匹配字符串的结束

*   当匹配元字符时 需要加反斜杠`\`,进行转义。
    
    ```Perl
    "2+2=4" =~ /2+2/;    # doesn't match, + is a metacharacter
    "2+2=4" =~ /2\+2/;   # matches, \+ is treated like an ordinary +
    'C:\WIN32' =~ /C:\\WIN/;                       # matches
    "/usr/bin/perl" =~ /\/usr\/bin\/perl/;  # matches
    ```
    
*   在正则表达式中也可以用转义序列 来匹配那些无法打印的 ASCII 字符。
    *   `\t` for tab
    *   `\n` for newline
    *   `\r` for a carriage return
    *   Arbitrary bytes are represented by octal escape sequences, e.g., `\033` ,
    *   hexadecimal escape sequences, e.g., `\x1B` :

```Perl
"1000\t2000" =~ m(0\t2)  # matches
"cat" =~ /\143\x61\x74/  # matches in ASCII, but 
                         # a weird way to spell cat
```

*   正则表达式大多是双引号内的字符串，所以变量也可以替换
    
    ```perl
      $foo = 'house';
      'cathouse' =~ /cat$foo/;   # matches
      'housecat' =~ /${foo}cat/; # matches
    ```
    
*   前边所有的正则表达式，都是匹配从任意位置开始，儿我们可以限定从开始，或者结尾进行匹配。
    
    *   The anchor `^` means match at the beginning of the string and the anchor
    *   `$` means match at the end of the string, or before a newline at the end of the string.
    *   `^`从字符串开始位置进行匹配
    *   `$`从字符串结束位置进行匹配，或者在 `/n`新行之前
    
    ```perl
        "housekeeper" =~ /keeper/;         # matches
        "housekeeper" =~ /^keeper/;        # doesn't match
        "housekeeper" =~ /keeper$/;        # matches
        "housekeeper\n" =~ /keeper$/;      # matches  ？\n 表示换行
        #这个匹配的原因就是 \n 表示换行，然后从字符串末尾进行匹配，\n不算在前边那个字符串里
        #默认情况下 $ 匹配字符串结尾，或字符尾部的一个\n前面。注意它只是个位置信息，不实际匹配任何字符
        "housekeeper" =~ /^housekeeper$/;  # matches
    ```
    
    ​

### 使用字符类 using character classes

*   字符类允许所有可能的字符集，不仅仅是单个字符来与正则表达式进行匹配字符类用中括号标记\[...\],字符集中所有字符都有匹配的可能。

```perl
    /cat/;            # matches 'cat'
    /[bcr]at/;        # matches 'bat', 'cat', or 'rat'
    "abc" =~ /[cab]/; # matches 'a'
```

说明：第三个，即使`c`是字符集里的第一个字符，但是根据最先匹配原则，与正则表达式匹配的是 `a`。 还有字符集之间可以自由组合

```perl

      /[yY][eE][sS]/; # match 'yes' in a case-insensitive way
                      # 'yes', 'Yes', 'YES', etc.
      /yes/i;         # also match 'yes' in a case-insensitive way
```

说明： 最后的例子中 `i` 表示 case-insensitive，换句话说，是不区分大小写。

*   字符集中既可以包含普通字符也可以有特殊字符，同样这些特殊字符`-]\^$`也需要转义。
    
    ```perl
       /[\]c]def/; # matches ']def' or 'cdef'
       $x = 'bcr';
       /[$x]at/;   # matches 'bat, 'cat', or 'rat'
       /[\$x]at/;  # matches '$at' or 'xat'
       /[\\$x]at/; # matches '\at', 'bat, 'cat', or 'ra
    ```
    
*   特殊字符`-`作为范围符号经常使用
    
    *   \[0-9\] 表示\[0123456789\]
    *   \[a-z\] 表示\[abc...xyz\]
    
    ```perl
        /item[0-9]/;  # matches 'item0' or ... or 'item9'
        /[0-9a-fA-F]/;  # matches a hexadecimal digit
    ```
    
    注意：如果`-`在第一位置或者最后的位置，把它当做普通字符使用。
*   特殊字符`^`在字符集中第一个位置，表示 非 或 取反的意思，否则的话，当做普通字符使用。
    
    ```perl
        /[^a]at/;  # doesn't match 'aat' or 'at', but matches
                   # all other 'bat', 'cat, '0at', '%at', etc.
        /[^0-9]/;  # matches a non-numeric character
        /[a^]at/;  # matches 'aat' or '^at'; here '^' is ordinary
    ```
    
*   反斜杠序列 Backslash sequences
    
    ```perl
     \d             #Match a decimal digit character.
     [0-9]
     \D             #Match a non-decimal-digit character.
     [^0-9]
     
     \w             #Match a "word" character.
     [0-9a-zA-Z_]
     \W             #Match a non-"word" character.
     [^0-9a-zA-Z_]
     
     \s             #Match a whitespace character.
     [\ \t\r\n\f]
     \S             #Match a non-whitespace character.
     [^/s]
     
     \h             #Match a horizontal whitespace character.
     \H             #Match a character that isn't horizontal whitespace.
     
     \v             #Match a vertical whitespace character.
     \V             #Match a character that isn't vertical whitespace.
     
     \N             #Match a character that isn't a newline.
     \pP, \p{Prop}  #Match a character that has the given Unicode property.
     \PP, \P{Prop}  #Match a character that doesn't have the Unicode property
    ```
    
    举个例子说明
    
    ```Perl
    
        /\d\d:\d\d:\d\d/; # matches a hh:mm:ss time format
        /[\d\s]/;         # matches any digit or whitespace character
        /\w\W\w/;         # matches a word char, followed by a
                          # non-word char, followed by a word char
        /..rt/;           # matches any two chars, followed by 'rt'
        /end\./;          # matches 'end.'
        /end[.]/;         # same thing, matches 'end.'
    ```
    
*   元字符`\b`，只匹配一个位置，不匹配字符，可以作为字符与非字符的边界`\w\W`或者`\W\w`。
    
    ```Perl
        $x = "Housecat catenates house and cat";
        $x =~ /\bcat/;  # matches cat in 'catenates'
        $x =~ /cat\b/;  # matches cat in 'housecat'
        $x =~ /\bcat\b/;  # matches 'cat' at end of string
    ```
    
*   对于自然语言的处理，经常使用 `\b{wb}`
    
    ```perl
    "don't" =~ / .+? \b{wb} /x;  # matches the whole string
    ```
    

### 或操作 Matching this or that

我们可以匹配不同的字符串 通过或操作符。例如 ​ 为了匹配 `cat`或者`dog`，我们可以把震泽表达式写成`catdog`。在之前，Perl 总将正则表达式 和字符串最早出现的可能的点进行匹配。 eg.

```perl

    "cats and dogs" =~ /catdogbird/;  # matches "cat"
    "cats and dogs" =~ /dogcatbird/;  # matches "cat"
```

说明： 尽管在第二个正则表达式中，dog 在 cat 之前，但是要匹配的字符串中，cat出现的最早，所以匹配cat。 eg.

```perl

    "cats"          =~ /ccacatcats/; # matches "c"
    "cats"          =~ /catscatcac/; # matches "cats"
```

原理同上，第一个允许正则表达式中`c`匹配成功，那么正则表达式匹配成功。像或操作一样，有一个为真，则整个为真。第二个，所有的都匹配，那么所以第一个匹配。 At a given character position, the first alternative that allows the regex match to succeed will be the one that matches. Here, all the alternatives match at the first string position, so the first matches.

### 分组与分层匹配

Grouping things and hierarchical matching 我们可以用`()`来进行分组，讲括号内的正则表达式的一部分。 eg.`house(catdog)`表示 house 后跟的不是cat，就是dog。

```perl

    /(ab)b/;    # matches 'ab' or 'bb'
    /(^ab)c/;   # matches 'ac' at start of string or 'bc' anywhere
    /house(cat)/;  # matches either 'housecat' or 'house'
    /house(cat(s))/;  # matches either 'housecats' or 'housecat' or
                        # 'house'.  Note groups can be nested.
                        # 分组可以嵌套
    "20" =~ /(1920)\d\d/;  # matches the null alternative '()\d\d',
                             # because '20\d\d' can't match
```

### 提取匹配 Extracting matches

我们也可以用`()` 提取已匹配的字符串的各个部分。对于每个分组，我们可以用特殊变量`$1`,`$2`来保存各个要提取的部分。

```perl

    # extract hours, minutes, seconds
    $time =~ /(\d\d):(\d\d):(\d\d)/;  # match hh:mm:ss format
    $hours = $1;
    $minutes = $2;
    $seconds = $3;
```

再这个正则表达式中，我们用括号将他们进行了分组，然后通过变量`$1`,`$2`,`$3`将他们提取出来。我们也可以改写成

```perl

    ($hours, $minutes, $second) = ($time =~ /(\d\d):(\d\d):(\d\d)/);
```

*   嵌套我们根据左括号进行排序，然后根据括号配对。
    
    ```perl
    
        /(ab(cdef)((gi)j))/;
         1  2      34
    ```
    
*   反向引用我们可通过反向引用 `\g1`,`\g2`, 将匹配的变量用在正则表达式内。
    
    ```perl
    
       /(\w\w\w)\s\g1/; # find sequences like 'the the' in string
    ```
    
    `$1`,`$2`,...主要用于正则表达式外部， `\g1`,`\g2`用于正则表达式。

### 重复匹配 Matching repetitions

*   常用限定符

代码/语法

说明

\*

重复0次或更多次

+

重复1次或更多次

?

重复0次或1次

{n}

重复n次

{n,}

重复n次或更多次

{n,m}

重复n到m次

eg.

*   `a?` = match 'a' 1 or 0 times
*   `a*` = match 'a' 0 or more times, i.e., any number of times
*   `a+` = match 'a' 1 or more times, i.e., at least once
*   `a{n,m}` = match at least `n` times, but not more than `m` times.
*   `a{n,}` = match at least `n` or more times
*   `a{n}` = match exactly `n` times

```perl

    $x = 'the cat in the hat';
    $x =~ /^(.*)(at)(.*)$/; # matches,
                            # $1 = 'the cat in the h'
                            # $2 = 'at'
                            # $3 = ''   (0 matches)
```

第一个`(.*)`匹配尽可能多的字符。 第二个`(.*)`只匹配了0次。

### 匹配多次 More matching

我们通常的匹配都是匹配一次，成功即返回，而还可以用`//g`匹配多次 eg

```perl

$var = "match match match";

while ($var =~ /match/g) { $a++; }
print "$a\n"; # prints 3

$a = 0;
$a++ foreach ($var =~ /match/g);
print "$a\n"; # prints 3
```

在标量上下文中，连续匹配多次需要用`//g`从一次匹配跳到另一次匹配，我们可以利用`pos()`设置位置，来定位追踪字符串的位置。 eg

```perl

    $x = "cat dog house"; # 3 words
    while ($x =~ /(\w+)/g) {
        print "Word is $1, ends at position ", pos $x, "\n";
    }
```

打印结果

```perl

    Word is cat, ends at position 3
    Word is dog, ends at position 7
    Word is house, ends at position 13
```

匹配失败或改变目标字符串会重置字符位置，如果你不想在匹配失败后让位置被重置，那么加上`//c`字符。 形如 `/regex/gc`。 在 list 上下文中，`//g`可以返回 分组的一个列表，如果没有分组的话，这个list 匹配整个正则表达式

```perl

    @words = ($x =~ /(\w+)/g);  # matches,
                                # $word[0] = 'cat'
                                # $word[1] = 'dog'
                                # $word[2] = 'house'
```

### 搜索和替换 Search and replace

查找和替换我们通过 `s/regex/replacement/modifiers`. replacement 是一个在Perl中双引号字符串，如果这个字符串匹配正则表达式，那么就用其替换。 我们依然使用`=~`来作为运算符。If matching against `$_` , the `$_ =~` can be dropped。如果匹配不成功，我们就将其丢弃掉。如果匹配成功，我们就将其替换，否则返回false。 eg

```perl

    $x = "Time to feed the cat!";
    $x =~ s/cat/hacker/;   # $x contains "Time to feed the hacker!"
    $y = "'quoted words'";
    $y =~ s/^'(.*)'$/$1/;  # strip single quotes,
       # $1 正好是分组获取的结果。即小括号的内容。
                           # $y contains "quoted words"
```

说明：With the `s///` operator, the matched variables `$1` , `$2` , etc. are immediately available for use in the replacement expression.匹配成功，立即生效

*   全部替换我们同样可以用`s///g`来进行多次替换，应该是全部替换。

eg

```perl

    $x = "I batted 4 for 4";
    $x =~ s/4/four/;   # $x contains "I batted four for 4"
    $x = "I batted 4 for 4";
    $x =~ s/4/four/g;  # $x contains "I batted four for four"
```

*   无损替换

我们可以使用`s///r`在进行替换时，返回替换的结果而不是被修改默认变量`$_` eg

```perl

    $x = "I like dogs.";
    $y = $x =~ s/dogs/cats/r;
    print "$x $y\n"; # prints "I like dogs. I like cats."
    #$x 没有被修改，结果不变，仅仅返回替换掉的结果，而不改变原来变量的值
    $x = "Cats are great.";
    print $x =~ s/Cats/Dogs/r =~ s/Dogs/Frogs/r =~
        s/Frogs/Hedgehogs/r, "\n";
    # prints "Hedgehogs are great."
    print $x
    # prints "Cats are great."
    
    @foo = map { s/[a-z]/X/r } qw(a b c 1 2 3);
    # @foo is now qw(X X X 1 2 3)
```

*   替换评估 再操作

我们用 `s///e`来实现一个评估`eval{...}`从替换的字符串和评估结果里进行打包，然后替换子串。 改变原来字符串的内容。 eg

```perl

    # reverse all the words in a string
    $x = "the cat in the hat";
    $x =~ s/(\w+)/reverse $1/ge;   # $x contains "eht tac ni eht tah"
        # convert percentage to decimal
    $x = "A 39% hit rate";
    $x =~ s!(\d+)%!$1/100!e;       # $x contains "A 0.39 hit rate"
```

### 分离字符 The split operator

`split /regex/，string`，将string 分离成一个l含有多个子串的list ，返回值是一个list。 eg

```perl

    $x = "Calvin and Hobbes";
    @word = split /\s+/, $x;  # $word[0] = 'Calvin'
                              # $word[1] = 'and'
                              # $word[2] = 'Hobbes'
```

或者将 ，一些数 进行分离 eg

```perl

    $x = "1.618,2.718,   3.142";
    @const = split /,\s*/, $x;  # $const[0] = '1.618'
                                # $const[1] = '2.718'
                                # $const[2] = '3.142'
```

如果字符串中包含`//`，我们要通过 m 修改替代 `//`， eg

```perl

    $x = "/usr/bin";
    @parts = split m!(/)!, $x;  # $parts[0] = ''
                                # $parts[1] = '/'
                                # $parts[2] = 'usr'
                                # $parts[3] = '/'
                                # $parts[4] = 'bin'
```

Since the first character of $x matched the regex, `split` prepended an empty initial element to the list.