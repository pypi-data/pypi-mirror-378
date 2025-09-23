/*! For license information please see f009ff5c2c2d274bec05.chunk.js.LICENSE.txt */
(globalThis.webpackChunksuperset=globalThis.webpackChunksuperset||[]).push([[4779],{7452:e=>{var t=function(e){"use strict";var t,r=Object.prototype,n=r.hasOwnProperty,o=Object.defineProperty||function(e,t,r){e[t]=r.value},i="function"==typeof Symbol?Symbol:{},l=i.iterator||"@@iterator",a=i.asyncIterator||"@@asyncIterator",s=i.toStringTag||"@@toStringTag";function c(e,t,r){return Object.defineProperty(e,t,{value:r,enumerable:!0,configurable:!0,writable:!0}),e[t]}try{c({},"")}catch(e){c=function(e,t,r){return e[t]=r}}function u(e,t,r,n){var i=t&&t.prototype instanceof y?t:y,l=Object.create(i.prototype),a=new Y(n||[]);return o(l,"_invoke",{value:E(e,r,a)}),l}function d(e,t,r){try{return{type:"normal",arg:e.call(t,r)}}catch(e){return{type:"throw",arg:e}}}e.wrap=u;var h="suspendedStart",p="suspendedYield",g="executing",f="completed",m={};function y(){}function v(){}function b(){}var w={};c(w,l,(function(){return this}));var S=Object.getPrototypeOf,k=S&&S(S(I([])));k&&k!==r&&n.call(k,l)&&(w=k);var C=b.prototype=y.prototype=Object.create(w);function x(e){["next","throw","return"].forEach((function(t){c(e,t,(function(e){return this._invoke(t,e)}))}))}function A(e,t){function r(o,i,l,a){var s=d(e[o],e,i);if("throw"!==s.type){var c=s.arg,u=c.value;return u&&"object"==typeof u&&n.call(u,"__await")?t.resolve(u.__await).then((function(e){r("next",e,l,a)}),(function(e){r("throw",e,l,a)})):t.resolve(u).then((function(e){c.value=e,l(c)}),(function(e){return r("throw",e,l,a)}))}a(s.arg)}var i;o(this,"_invoke",{value:function(e,n){function o(){return new t((function(t,o){r(e,n,t,o)}))}return i=i?i.then(o,o):o()}})}function E(e,r,n){var o=h;return function(i,l){if(o===g)throw new Error("Generator is already running");if(o===f){if("throw"===i)throw l;return{value:t,done:!0}}for(n.method=i,n.arg=l;;){var a=n.delegate;if(a){var s=N(a,n);if(s){if(s===m)continue;return s}}if("next"===n.method)n.sent=n._sent=n.arg;else if("throw"===n.method){if(o===h)throw o=f,n.arg;n.dispatchException(n.arg)}else"return"===n.method&&n.abrupt("return",n.arg);o=g;var c=d(e,r,n);if("normal"===c.type){if(o=n.done?f:p,c.arg===m)continue;return{value:c.arg,done:n.done}}"throw"===c.type&&(o=f,n.method="throw",n.arg=c.arg)}}}function N(e,r){var n=r.method,o=e.iterator[n];if(o===t)return r.delegate=null,"throw"===n&&e.iterator.return&&(r.method="return",r.arg=t,N(e,r),"throw"===r.method)||"return"!==n&&(r.method="throw",r.arg=new TypeError("The iterator does not provide a '"+n+"' method")),m;var i=d(o,e.iterator,r.arg);if("throw"===i.type)return r.method="throw",r.arg=i.arg,r.delegate=null,m;var l=i.arg;return l?l.done?(r[e.resultName]=l.value,r.next=e.nextLoc,"return"!==r.method&&(r.method="next",r.arg=t),r.delegate=null,m):l:(r.method="throw",r.arg=new TypeError("iterator result is not an object"),r.delegate=null,m)}function O(e){var t={tryLoc:e[0]};1 in e&&(t.catchLoc=e[1]),2 in e&&(t.finallyLoc=e[2],t.afterLoc=e[3]),this.tryEntries.push(t)}function T(e){var t=e.completion||{};t.type="normal",delete t.arg,e.completion=t}function Y(e){this.tryEntries=[{tryLoc:"root"}],e.forEach(O,this),this.reset(!0)}function I(e){if(null!=e){var r=e[l];if(r)return r.call(e);if("function"==typeof e.next)return e;if(!isNaN(e.length)){var o=-1,i=function r(){for(;++o<e.length;)if(n.call(e,o))return r.value=e[o],r.done=!1,r;return r.value=t,r.done=!0,r};return i.next=i}}throw new TypeError(typeof e+" is not iterable")}return v.prototype=b,o(C,"constructor",{value:b,configurable:!0}),o(b,"constructor",{value:v,configurable:!0}),v.displayName=c(b,s,"GeneratorFunction"),e.isGeneratorFunction=function(e){var t="function"==typeof e&&e.constructor;return!!t&&(t===v||"GeneratorFunction"===(t.displayName||t.name))},e.mark=function(e){return Object.setPrototypeOf?Object.setPrototypeOf(e,b):(e.__proto__=b,c(e,s,"GeneratorFunction")),e.prototype=Object.create(C),e},e.awrap=function(e){return{__await:e}},x(A.prototype),c(A.prototype,a,(function(){return this})),e.AsyncIterator=A,e.async=function(t,r,n,o,i){void 0===i&&(i=Promise);var l=new A(u(t,r,n,o),i);return e.isGeneratorFunction(r)?l:l.next().then((function(e){return e.done?e.value:l.next()}))},x(C),c(C,s,"Generator"),c(C,l,(function(){return this})),c(C,"toString",(function(){return"[object Generator]"})),e.keys=function(e){var t=Object(e),r=[];for(var n in t)r.push(n);return r.reverse(),function e(){for(;r.length;){var n=r.pop();if(n in t)return e.value=n,e.done=!1,e}return e.done=!0,e}},e.values=I,Y.prototype={constructor:Y,reset:function(e){if(this.prev=0,this.next=0,this.sent=this._sent=t,this.done=!1,this.delegate=null,this.method="next",this.arg=t,this.tryEntries.forEach(T),!e)for(var r in this)"t"===r.charAt(0)&&n.call(this,r)&&!isNaN(+r.slice(1))&&(this[r]=t)},stop:function(){this.done=!0;var e=this.tryEntries[0].completion;if("throw"===e.type)throw e.arg;return this.rval},dispatchException:function(e){if(this.done)throw e;var r=this;function o(n,o){return a.type="throw",a.arg=e,r.next=n,o&&(r.method="next",r.arg=t),!!o}for(var i=this.tryEntries.length-1;i>=0;--i){var l=this.tryEntries[i],a=l.completion;if("root"===l.tryLoc)return o("end");if(l.tryLoc<=this.prev){var s=n.call(l,"catchLoc"),c=n.call(l,"finallyLoc");if(s&&c){if(this.prev<l.catchLoc)return o(l.catchLoc,!0);if(this.prev<l.finallyLoc)return o(l.finallyLoc)}else if(s){if(this.prev<l.catchLoc)return o(l.catchLoc,!0)}else{if(!c)throw new Error("try statement without catch or finally");if(this.prev<l.finallyLoc)return o(l.finallyLoc)}}}},abrupt:function(e,t){for(var r=this.tryEntries.length-1;r>=0;--r){var o=this.tryEntries[r];if(o.tryLoc<=this.prev&&n.call(o,"finallyLoc")&&this.prev<o.finallyLoc){var i=o;break}}i&&("break"===e||"continue"===e)&&i.tryLoc<=t&&t<=i.finallyLoc&&(i=null);var l=i?i.completion:{};return l.type=e,l.arg=t,i?(this.method="next",this.next=i.finallyLoc,m):this.complete(l)},complete:function(e,t){if("throw"===e.type)throw e.arg;return"break"===e.type||"continue"===e.type?this.next=e.arg:"return"===e.type?(this.rval=this.arg=e.arg,this.method="return",this.next="end"):"normal"===e.type&&t&&(this.next=t),m},finish:function(e){for(var t=this.tryEntries.length-1;t>=0;--t){var r=this.tryEntries[t];if(r.finallyLoc===e)return this.complete(r.completion,r.afterLoc),T(r),m}},catch:function(e){for(var t=this.tryEntries.length-1;t>=0;--t){var r=this.tryEntries[t];if(r.tryLoc===e){var n=r.completion;if("throw"===n.type){var o=n.arg;T(r)}return o}}throw new Error("illegal catch attempt")},delegateYield:function(e,r,n){return this.delegate={iterator:I(e),resultName:r,nextLoc:n},"next"===this.method&&(this.arg=t),m}},e}(e.exports);try{regeneratorRuntime=t}catch(e){"object"==typeof globalThis?globalThis.regeneratorRuntime=t:Function("r","regeneratorRuntime = r")(t)}},35697:(e,t,r)=>{var n=r(75972).k5;e.exports.X=function(e){return n({tag:"svg",attr:{viewBox:"0 0 320 512"},child:[{tag:"path",attr:{d:"M279 224H41c-21.4 0-32.1-25.9-17-41L143 64c9.4-9.4 24.6-9.4 33.9 0l119 119c15.2 15.1 4.5 41-16.9 41z"}}]})(e)}},51545:(e,t,r)=>{"use strict";r.d(t,{Ht:()=>a,cG:()=>i});var n=r(70731),o=r.n(n);const i={CASE_SENSITIVE_EQUAL:7,EQUAL:6,STARTS_WITH:5,WORD_STARTS_WITH:4,CONTAINS:3,ACRONYM:2,MATCHES:1,NO_MATCH:0},l=(e,t)=>String(e.rankedValue).localeCompare(String(t.rankedValue));function a(e,t,r){void 0===r&&(r={});const{keys:n,threshold:o=i.MATCHES,baseSort:a=l,sorter:u=e=>e.sort(((e,t)=>c(e,t,a)))}=r,h=e.reduce((function(e,l,a){const c=function(e,t,r,n){if(!t)return{rankedValue:e,rank:s(e,r,n),keyIndex:-1,keyThreshold:n.threshold};const o=function(e,t){const r=[];for(let n=0,o=t.length;n<o;n++){const o=t[n],i=p(o),l=d(e,o);for(let e=0,t=l.length;e<t;e++)r.push({itemValue:l[e],attributes:i})}return r}(e,t);return o.reduce(((e,t,o)=>{let{rank:l,rankedValue:a,keyIndex:c,keyThreshold:u}=e,{itemValue:d,attributes:h}=t,p=s(d,r,n),g=a;const{minRanking:f,maxRanking:m,threshold:y}=h;return p<f&&p>=i.MATCHES?p=f:p>m&&(p=m),p>l&&(l=p,c=o,u=y,g=d),{rankedValue:g,rank:l,keyIndex:c,keyThreshold:u}}),{rankedValue:e,rank:i.NO_MATCH,keyIndex:-1,keyThreshold:n.threshold})}(l,n,t,r),{rank:u,keyThreshold:h=o}=c;return u>=h&&e.push({...c,item:l,index:a}),e}),[]);return u(h).map((e=>{let{item:t}=e;return t}))}function s(e,t,r){return e=u(e,r),(t=u(t,r)).length>e.length?i.NO_MATCH:e===t?i.CASE_SENSITIVE_EQUAL:(e=e.toLowerCase())===(t=t.toLowerCase())?i.EQUAL:e.startsWith(t)?i.STARTS_WITH:e.includes(` ${t}`)?i.WORD_STARTS_WITH:e.includes(t)?i.CONTAINS:1===t.length?i.NO_MATCH:function(e){let t="";return e.split(" ").forEach((e=>{e.split("-").forEach((e=>{t+=e.substr(0,1)}))})),t}(e).includes(t)?i.ACRONYM:function(e,t){let r=0,n=0;function o(e,t,n){for(let o=n,i=t.length;o<i;o++)if(t[o]===e)return r+=1,o+1;return-1}const l=o(t[0],e,0);if(l<0)return i.NO_MATCH;n=l;for(let r=1,l=t.length;r<l;r++)if(n=o(t[r],e,n),!(n>-1))return i.NO_MATCH;return function(e){const n=1/e,o=r/t.length;return i.MATCHES+o*n}(n-l)}(e,t)}function c(e,t,r){const{rank:n,keyIndex:o}=e,{rank:i,keyIndex:l}=t;return n===i?o===l?r(e,t):o<l?-1:1:n>i?-1:1}function u(e,t){let{keepDiacritics:r}=t;return e=`${e}`,r||(e=o()(e)),e}function d(e,t){let r;if("object"==typeof t&&(t=t.key),"function"==typeof t)r=t(e);else if(null==e)r=null;else if(Object.hasOwnProperty.call(e,t))r=e[t];else{if(t.includes("."))return function(e,t){const r=e.split(".");let n=[t];for(let e=0,t=r.length;e<t;e++){const t=r[e];let o=[];for(let e=0,r=n.length;e<r;e++){const r=n[e];if(null!=r)if(Object.hasOwnProperty.call(r,t)){const e=r[t];null!=e&&o.push(e)}else"*"===t&&(o=o.concat(r))}n=o}return Array.isArray(n[0])?[].concat(...n):n}(t,e);r=null}return null==r?[]:Array.isArray(r)?r:[String(r)]}a.rankings=i;const h={maxRanking:1/0,minRanking:-1/0};function p(e){return"string"==typeof e?h:{...h,...e}}},64779:(e,t,r)=>{"use strict";r.r(t),r.d(t,{default:()=>Ee});var n=r(2404),o=r.n(n),i=r(38221),l=r.n(i),a=r(62193),s=r.n(a),c=r(2445),u=r(96540),d=r(21671),h=r(61573),p=r(69856),g=r(77796),f=r(35697),m=r(46942),y=r.n(m),v=r(7683),b=r(74098),w=r(17437),S=r(58083),k=r(50290),C=r(31463),x=r(90924),A=r(95021),E=r(28392),N=r(17355),O=r(36492),T=r(28827),Y=r(95018),I=r(26067),M=r(13341),P=r(14103),$=r(39822),F=r(35709),L=r(29248),R=r(96254),z=r(85173),H=r(67413),D=r(32885),B=r(51545);r(7452);const j=new Map;function U({count:e,value:t,onChange:r,onBlur:n,inputRef:o}){return(0,c.FD)(E.A,{direction:"horizontal",size:4,className:"dt-global-filter",children:["Search",(0,c.Y)(N.A,{size:"small",ref:o,placeholder:`${e} records...`,value:t,onChange:r,onBlur:n,className:"form-control input-sm"})]})}const G=(0,u.memo)((function({preGlobalFilteredRows:e,filterValue:t="",searchInput:r,setGlobalFilter:n,id:o="",serverPagination:i,rowCount:l}){const a=i?l:e.length,s=(0,u.useRef)(null),[d,h]=function(e,t,r=200){const[n,o]=(0,u.useState)(e),i=(0,u.useRef)(e),l=(0,D.useAsyncDebounce)(t,r);return i.current!==e&&(i.current=e,n!==e&&o(e)),[n,e=>{o(e),l(e)}]}(t,(e=>{n(e||void 0)}),200);(0,u.useEffect)((()=>{var e;i&&j.get(o)&&document.activeElement!==s.current&&(null==(e=s.current)||e.focus())}),[d,i]);const p=r||U;return(0,c.Y)(p,{count:a,value:d,inputRef:s,onChange:e=>{const t=e.target;e.preventDefault(),j.set(o,!0),h(t.value)},onBlur:()=>{j.set(o,!1)}})}));var _=r(20259);function W({current:e,options:t,onChange:r}){const{Option:n}=O.A;return(0,c.FD)("span",{className:"dt-select-page-size form-inline",children:[(0,b.t)("Show")," ",(0,c.Y)(O.A,{value:e,onChange:e=>r(e),size:"small",css:e=>w.AH`
          width: ${18*e.sizeUnit}px;
        `,children:t.map((e=>{const[t,r]=Array.isArray(e)?e:[e,e],o=0===t?(0,b.t)("all"):t;return(0,c.Y)(n,{value:Number(t),"aria-label":(0,b.t)("Show %s entries",o),children:r},t)}))})," ",(0,b.t)("entries")]})}function V(e){return Array.isArray(e)?e[0]:e}const X=(0,u.memo)((function({total:e,options:t,current:r,selectRenderer:n,onChange:o}){const i=t.map(V);let l=[...t];void 0===r||r===e&&i.includes(0)||i.includes(r)||(l=[...t],l.splice(i.findIndex((e=>e>r)),0,(0,_.u)([r])[0]));const a=void 0===r?i[0]:r,s=n||W;return(0,c.Y)(s,{current:a,options:l,onChange:o})})),K=(0,u.memo)((0,u.forwardRef)((function({style:e,pageCount:t,currentPage:r=0,maxPageItemCount:n=9,onPageChange:o},i){const l=function(e,t,r){if(r<7)throw new Error("Must allow at least 7 page items");if(r%2==0)throw new Error("Must allow odd number of page items");if(e<r)return[...new Array(e).keys()];const n=Math.max(0,Math.min(e-r,t-Math.floor(r/2))),o=new Array(r);for(let e=0;e<r;e+=1)o[e]=e+n;"number"==typeof o[0]&&o[0]>0&&(o[0]=0,o[1]="prev-more");const i=o[o.length-1];return"number"==typeof i&&i<e-1&&(o[o.length-1]=e-1,o[o.length-2]="next-more"),o}(t,r,n);return(0,c.Y)("div",{ref:i,className:"dt-pagination",style:e,children:(0,c.Y)("ul",{className:"pagination pagination-sm",children:l.map((e=>"number"==typeof e?(0,c.Y)("li",{className:r===e?"active":void 0,children:(0,c.Y)("a",{href:`#page-${e}`,role:"button",onClick:t=>{t.preventDefault(),o(e)},children:e+1})},e):(0,c.Y)("li",{className:"dt-pagination-ellipsis",children:(0,c.Y)("span",{children:"…"})},e)))})})})));let Q;const Z=e=>e.join("\n");function J(e=!1){if("undefined"==typeof document)return 0;if(void 0===Q||e){const e=document.createElement("div"),t=document.createElement("div");e.style.cssText=Z`
      width: auto;
      height: 100%;
      overflow: scroll;
    `,t.style.cssText=Z`
      position: absolute;
      visibility: hidden;
      overflow: hidden;
      width: 100px;
      height: 50px;
    `,t.append(e),document.body.append(t),Q=t.clientWidth-e.clientWidth,t.remove()}return Q}var q;!function(e){e.Init="init",e.SetStickyState="setStickyState"}(q||(q={}));const ee=(e,t)=>e+t,te=(e,t)=>({style:{...e.props.style,...t}}),re={tableLayout:"fixed"};function ne({sticky:e={},width:t,height:r,children:n,setStickyState:o}){if(!n||"table"!==n.type)throw new Error("<StickyWrap> must have only one <table> element as child");let i,l,a;if(u.Children.forEach(n.props.children,(e=>{e&&("thead"===e.type?i=e:"tbody"===e.type?l=e:"tfoot"===e.type&&(a=e))})),!i||!l)throw new Error("<table> in <StickyWrap> must contain both thead and tbody.");const s=(0,u.useMemo)((()=>{var e;return u.Children.toArray(null==(e=i)?void 0:e.props.children).pop().props.children.length}),[i]),d=(0,u.useRef)(null),h=(0,u.useRef)(null),p=(0,u.useRef)(null),g=(0,u.useRef)(null),f=(0,u.useRef)(null),m=J(),{bodyHeight:y,columnWidths:v}=e,b=!v||e.width!==t||e.height!==r||e.setStickyState!==o;let w,S,k,C;if((0,u.useLayoutEffect)((()=>{var e,n;if(!d.current)return;const i=d.current,l=i.clientHeight,a=h.current?h.current.clientHeight:0;if(!l)return;const s=i.parentNode.clientHeight,c=null==(e=i.childNodes)?void 0:e[(null==(n=i.childNodes)?void 0:n.length)-1||0].childNodes,u=Array.from(c).map((e=>{var t;return(null==(t=e.getBoundingClientRect())?void 0:t.width)||e.clientWidth})),[p,g]=function({width:e,height:t,innerHeight:r,innerWidth:n,scrollBarSize:o}){const i=r>t;return[i,n>e-(i?o:0)]}({width:t,height:r-l-a,innerHeight:s,innerWidth:u.reduce(ee),scrollBarSize:m}),f=Math.min(r,g?s+m:s);o({hasVerticalScroll:p,hasHorizontalScroll:g,setStickyState:o,width:t,height:r,realHeight:f,tableHeight:s,bodyHeight:f-l-a,columnWidths:u})}),[t,r,o,m]),b){const e=(0,u.cloneElement)(i,{ref:d}),t=a&&(0,u.cloneElement)(a,{ref:h});w=(0,c.Y)("div",{style:{height:r,overflow:"auto",visibility:"hidden",scrollbarGutter:"stable"},role:"presentation",children:(0,u.cloneElement)(n,{role:"presentation"},e,l,t)},"sizer")}const x=null==v?void 0:v.slice(0,s);if(x&&y){const t=(0,c.Y)("colgroup",{children:x.map(((e,t)=>(0,c.Y)("col",{width:e},t)))});S=(0,c.FD)("div",{ref:p,style:{overflow:"hidden",scrollbarGutter:"stable"},role:"presentation",children:[(0,u.cloneElement)((0,u.cloneElement)(n,{role:"presentation"}),te(n,re),t,i),S]},"header"),k=a&&(0,c.FD)("div",{ref:g,style:{overflow:"hidden",scrollbarGutter:"stable"},role:"presentation",children:[(0,u.cloneElement)((0,u.cloneElement)(n,{role:"presentation"}),te(n,re),t,a),k]},"footer");const r=e=>{p.current&&(p.current.scrollLeft=e.currentTarget.scrollLeft),g.current&&(g.current.scrollLeft=e.currentTarget.scrollLeft)};C=(0,c.Y)("div",{ref:f,style:{height:y,overflow:"auto",scrollbarGutter:"stable"},onScroll:e.hasHorizontalScroll?r:void 0,role:"presentation",children:(0,u.cloneElement)((0,u.cloneElement)(n,{role:"presentation"}),te(n,re),t,l)},"body")}return(0,c.FD)("div",{style:{width:t,height:e.realHeight||r,overflow:"hidden"},role:"table",children:[S,C,k,w]})}function oe(e){const{dispatch:t,state:{sticky:r},data:n,page:o,rows:i,allColumns:l,getTableSize:a=()=>{}}=e,s=(0,u.useCallback)((e=>{t({type:q.SetStickyState,size:e})}),[t,a,o,i]);Object.assign(e,{setStickyState:s,wrapStickyTable:e=>{const{width:t,height:d}=function(e,t){const r=(0,u.useRef)();return(0,u.useLayoutEffect)((()=>{r.current=e})),(0,u.useMemo)((()=>{if(r.current)return e()}),[r.current,r.current===e,...t||[]])}(a,[a])||r,h=(0,u.useMemo)(e,[o,i,l]);return(0,u.useLayoutEffect)((()=>{t&&d||s()}),[t,d]),t&&d?0===n.length?h:(0,c.Y)(ne,{width:t,height:d,sticky:r,setStickyState:s,children:h}):null}})}function ie(e){e.useInstance.push(oe),e.stateReducers.push(((e,t,r)=>{const n=t;if(n.type===q.Init)return{...e,sticky:{...null==r?void 0:r.sticky}};if(n.type===q.SetStickyState){const{size:t}=n;return t?{...e,sticky:{...null==r?void 0:r.sticky,...null==e?void 0:e.sticky,...n.size}}:{...e}}return e}))}ie.pluginName="useSticky";var le=r(68235);const ae=(0,k.I4)(O.A)`
  width: 120px;
  margin-right: 8px;
`,se=function({value:e,onChange:t,searchOptions:r}){var n,o;return(0,c.Y)(ae,{className:"search-select",value:e||(null!=(n=null==r||null==(o=r[0])?void 0:o.value)?n:""),options:r,onChange:t})},ce={alphanumeric:(e,t,r)=>{const n=e.values[r],o=t.values[r];return n&&"string"==typeof n?o&&"string"==typeof o?n.localeCompare(o):1:-1}},ue=(0,k.I4)(E.A)`
  display: flex;
  justify-content: flex-end;

  .search-select-container {
    display: flex;
  }

  .search-by-label {
    align-self: center;
    margin-right: 4px;
  }
`,de=k.I4.div`
  display: flex;
`,he=(0,z.v)((function({tableClassName:e,columns:t,data:r,serverPaginationData:n,width:i="100%",height:l=300,pageSize:a=0,initialState:s={},pageSizeOptions:d=le.x,maxPageItemCount:h=9,sticky:p,searchInput:g=!0,onServerPaginationChange:f,rowCount:m,selectPageSize:y,noResults:v="No data found",hooks:b,serverPagination:w,wrapperRef:S,onColumnOrderChange:k,renderGroupingHeaders:C,renderTimeComparisonDropdown:x,handleSortByChange:A,sortByFromParent:E=[],manualSearch:N=!1,onSearchChange:O,initialSearchText:T,searchInputId:Y,onSearchColChange:I,searchOptions:M,...P}){const $=[D.useGlobalFilter,D.useSortBy,D.usePagination,D.useColumnOrder,p?ie:[],b||[]].flat(),F=Object.keys((null==r?void 0:r[0])||{}),L=(0,H.Z)(F),R=w?m:r.length,z=(0,u.useRef)([]),j=(0,u.useRef)([a,R]),U=a>0&&R>0,_=U||!!g||x,W={...s,sortBy:w?E:z.current,pageSize:a>0?a:R||10},V=(0,u.useRef)(null),Q=(0,u.useRef)(null),Z=(0,u.useRef)(null),J=S||V,q=JSON.stringify(n),ee=(0,u.useCallback)((()=>{var e,t;if(J.current)return{width:Number(i)||J.current.clientWidth,height:(Number(l)||J.current.clientHeight)-((null==(e=Q.current)?void 0:e.clientHeight)||0)-((null==(t=Z.current)?void 0:t.clientHeight)||0)}}),[l,i,J,U,_,Z,R,q]),te=(0,u.useCallback)(((e,t,r)=>(0,B.Ht)(e,r,{keys:[...t,e=>t.map((t=>e.values[t])).join(" ")],threshold:B.cG.ACRONYM})),[]),{getTableProps:re,getTableBodyProps:ne,prepareRow:oe,headerGroups:ae,footerGroups:he,page:pe,pageCount:ge,gotoPage:fe,preGlobalFilteredRows:me,setGlobalFilter:ye,setPageSize:ve,wrapStickyTable:be,setColumnOrder:we,allColumns:Se,state:{pageIndex:ke,pageSize:Ce,globalFilter:xe,sticky:Ae={},sortBy:Ee}}=(0,D.useTable)({columns:t,data:r,initialState:W,getTableSize:ee,globalFilter:te,sortTypes:ce,autoResetSortBy:!o()(F,L),manualSortBy:!!w,...P},...$),Ne=(0,u.useCallback)((e=>{N&&O?O(e):ye(e)}),[N,O,ye]);(0,u.useEffect)((()=>{const e=(null==n?void 0:n.sortBy)||[];if(w&&!o()(Ee,e))if(Array.isArray(Ee)&&Ee.length>0){const[e]=Ee,r=t.find((t=>(null==t?void 0:t.id)===(null==e?void 0:e.id)));if(r&&"columnKey"in r){const t={...e,key:r.columnKey};A([t])}}else A([])}),[Ee]);const Oe=e=>{w&&f(0,e),(e||0!==R)&&ve(0===e?R:e)},Te="function"==typeof v?v(xe):v,Ye=()=>(0,c.Y)("div",{className:"dt-no-results",children:Te});if(!t||0===t.length)return be?be(Ye):Ye();const Ie=t.some((e=>!!e.Footer));let Me=-1;const Pe=e=>{const t=e.target;Me=Se.findIndex((e=>e.id===t.dataset.columnName)),e.dataTransfer.setData("text/plain",`${Me}`)},$e=e=>{const t=e.target,r=Se.findIndex((e=>e.id===t.dataset.columnName));if(-1!==r){const e=Se.map((e=>e.id)),t=e.splice(Me,1);e.splice(r,0,t[0]),we(e),k()}e.preventDefault()},Fe=()=>(0,c.FD)("table",{...re({className:e}),children:[(0,c.FD)("thead",{children:[C?C():null,ae.map((e=>{const{key:t,...r}=e.getHeaderGroupProps();return(0,c.Y)("tr",{...r,children:e.headers.map((e=>e.render("Header",{key:e.id,...e.getSortByToggleProps(),onDragStart:Pe,onDrop:$e})))},t||e.id)}))]}),(0,c.Y)("tbody",{...ne(),children:pe&&pe.length>0?pe.map((e=>{oe(e);const{key:t,...r}=e.getRowProps();return(0,c.Y)("tr",{...r,role:"row",children:e.cells.map((e=>e.render("Cell",{key:e.column.id})))},t||e.id)})):(0,c.Y)("tr",{children:(0,c.Y)("td",{className:"dt-no-results",colSpan:t.length,children:Te})})}),Ie&&(0,c.Y)("tfoot",{children:he.map((e=>{const{key:t,...r}=e.getHeaderGroupProps();return(0,c.Y)("tr",{...r,role:"row",children:e.headers.map((e=>e.render("Footer",{key:e.id})))},t||e.id)}))})]});(j.current[0]!==a||0===a&&j.current[1]!==R)&&(j.current=[a,R],Oe(a));const Le=Ae.height?{}:{visibility:"hidden"};let Re=ge,ze=Ce,He=ke,De=fe;if(w){var Be,je;const e=null!=(Be=null==n?void 0:n.pageSize)?Be:a;Re=Math.ceil(m/e),Number.isFinite(Re)||(Re=0),ze=e,-1===d.findIndex((([e])=>e>=ze))&&(ze=0),He=null!=(je=null==n?void 0:n.currentPage)?je:0,De=t=>f(t,e)}return(0,c.FD)("div",{ref:J,style:{width:i,height:l},children:[_?(0,c.Y)("div",{ref:Q,className:"form-inline dt-controls",children:(0,c.Y)(de,{className:"row",children:(0,c.FD)(ue,{size:"middle",children:[U?(0,c.Y)(X,{total:R,current:ze,options:d,selectRenderer:"boolean"==typeof y?void 0:y,onChange:Oe}):null,w&&(0,c.FD)("div",{className:"search-select-container",children:[(0,c.Y)("span",{className:"search-by-label",children:"Search by: "}),(0,c.Y)(se,{searchOptions:M,value:(null==n?void 0:n.searchColumn)||"",onChange:I})]}),g&&(0,c.Y)(G,{searchInput:"boolean"==typeof g?void 0:g,preGlobalFilteredRows:me,setGlobalFilter:N?Ne:ye,filterValue:N?T:xe,id:Y,serverPagination:!!w,rowCount:m}),x?x():null]})})}):null,be?be(Fe):Fe(),U&&Re>1?(0,c.Y)(K,{ref:Z,style:Le,maxPageItemCount:h,pageCount:Re,currentPage:He,onPageChange:De}):null]})})),pe=k.I4.div`
  ${({theme:e})=>w.AH`
    /* Base table styles */
    table {
      width: 100%;
      min-width: auto;
      max-width: none;
      margin: 0;
      border-collapse: collapse;
    }

    /* Cell styling */
    th,
    td {
      min-width: 4.3em;
      padding: 0.75rem;
      vertical-align: top;
    }

    /* Header styling */
    thead > tr > th {
      padding-right: 0;
      position: relative;
      background-color: ${e.colorBgBase};
      text-align: left;
      border-bottom: 2px solid ${e.colorSplit};
      color: ${e.colorText};
      vertical-align: bottom;
    }

    /* Icons in header */
    th svg {
      margin: 1px ${e.sizeUnit/2}px;
      fill-opacity: 0.2;
    }

    th.is-sorted svg {
      color: ${e.colorText};
      fill-opacity: 1;
    }

    /* Table body styling */
    .table > tbody > tr:first-of-type > td,
    .table > tbody > tr:first-of-type > th {
      border-top: 0;
    }

    .table > tbody tr td {
      font-feature-settings: 'tnum' 1;
      border-top: 1px solid ${e.colorSplit};
    }

    /* Bootstrap-like condensed table styles */
    table.table-condensed,
    table.table-sm {
      font-size: ${e.fontSizeSM}px;
    }

    table.table-condensed th,
    table.table-condensed td,
    table.table-sm th,
    table.table-sm td {
      padding: 0.3rem;
    }

    /* Bootstrap-like bordered table styles */
    table.table-bordered {
      border: 1px solid ${e.colorSplit};
    }

    table.table-bordered th,
    table.table-bordered td {
      border: 1px solid ${e.colorSplit};
    }

    /* Bootstrap-like striped table styles */
    table.table-striped tbody tr:nth-of-type(odd) {
      background-color: ${e.colorBgLayout};
    }

    /* Controls and metrics */
    .dt-controls {
      padding-bottom: 0.65em;
    }

    .dt-metric {
      text-align: right;
    }

    .dt-totals {
      font-weight: ${e.fontWeightStrong};
    }

    .dt-is-null {
      color: ${e.colorTextTertiary};
    }

    td.dt-is-filter {
      cursor: pointer;
    }

    td.dt-is-filter:hover {
      background-color: ${e.colorPrimaryBgHover};
    }

    td.dt-is-active-filter,
    td.dt-is-active-filter:hover {
      background-color: ${e.colorPrimaryBgHover};
    }

    .dt-global-filter {
      float: right;
    }

    /* Cell truncation */
    .dt-truncate-cell {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .dt-truncate-cell:hover {
      overflow: visible;
      white-space: normal;
      height: auto;
    }

    /* Pagination styling */
    .dt-pagination {
      text-align: right;
      /* use padding instead of margin so clientHeight can capture it */
      padding: ${e.paddingXXS}px 0px;
    }

    .dt-pagination .pagination > li {
      display: inline;
      margin: 0 ${e.marginXXS}px;
    }

    .dt-pagination .pagination > li > a,
    .dt-pagination .pagination > li > span {
      background-color: ${e.colorBgBase};
      color: ${e.colorText};
      border-color: ${e.colorBorderSecondary};
      padding: ${e.paddingXXS}px ${e.paddingXS}px;
      border-radius: ${e.borderRadius}px;
    }

    .dt-pagination .pagination > li.active > a,
    .dt-pagination .pagination > li.active > span,
    .dt-pagination .pagination > li.active > a:focus,
    .dt-pagination .pagination > li.active > a:hover,
    .dt-pagination .pagination > li.active > span:focus,
    .dt-pagination .pagination > li.active > span:hover {
      background-color: ${e.colorPrimary};
      color: ${e.colorBgContainer};
      border-color: ${e.colorBorderSecondary};
    }

    .pagination > li > span.dt-pagination-ellipsis:focus,
    .pagination > li > span.dt-pagination-ellipsis:hover {
      background: ${e.colorBgLayout};
      border-color: ${e.colorBorderSecondary};
    }

    .dt-no-results {
      text-align: center;
      padding: 1em 0.6em;
    }

    .right-border-only {
      border-right: 2px solid ${e.colorSplit};
    }

    table .right-border-only:last-child {
      border-right: none;
    }
  `}
`;var ge=r(7566),fe=r(40984),me=r(29898),ye=r(42879);function ve(e,t){const{dataType:r,formatter:n,config:o={}}=e,i=r===v.s.Numeric,l=void 0===o.d3SmallNumberFormat?n:o.currencyFormat?new fe.A({d3Format:o.d3SmallNumberFormat,currency:o.currencyFormat}):(0,me.gV)(o.d3SmallNumberFormat);return function(e,t){return void 0===t?[!1,""]:null===t||t instanceof ye.A&&null===t.input?[!1,"N/A"]:e?[!1,e(t)]:"string"==typeof t?(0,ge.fE)(t)?[!0,(0,ge.pn)(t)]:[!1,t]:[!1,t.toString()]}(i&&"number"==typeof t&&Math.abs(t)<1?l:n,t)}var be=r(25766);const we={enter:"Enter",spacebar:"Spacebar",space:" "};function Se(e){return e===v.s.Temporal?"datetime":e===v.s.String?"alphanumeric":"basic"}function ke({column:e}){const{isSorted:t,isSortedDesc:r}=e;let n=(0,c.Y)(p.M,{});return t&&(n=r?(0,c.Y)(g.G,{}):(0,c.Y)(f.X,{})),n}function Ce({count:e,value:t,onChange:r,onBlur:n,inputRef:o}){return(0,c.FD)(E.A,{direction:"horizontal",size:4,className:"dt-global-filter",children:[(0,b.t)("Search"),(0,c.Y)(N.A,{"aria-label":(0,b.t)("Search %s records",e),placeholder:(0,b.tn)("%s record","%s records...",e,e),value:t,onChange:r,onBlur:n,ref:o})]})}function xe({options:e,current:t,onChange:r}){const{Option:n}=O.A;return(0,c.FD)(c.FK,{children:[(0,c.Y)("label",{htmlFor:"pageSizeSelect",className:"sr-only",children:(0,b.t)("Select page size")}),(0,b.t)("Show")," ",(0,c.Y)(O.A,{id:"pageSizeSelect",value:t,onChange:e=>r(e),size:"small",css:e=>w.AH`
          width: ${18*e.sizeUnit}px;
        `,"aria-label":(0,b.t)("Show entries per page"),children:e.map((e=>{const[t,r]=Array.isArray(e)?e:[e,e];return(0,c.Y)(n,{value:Number(t),children:r},t)}))})," ",(0,b.t)("entries per page")]})}const Ae=e=>e?(0,b.t)("No matching records found"):(0,b.t)("No records found");function Ee(e){const{timeGrain:t,height:r,width:n,data:i,totals:a,isRawRecords:p,rowCount:g=0,columns:f,alignPositiveNegative:m=!1,colorPositiveNegative:v=!1,includeSearch:E=!1,pageSize:N=0,serverPagination:O=!1,serverPaginationData:z,setDataMask:H,showCellBars:D=!0,sortDesc:B=!1,filters:j,sticky:U=!0,columnColorFormatters:G,allowRearrangeColumns:_=!1,allowRenderHtml:W=!0,onContextMenu:V,emitCrossFilters:X,isUsingTimeComparison:K,basicColorFormatters:Q,basicColorColumnFormatters:Z,hasServerPageLengthChanged:q,serverPageLength:ee,slice_id:te}=e,re=[{key:"all",label:(0,b.t)("Display all")},{key:"#",label:"#"},{key:"△",label:"△"},{key:"%",label:"%"}],ne=(0,u.useCallback)((e=>(0,S.PT)(t)(e)),[t]),[oe,ie]=(0,u.useState)({width:0,height:0}),[ae,se]=(0,u.useState)(!1),[ce,ue]=(0,u.useState)(!1),[de,ge]=(0,u.useState)([re[0].key]),[fe,me]=(0,u.useState)([]),Ee=(0,k.DP)(),Ne=(0,u.useMemo)((()=>(O?le.D:le.x).filter((([e])=>O?(e=>e<=g)(e):e<=2*i.length))),[i.length,g,O]),Oe=(0,u.useCallback)((function(e,t){const r=null==i?void 0:i.map((t=>null==t?void 0:t[e])).filter((e=>"number"==typeof e));return i&&r.length===i.length?t?[0,(0,d.A)(r.map(Math.abs))]:(0,h.A)(r):null}),[i]),Te=(0,u.useCallback)((function(e,t){var r;return!!j&&(null==(r=j[e])?void 0:r.includes(t))}),[j]),Ye=(e,r)=>{let n={...j||{}};n=j&&Te(e,r)?{}:{[e]:[r]},Array.isArray(n[e])&&0===n[e].length&&delete n[e];const o=Object.keys(n),i=Object.values(n),l=[];return o.forEach((e=>{var t;const r=e===C.Tf,o=(0,x.A)(null==(t=n)?void 0:t[e]);if(o.length){const e=o.map((e=>r?ne(e):e));l.push(`${e.join(", ")}`)}})),{dataMask:{extraFormData:{filters:0===o.length?[]:o.map((e=>{var r;const o=(0,x.A)(null==(r=n)?void 0:r[e]);return o.length?{col:e,op:"IN",val:o.map((e=>e instanceof Date?e.getTime():e)),grain:e===C.Tf?t:void 0}:{col:e,op:"IS NULL"}}))},filterState:{label:l.join(", "),value:i.length?i:null,filters:n&&Object.keys(n).length?n:null}},isCurrentValueSelected:Te(e,r)}},Ie=(0,u.useCallback)((function(e,t){X&&H(Ye(e,t).dataMask)}),[X,Ye,H]),Me=[(0,b.t)("Main"),"#","△","%"],Pe=(0,u.useMemo)((()=>{if(!K)return f;const e=re[0].key,t=Me[0],r=de.includes(e);return f.filter((({label:e,key:n})=>{const o=n.substring(e.length),i=fe.includes(o);return e===t||!i&&(!Me.includes(e)||r||de.includes(e))}))}),[f,re,Me,K,fe,de]),$e=V&&!p?(e,t,r,n)=>{const o=[];Pe.forEach((t=>{if(!t.isMetric){const r=e[t.key];o.push({col:t.key,op:"==",val:r,formattedVal:ve(t,r)[1]})}})),V(r,n,{drillToDetail:o,crossFilter:t.isMetric?void 0:Ye(t.key,t.value),drillBy:t.isMetric?void 0:{filters:[{col:t.key,op:"==",val:t.value}],groupbyFieldName:"groupby"}})}:void 0,Fe=(0,u.useMemo)((()=>((e,t)=>{const r={};return t?(e.forEach(((e,t)=>{if(Me.includes(e.label)){const n=e.key.substring(e.label.length);r[n]?r[n].push(t):r[n]=[t]}})),r):r})(Pe,K)),[Pe,K]),Le=(0,u.useCallback)(((e,t)=>{const{key:r,label:n,isNumeric:o,dataType:i,isMetric:l,isPercentMetric:s,config:u={}}=e,d=u.customColumnName||n;let h=d;["#","△","%",(0,b.t)("Main")].includes(e.label)&&(e.label===(0,b.t)("Main")?h=u.customColumnName||e.originalLabel||"":u.customColumnName?h=!1!==u.displayTypeIcon?`${e.label} ${u.customColumnName}`:u.customColumnName:!1===u.displayTypeIcon&&(h=""));const g=Number.isNaN(Number(u.columnWidth))?u.columnWidth:Number(u.columnWidth),f=(e=>{const{isNumeric:t,config:r={}}=e;return{textAlign:r.horizontalAlign||(t&&!K?"right":"left")}})(e),S=void 0===u.alignPositiveNegative?m:u.alignPositiveNegative,C=void 0===u.colorPositiveNegative?v:u.colorPositiveNegative,{truncateLongCells:x}=u,E=o&&Array.isArray(G)&&G.length>0,N=K&&Array.isArray(Q)&&Q.length>0,O=!N&&!E&&(void 0===u.showCellBars?D:u.showCellBars)&&(l||p||s)&&Oe(r,S);let T="";if(X&&!l&&(T+=" dt-is-filter"),l||s){if(Me.includes(d)){const e=r.substring(d.length),n=Fe[e]||[];t===n[n.length-1]&&(T+=" right-border-only")}}else T+=" right-border-only";return{id:String(t),columnKey:r,accessor:e=>e[r],Cell:({value:t,row:n})=>{var o;const[i,a]=ve(e,t),s=i&&W?{__html:a}:void 0;let u,d="";const h=e.key.substring(e.label.length).trim();var p,m,v,b;!E&&N&&(u=null==(p=Q[n.index][h])?void 0:p.backgroundColor,d=e.label===Me[0]?null==(m=Q[n.index][h])?void 0:m.mainArrow:""),E&&G.filter((t=>t.column===e.key)).forEach((e=>{const r=!(!t&&0!==t)&&e.getColorFromValue(t);r&&(u=r)})),Z&&(null==Z?void 0:Z.length)>0&&(u=(null==(v=Z[n.index][e.key])?void 0:v.backgroundColor)||u,d=e.label===Me[0]?null==(b=Z[n.index][e.key])?void 0:b.mainArrow:"");const Y=k.I4.td`
            color: ${Ee.colorText};
            text-align: ${f.textAlign};
            white-space: ${t instanceof Date?"nowrap":void 0};
            position: relative;
            background: ${u||void 0};
            padding-left: ${e.isChildColumn?5*Ee.sizeUnit+"px":`${Ee.sizeUnit}px`};
          `,I=w.AH`
            position: absolute;
            height: 100%;
            display: block;
            top: 0;
            ${O&&`\n                width: ${function({value:e,valueRange:t,alignPositiveNegative:r}){const[n,o]=t;if(r)return Math.abs(Math.round(e/o*100));const i=Math.abs(Math.max(o,0))+Math.abs(Math.min(n,0));return Math.round(Math.abs(e)/i*100)}({value:t,valueRange:O,alignPositiveNegative:S})}%;\n                left: ${function({value:e,valueRange:t,alignPositiveNegative:r}){if(r)return 0;const[n,o]=t,i=Math.abs(Math.max(o,0)),l=Math.abs(Math.min(n,0)),a=i+l;return Math.round(Math.min(l+e,l)/a*100)}({value:t,valueRange:O,alignPositiveNegative:S})}%;\n                background-color: ${function({value:e,colorPositiveNegative:t=!1}){return`rgba(${t&&e<0?150:0},0,0,0.2)`}({value:t,colorPositiveNegative:C})};\n              `}
          `;let M=w.AH`
            color: ${Q&&(null==(o=Q[n.index][h])?void 0:o.arrowColor)===R.m.Green?Ee.colorSuccess:Ee.colorError};
            margin-right: ${Ee.sizeUnit}px;
          `;var P;Z&&(null==Z?void 0:Z.length)>0&&(M=w.AH`
              color: ${(null==(P=Z[n.index][e.key])?void 0:P.arrowColor)===R.m.Green?Ee.colorSuccess:Ee.colorError};
              margin-right: ${Ee.sizeUnit}px;
            `);const $={"aria-labelledby":`header-${e.key}`,role:"cell",title:"number"==typeof t?String(t):void 0,onClick:!X||O||l?void 0:()=>{(0,A.j)()||Ie(r,t)},onContextMenu:e=>{$e&&(e.preventDefault(),e.stopPropagation(),$e(n.original,{key:r,value:t,isMetric:l},e.nativeEvent.clientX,e.nativeEvent.clientY))},className:[T,null==t||t instanceof ye.A&&null==t.input?"dt-is-null":"",Te(r,t)?" dt-is-active-filter":""].join(" "),tabIndex:0};return s?x?(0,c.Y)(Y,{...$,children:(0,c.Y)("div",{className:"dt-truncate-cell",style:g?{width:g}:void 0,dangerouslySetInnerHTML:s})}):(0,c.Y)(Y,{...$,dangerouslySetInnerHTML:s}):(0,c.FD)(Y,{...$,children:[O&&(0,c.Y)("div",{className:y()("cell-bar","number"==typeof t&&t<0?"negative":"positive"),css:I,role:"presentation"}),x?(0,c.FD)("div",{className:"dt-truncate-cell",style:g?{width:g}:void 0,children:[d&&(0,c.Y)("span",{css:M,children:d}),a]}):(0,c.FD)(c.FK,{children:[d&&(0,c.Y)("span",{css:M,children:d}),a]})]})},Header:({column:t,onClick:r,style:n,onDragStart:o,onDrop:i})=>(0,c.FD)("th",{id:`header-${e.originalLabel}`,title:(0,b.t)("Shift + Click to sort by multiple columns"),className:[T,t.isSorted?"is-sorted":""].join(" "),style:{...f,...n},onKeyDown:e=>{Object.values(we).includes(e.key)&&t.toggleSortBy()},role:"columnheader button",onClick:r,"data-column-name":t.id,..._&&{draggable:"true",onDragStart:o,onDragOver:e=>e.preventDefault(),onDragEnter:e=>e.preventDefault(),onDrop:i},tabIndex:0,children:[u.columnWidth?(0,c.Y)("div",{style:{width:g,height:.01}}):null,(0,c.FD)("div",{"data-column-name":t.id,css:{display:"inline-flex",alignItems:"flex-end"},children:[(0,c.Y)("span",{"data-column-name":t.id,children:h}),(0,c.Y)(ke,{column:t})]})]}),Footer:a?0===t?(0,c.Y)("th",{children:(0,c.FD)("div",{css:w.AH`
                  display: flex;
                  align-items: center;
                  & svg {
                    margin-left: ${Ee.sizeUnit}px;
                    color: ${Ee.colorBorder} !important;
                  }
                `,children:[(0,b.t)("Summary"),(0,c.Y)(Y.m,{overlay:(0,b.t)("Show total aggregations of selected metrics. Note that row limit does not apply to the result."),children:(0,c.Y)(L.A,{})})]})},`footer-summary-${t}`):(0,c.Y)("td",{style:f,children:(0,c.Y)("strong",{children:ve(e,a[r])[1]})},`footer-total-${t}`):void 0,sortDescFirst:B,sortType:Se(i)}}),[m,v,X,Oe,Te,p,D,B,Ie,a,G,ae]),Re=(0,u.useMemo)((()=>Pe.filter((e=>{var t;return!1!==(null==(t=e.config)?void 0:t.visible)}))),[Pe]),ze=(0,u.useMemo)((()=>Re.map(Le)),[Re,Le]),[He,De]=(0,u.useState)([]);(0,u.useEffect)((()=>{const e=ze.filter((e=>"alphanumeric"===(null==e?void 0:e.sortType))).map((e=>({value:e.columnKey,label:e.columnKey})));o()(e,He)||De(e||[])}),[ze]);const Be=(0,u.useCallback)(((e,t)=>{const r={...z,currentPage:e,pageSize:t};(0,be.F)(H,r)}),[H]);(0,u.useEffect)((()=>{if(q){const e={...z,currentPage:0,pageSize:ee};(0,be.F)(H,e)}}),[]);const je=(0,u.useCallback)((({width:e,height:t})=>{ie({width:e,height:t})}),[]);(0,u.useLayoutEffect)((()=>{const e=J(),{width:t,height:o}=oe;n-t>e||r-o>e?je({width:n-e,height:r-e}):(t-n>e||o-r>e)&&je({width:n,height:r})}),[n,r,je,oe]);const{width:Ue,height:Ge}=oe,_e=(0,u.useCallback)((e=>{if(!O)return;const t={...z,sortBy:e};(0,be.F)(H,t)}),[H,O]),We=l()((e=>{var t;const r={...z||{},searchColumn:(null==z?void 0:z.searchColumn)||(null==(t=He[0])?void 0:t.value),searchText:e,currentPage:0};(0,be.F)(H,r)}),800);return(0,c.Y)(pe,{children:(0,c.Y)(he,{columns:ze,data:i,rowCount:g,tableClassName:"table table-striped table-condensed",pageSize:N,serverPaginationData:z,pageSizeOptions:Ne,width:Ue,height:Ge,serverPagination:O,onServerPaginationChange:Be,onColumnOrderChange:()=>se(!ae),initialSearchText:(null==z?void 0:z.searchText)||"",sortByFromParent:(null==z?void 0:z.sortBy)||[],searchInputId:`${te}-search`,maxPageItemCount:n>340?9:7,noResults:Ae,searchInput:E&&Ce,selectPageSize:null!==N&&xe,sticky:U,renderGroupingHeaders:s()(Fe)?void 0:()=>{const e=[];let t=0;return Object.entries(Fe||{}).forEach((([r,n])=>{var o;const i=n[0],l=n.length,a=Pe[i],s=a&&(null==(o=f.find((e=>e.key===a.key)))?void 0:o.originalLabel)||r;for(let r=t;r<i;r+=1)e.push((0,c.Y)("th",{style:{borderBottom:0},"aria-label":`Header-${r}`},`placeholder-${r}`));e.push((0,c.FD)("th",{colSpan:l,style:{borderBottom:0},children:[s,(0,c.Y)("span",{css:w.AH`
              float: right;
              & svg {
                color: ${Ee.colorIcon} !important;
              }
            `,children:fe.includes(r)?(0,c.Y)($.A,{onClick:()=>me(fe.filter((e=>e!==r)))}):(0,c.Y)(F.A,{onClick:()=>me([...fe,r])})})]},`header-${r}`)),t=i+l})),(0,c.Y)("tr",{css:w.AH`
          th {
            border-right: 1px solid ${Ee.colorSplit};
          }
          th:first-child {
            border-left: none;
          }
          th:last-child {
            border-right: none;
          }
        `,children:e})},renderTimeComparisonDropdown:K?()=>{const e=re[0].key;return(0,c.Y)(T.ms,{placement:"bottomRight",open:ce,onOpenChange:e=>{ue(e)},menu:{multiple:!0,onClick:t=>{const{key:r}=t;r===e?ge([e]):de.includes(e)?ge([r]):ge(de.includes(r)?de.filter((e=>e!==r)):[...de,r])},onBlur:()=>{3===de.length&&ge([re[0].key])},selectedKeys:de,items:[{key:"all",label:(0,c.Y)("div",{css:w.AH`
                    max-width: 242px;
                    padding: 0 ${2*Ee.sizeUnit}px;
                    color: ${Ee.colorText};
                    font-size: ${Ee.fontSizeSM}px;
                  `,children:(0,b.t)("Select columns that will be displayed in the table. You can multiselect columns.")}),type:"group",children:re.map((e=>({key:e.key,label:(0,c.FD)(c.FK,{children:[(0,c.Y)("span",{css:w.AH`
                          color: ${Ee.colorText};
                        `,children:e.label}),(0,c.Y)("span",{css:w.AH`
                          float: right;
                          font-size: ${Ee.fontSizeSM}px;
                        `,children:de.includes(e.key)&&(0,c.Y)(I.A,{})})]})})))}]},trigger:["click"],children:(0,c.FD)("span",{children:[(0,c.Y)(M.A,{})," ",(0,c.Y)(P.A,{})]})})}:void 0,handleSortByChange:_e,onSearchColChange:e=>{if(!o()(e,null==z?void 0:z.searchColumn)){const t={...z||{},searchColumn:e,searchText:""};(0,be.F)(H,t)}},manualSearch:O,onSearchChange:We,searchOptions:He})})}},69856:(e,t,r)=>{var n=r(75972).k5;e.exports.M=function(e){return n({tag:"svg",attr:{viewBox:"0 0 320 512"},child:[{tag:"path",attr:{d:"M41 288h238c21.4 0 32.1 25.9 17 41L177 448c-9.4 9.4-24.6 9.4-33.9 0L24 329c-15.1-15.1-4.4-41 17-41zm255-105L177 64c-9.4-9.4-24.6-9.4-33.9 0L24 183c-15.1 15.1-4.4 41 17 41h238c21.4 0 32.1-25.9 17-41z"}}]})(e)}},70731:e=>{var t={À:"A",Á:"A",Â:"A",Ã:"A",Ä:"A",Å:"A",Ấ:"A",Ắ:"A",Ẳ:"A",Ẵ:"A",Ặ:"A",Æ:"AE",Ầ:"A",Ằ:"A",Ȃ:"A",Ả:"A",Ạ:"A",Ẩ:"A",Ẫ:"A",Ậ:"A",Ç:"C",Ḉ:"C",È:"E",É:"E",Ê:"E",Ë:"E",Ế:"E",Ḗ:"E",Ề:"E",Ḕ:"E",Ḝ:"E",Ȇ:"E",Ẻ:"E",Ẽ:"E",Ẹ:"E",Ể:"E",Ễ:"E",Ệ:"E",Ì:"I",Í:"I",Î:"I",Ï:"I",Ḯ:"I",Ȋ:"I",Ỉ:"I",Ị:"I",Ð:"D",Ñ:"N",Ò:"O",Ó:"O",Ô:"O",Õ:"O",Ö:"O",Ø:"O",Ố:"O",Ṍ:"O",Ṓ:"O",Ȏ:"O",Ỏ:"O",Ọ:"O",Ổ:"O",Ỗ:"O",Ộ:"O",Ờ:"O",Ở:"O",Ỡ:"O",Ớ:"O",Ợ:"O",Ù:"U",Ú:"U",Û:"U",Ü:"U",Ủ:"U",Ụ:"U",Ử:"U",Ữ:"U",Ự:"U",Ý:"Y",à:"a",á:"a",â:"a",ã:"a",ä:"a",å:"a",ấ:"a",ắ:"a",ẳ:"a",ẵ:"a",ặ:"a",æ:"ae",ầ:"a",ằ:"a",ȃ:"a",ả:"a",ạ:"a",ẩ:"a",ẫ:"a",ậ:"a",ç:"c",ḉ:"c",è:"e",é:"e",ê:"e",ë:"e",ế:"e",ḗ:"e",ề:"e",ḕ:"e",ḝ:"e",ȇ:"e",ẻ:"e",ẽ:"e",ẹ:"e",ể:"e",ễ:"e",ệ:"e",ì:"i",í:"i",î:"i",ï:"i",ḯ:"i",ȋ:"i",ỉ:"i",ị:"i",ð:"d",ñ:"n",ò:"o",ó:"o",ô:"o",õ:"o",ö:"o",ø:"o",ố:"o",ṍ:"o",ṓ:"o",ȏ:"o",ỏ:"o",ọ:"o",ổ:"o",ỗ:"o",ộ:"o",ờ:"o",ở:"o",ỡ:"o",ớ:"o",ợ:"o",ù:"u",ú:"u",û:"u",ü:"u",ủ:"u",ụ:"u",ử:"u",ữ:"u",ự:"u",ý:"y",ÿ:"y",Ā:"A",ā:"a",Ă:"A",ă:"a",Ą:"A",ą:"a",Ć:"C",ć:"c",Ĉ:"C",ĉ:"c",Ċ:"C",ċ:"c",Č:"C",č:"c",C̆:"C",c̆:"c",Ď:"D",ď:"d",Đ:"D",đ:"d",Ē:"E",ē:"e",Ĕ:"E",ĕ:"e",Ė:"E",ė:"e",Ę:"E",ę:"e",Ě:"E",ě:"e",Ĝ:"G",Ǵ:"G",ĝ:"g",ǵ:"g",Ğ:"G",ğ:"g",Ġ:"G",ġ:"g",Ģ:"G",ģ:"g",Ĥ:"H",ĥ:"h",Ħ:"H",ħ:"h",Ḫ:"H",ḫ:"h",Ĩ:"I",ĩ:"i",Ī:"I",ī:"i",Ĭ:"I",ĭ:"i",Į:"I",į:"i",İ:"I",ı:"i",Ĳ:"IJ",ĳ:"ij",Ĵ:"J",ĵ:"j",Ķ:"K",ķ:"k",Ḱ:"K",ḱ:"k",K̆:"K",k̆:"k",Ĺ:"L",ĺ:"l",Ļ:"L",ļ:"l",Ľ:"L",ľ:"l",Ŀ:"L",ŀ:"l",Ł:"l",ł:"l",Ḿ:"M",ḿ:"m",M̆:"M",m̆:"m",Ń:"N",ń:"n",Ņ:"N",ņ:"n",Ň:"N",ň:"n",ŉ:"n",N̆:"N",n̆:"n",Ō:"O",ō:"o",Ŏ:"O",ŏ:"o",Ő:"O",ő:"o",Œ:"OE",œ:"oe",P̆:"P",p̆:"p",Ŕ:"R",ŕ:"r",Ŗ:"R",ŗ:"r",Ř:"R",ř:"r",R̆:"R",r̆:"r",Ȓ:"R",ȓ:"r",Ś:"S",ś:"s",Ŝ:"S",ŝ:"s",Ş:"S",Ș:"S",ș:"s",ş:"s",Š:"S",š:"s",Ţ:"T",ţ:"t",ț:"t",Ț:"T",Ť:"T",ť:"t",Ŧ:"T",ŧ:"t",T̆:"T",t̆:"t",Ũ:"U",ũ:"u",Ū:"U",ū:"u",Ŭ:"U",ŭ:"u",Ů:"U",ů:"u",Ű:"U",ű:"u",Ų:"U",ų:"u",Ȗ:"U",ȗ:"u",V̆:"V",v̆:"v",Ŵ:"W",ŵ:"w",Ẃ:"W",ẃ:"w",X̆:"X",x̆:"x",Ŷ:"Y",ŷ:"y",Ÿ:"Y",Y̆:"Y",y̆:"y",Ź:"Z",ź:"z",Ż:"Z",ż:"z",Ž:"Z",ž:"z",ſ:"s",ƒ:"f",Ơ:"O",ơ:"o",Ư:"U",ư:"u",Ǎ:"A",ǎ:"a",Ǐ:"I",ǐ:"i",Ǒ:"O",ǒ:"o",Ǔ:"U",ǔ:"u",Ǖ:"U",ǖ:"u",Ǘ:"U",ǘ:"u",Ǚ:"U",ǚ:"u",Ǜ:"U",ǜ:"u",Ứ:"U",ứ:"u",Ṹ:"U",ṹ:"u",Ǻ:"A",ǻ:"a",Ǽ:"AE",ǽ:"ae",Ǿ:"O",ǿ:"o",Þ:"TH",þ:"th",Ṕ:"P",ṕ:"p",Ṥ:"S",ṥ:"s",X́:"X",x́:"x",Ѓ:"Г",ѓ:"г",Ќ:"К",ќ:"к",A̋:"A",a̋:"a",E̋:"E",e̋:"e",I̋:"I",i̋:"i",Ǹ:"N",ǹ:"n",Ồ:"O",ồ:"o",Ṑ:"O",ṑ:"o",Ừ:"U",ừ:"u",Ẁ:"W",ẁ:"w",Ỳ:"Y",ỳ:"y",Ȁ:"A",ȁ:"a",Ȅ:"E",ȅ:"e",Ȉ:"I",ȉ:"i",Ȍ:"O",ȍ:"o",Ȑ:"R",ȑ:"r",Ȕ:"U",ȕ:"u",B̌:"B",b̌:"b",Č̣:"C",č̣:"c",Ê̌:"E",ê̌:"e",F̌:"F",f̌:"f",Ǧ:"G",ǧ:"g",Ȟ:"H",ȟ:"h",J̌:"J",ǰ:"j",Ǩ:"K",ǩ:"k",M̌:"M",m̌:"m",P̌:"P",p̌:"p",Q̌:"Q",q̌:"q",Ř̩:"R",ř̩:"r",Ṧ:"S",ṧ:"s",V̌:"V",v̌:"v",W̌:"W",w̌:"w",X̌:"X",x̌:"x",Y̌:"Y",y̌:"y",A̧:"A",a̧:"a",B̧:"B",b̧:"b",Ḑ:"D",ḑ:"d",Ȩ:"E",ȩ:"e",Ɛ̧:"E",ɛ̧:"e",Ḩ:"H",ḩ:"h",I̧:"I",i̧:"i",Ɨ̧:"I",ɨ̧:"i",M̧:"M",m̧:"m",O̧:"O",o̧:"o",Q̧:"Q",q̧:"q",U̧:"U",u̧:"u",X̧:"X",x̧:"x",Z̧:"Z",z̧:"z",й:"и",Й:"И",ё:"е",Ё:"Е"},r=Object.keys(t).join("|"),n=new RegExp(r,"g"),o=new RegExp(r,"");function i(e){return t[e]}var l=function(e){return e.replace(n,i)};e.exports=l,e.exports.has=function(e){return!!e.match(o)},e.exports.remove=l},75972:(e,t,r)=>{"use strict";r.d(t,{k5:()=>c});var n=r(96540),o={color:void 0,size:void 0,className:void 0,style:void 0,attr:void 0},i=n.createContext&&n.createContext(o),l=function(){return l=Object.assign||function(e){for(var t,r=1,n=arguments.length;r<n;r++)for(var o in t=arguments[r])Object.prototype.hasOwnProperty.call(t,o)&&(e[o]=t[o]);return e},l.apply(this,arguments)},a=function(e,t){var r={};for(var n in e)Object.prototype.hasOwnProperty.call(e,n)&&t.indexOf(n)<0&&(r[n]=e[n]);if(null!=e&&"function"==typeof Object.getOwnPropertySymbols){var o=0;for(n=Object.getOwnPropertySymbols(e);o<n.length;o++)t.indexOf(n[o])<0&&Object.prototype.propertyIsEnumerable.call(e,n[o])&&(r[n[o]]=e[n[o]])}return r};function s(e){return e&&e.map((function(e,t){return n.createElement(e.tag,l({key:t},e.attr),s(e.child))}))}function c(e){return function(t){return n.createElement(u,l({attr:l({},e.attr)},t),s(e.child))}}function u(e){var t=function(t){var r,o=e.attr,i=e.size,s=e.title,c=a(e,["attr","size","title"]),u=i||t.size||"1em";return t.className&&(r=t.className),e.className&&(r=(r?r+" ":"")+e.className),n.createElement("svg",l({stroke:"currentColor",fill:"currentColor",strokeWidth:"0"},t.attr,o,c,{className:r,style:l(l({color:e.color||t.color},t.style),e.style),height:u,width:u,xmlns:"http://www.w3.org/2000/svg"}),s&&n.createElement("title",null,s),e.children)};return void 0!==i?n.createElement(i.Consumer,null,(function(e){return t(e)})):t(o)}},77796:(e,t,r)=>{var n=r(75972).k5;e.exports.G=function(e){return n({tag:"svg",attr:{viewBox:"0 0 320 512"},child:[{tag:"path",attr:{d:"M41 288h238c21.4 0 32.1 25.9 17 41L177 448c-9.4 9.4-24.6 9.4-33.9 0L24 329c-15.1-15.1-4.4-41 17-41z"}}]})(e)}},85173:(e,t,r)=>{"use strict";r.d(t,{v:()=>n});const n=r(96540).memo},95021:(e,t,r)=>{"use strict";r.d(t,{j:()=>n});const n=()=>{var e;return null==(e=window.getSelection())?void 0:e.toString()}}}]);