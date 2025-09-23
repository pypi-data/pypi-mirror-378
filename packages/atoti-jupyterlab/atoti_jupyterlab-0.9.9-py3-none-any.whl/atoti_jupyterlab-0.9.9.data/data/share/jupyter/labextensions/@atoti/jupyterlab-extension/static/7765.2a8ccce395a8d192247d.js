"use strict";(self.webpackChunk_atoti_jupyterlab_extension=self.webpackChunk_atoti_jupyterlab_extension||[]).push([[7765],{67075:(r,o,e)=>{e.d(o,{o:()=>t});const t=(0,e(93345).createContext)({accentColor:"blue",successColor:"green",warningColor:"orange",errorColor:"red",whiteColor:"white",lightGrayColor:"lightgray",darkGrayColor:"darkgray"})},20258:(r,o,e)=>{e.d(o,{l:()=>d});var t=e(74389),n=e(66624),a=e(70070),i=e(93345),l=e.n(i);const c=a.A.default??a.A,s=n.A.default??n.A,d=l().forwardRef(((r,o)=>(0,t.Y)(c,{...r,ref:o,icon:s})))},78775:(r,o,e)=>{e.d(o,{L:()=>l});var t=e(74389),n=e(28349),a=e(93345),i=e(67075);const l=(0,n.E)(((r,o)=>{const e=(0,a.useContext)(i.o);return(0,t.FD)("svg",{width:"1em",height:"1em",viewBox:"0 0 180 115",fill:"currentColor",xmlns:"http://www.w3.org/2000/svg",ref:o,...r,children:[(0,t.FD)("g",{clipPath:"url(#IconEmptyFolder__a)",children:[(0,t.Y)("path",{opacity:.8,fillRule:"evenodd",clipRule:"evenodd",d:"M31.006 22.899c2.053-6.458 3.967-10.48 5.734-12.064 4.895-4.387 11.654-2 13.095-1.654 5.053 1.208 3.415-6.725 7.747-8.34 2.891-1.069 5.27.238 7.125 3.943C66.355 1.337 68.87-.248 72.257.03c5.072.425 6.848 17.45 13.815 13.727 6.967-3.724 15.513-4.576 19.164.96.79 1.2 1.096-.663 6.454-7.012 5.369-6.348 10.718-9.151 21.691-5.447 4.994 1.684 11.497 6.557 12.316 13.658 1.924 11.628 7.845 16.867 23.526 18.818 23.527 2.922 5.27 28.06-23.526 35.428-28.796 7.369-95.082 11.34-131.053-7.27-23.97-12.4-18.523-25.731 16.362-39.993Z",fill:"url(#IconEmptyFolder__b)"}),(0,t.Y)("path",{d:"M128.977 113.949H34.99c-1.382 0-2.51-1.033-2.51-2.303V41.303c0-1.27 1.128-2.303 2.51-2.303h35.157l5.413 8.218 53.417.177c1.383 0 2.511 1.26 2.511 2.53v61.731c0 1.27-1.128 2.303-2.511 2.303v-.01Z",fill:r.whiteColor||e.whiteColor,stroke:"#B3B3B3",strokeWidth:2,strokeMiterlimit:10}),(0,t.Y)("path",{d:"M136.057 113.949H35.422c-1.746 0-2.805-1.092-2.383-2.441l16.524-51.967c.402-1.378 2.02-2.963 3.962-2.736h100.028c1.745 0 2.451 1.968 1.618 4.498l-15.191 50.205c-.431 1.349-2.187 2.441-3.932 2.441h.009Z",fill:r.whiteColor||e.whiteColor,stroke:"#B3B3B3",strokeWidth:2,strokeMiterlimit:10})]}),(0,t.FD)("defs",{children:[(0,t.FD)("linearGradient",{id:"IconEmptyFolder__b",x1:90,y1:79.156,x2:90,y2:-13.45,gradientUnits:"userSpaceOnUse",children:[(0,t.Y)("stop",{stopColor:"#DEDEDE",stopOpacity:0}),(0,t.Y)("stop",{offset:1,stopColor:"#D3D3D3",stopOpacity:.6})]}),(0,t.Y)("clipPath",{id:"IconEmptyFolder__a",children:(0,t.Y)("path",{fill:r.whiteColor||e.whiteColor,d:"M0 0h180v114.94H0z"})})]})]})}))},28349:(r,o,e)=>{e.d(o,{E:()=>t});const t=e(93345).forwardRef},45064:(r,o,e)=>{if(e.d(o,{DP:()=>p,NP:()=>u}),4871==e.j)var t=e(74389);var n=e(40570),a=e(74667),i=e(93345),l=e(33212);if(4871==e.j)var c=e(29568);if(4871==e.j)var s=e(78234);const d=(0,i.createContext)(null),u=r=>{const o=(0,i.useMemo)((()=>(0,s.D)(r.value)),[r.value]),e=(0,c.D)(o),u=(0,i.useMemo)((()=>({accentColor:o.primaryColor,successColor:o.successColor,warningColor:o.warningColor,errorColor:o.errorColor,whiteColor:o.backgroundColor,lightGrayColor:o.grayScale[5],darkGrayColor:o.grayScale[7]})),[o]);return(0,t.Y)(d.Provider,{value:o,children:(0,t.Y)(a.ConfigProvider,{theme:e,children:(0,t.Y)(l.IconThemeContext.Provider,{value:u,children:(0,t.Y)(a.App,{className:r.className,css:n.css`
              box-sizing: border-box;
              font-size: ${e.token?.fontSizeSM}px;
              line-height: ${e.token?.lineHeight};
              font-family: ${e.token?.fontFamily};
              color: ${e.token?.colorText};
              background-color: ${e.token?.colorBgBase};
              color-scheme: ${o.isDark?"dark":"light"};

              *,
              *:before,
              *:after {
                box-sizing: inherit;
              }
              .ant-select-tree-list-scrollbar {
                visibility: visible !important;
              }
              .rc-virtual-list-scrollbar,
              .ant-select-tree-list-scrollbar {
                width: 10px !important;
              }
              *::-webkit-scrollbar {
                width: 10px;
                height: 10px;
              }
              *::-webkit-scrollbar-thumb,
              .rc-virtual-list-scrollbar-thumb,
              .ant-select-tree-list-scrollbar-thumb {
                background-color: ${o.grayScale[5]}!important;
                border-radius: 2px !important;
              }
              *::-webkit-scrollbar-thumb:hover,
              .rc-virtual-list-scrollbar-thumb:hover,
              .ant-select-tree-list-scrollbar-thumb:hover {
                background-color: ${o.grayScale[6]}!important;
              }
              *::-webkit-scrollbar-track {
                background-color: transparent;
              }
              *::-webkit-scrollbar-track:hover,
              .rc-virtual-list-scrollbar:hover,
              .ant-select-tree-list-scrollbar:hover {
                background-color: ${o.grayScale[3]};
              }
              *::-webkit-scrollbar-button {
                display: none;
              }

              .aui-invisible-scrollbars {
                scrollbar-width: none;
              }
              .aui-invisible-scrollbars::-webkit-scrollbar {
                display: none;
              }

              .ant-picker-dropdown {
                padding: 0;
              }
              .ant-picker-range-arrow {
                ::before,
                ::after {
                  display: none;
                }
              }

              .ant-modal-footer {
                padding-inline: ${e.components?.Modal?.paddingLG}px!important;
              }

              .ant-popconfirm-buttons {
                padding-top: ${e.components?.Popconfirm?.paddingXXS}px!important;
              }

              .ant-popover {
                .ant-popover-title {
                  border-bottom: 0px;
                }

                .ant-popover-inner-content {
                  padding: 6px 12px 10px 12px;
                }
              }

              button,
              input {
                font-family: inherit;
                line-height: inherit;
                font-size: inherit;
              }

              input[type="checkbox"] {
                margin: 0;
              }

              fieldset {
                border: none;
              }

              g.pointtext {
                display: none;
              }

              /*
           * TODO Remove when upgrading Ant Design.
           * This is an Ant Design bug fixed in https://github.com/ant-design/ant-design/commit/467741f5.
           */
              .ant-dropdown-menu-sub {
                margin: 0;
              }
            `,children:r.children})})})})};function p(){const r=(0,i.useContext)(d);if(!r)throw new Error("Missing theme. Remember to add <ThemeProvider /> at the top of your application.");return r}},28673:(r,o,e)=>{if(e.d(o,{O:()=>l}),4871==e.j)var t=e(24430);if(4871==e.j)var n=e(26590);if(4871==e.j)var a=e(54815);const i=4871==e.j?["transparent",void 0,null]:null,l=function(r,o,e){if(i.includes(r)&&o)return(0,n.J)((0,t.p)(o),e);if(i.includes(o)&&r)return(0,n.J)((0,t.p)(r),e);if(r&&o){const n=(0,t.p)(r),i=(0,t.p)(o);return(0,a.e)(function(r,...o){return o[0].map(((e,t)=>r(...o.map((r=>r[t])))))}(((r,o)=>Math.ceil((1-e)*r+e*o)),n,i))}throw new Error("Invalid arguments to addColorLayer")}},17759:(r,o,e)=>{e.d(o,{e:()=>i});var t=e(24430),n=e(26590);const a=/\d+(\.\d*)?|\.\d+/g,i=function({color:r,opacity:o,shadeFactor:e=0,isShading:i,isInverting:l}){const c=(0,t.p)(r),s=r.startsWith("rgba")?(r=>{const o=r.match(a);if(!o)throw new SyntaxError("Invalid rgba parameter");return Number.parseFloat(o.slice(3).join(""))})(r):1;return(0,n.J)(c.map((r=>{const o=l?(r=>255-r)(r):r;return t=i?o*(1-e):o+(255-o)*e,Math.max(0,Math.min(255,t));var t})),(d=s*o,Math.max(0,Math.min(1,d))));var d}},41769:(r,o,e)=>{if(e.d(o,{w:()=>n}),4871==e.j)var t=e(28673);const n=(r,o)=>{const e=e=>(0,t.O)(r,o,e);return[e(0),e(.02),e(.04),e(.06),e(.09),e(.15),e(.25),e(.45),e(.55),e(.65),e(.75),e(.85),e(.95),e(1)]}},29568:(r,o,e)=>{e.d(o,{D:()=>n});var t=e(74667);function n(r){return{token:{lineHeight:1.66667,fontSizeSM:12,fontFamily:"-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, Noto Sans, sans-serif, Apple Color Emoji, Segoe UI Emoji, Segoe UI Symbol, Noto Color Emoji",borderRadius:2,controlOutlineWidth:0,colorPrimary:r.primaryColor,colorSuccess:r.successColor,colorWarning:r.warningColor,colorText:r.textColor,colorTextPlaceholder:r.placeholderColor,colorTextDisabled:r.disabledTextColor,colorBgBase:r.backgroundColor,colorPrimaryBg:r.selectedMenuItemBackground,colorBgContainerDisabled:r.disabledBackground,colorBorder:r.cellBorderColor,colorBorderSecondary:r.cellBorderColor},components:{Menu:{radiusItem:0,radiusSubMenuItem:0,lineWidth:.5,margin:12,controlHeightLG:32,colorActiveBarBorderSize:0,activeBarWidth:3,itemSelectedColor:r.primaryColor,subMenuItemBg:r.menuInlineSubmenuBg},Tooltip:{paddingXS:8,paddingSM:12},Checkbox:{paddingXS:8},Modal:{wireframe:!0,paddingXS:8,marginXS:8,padding:11,paddingLG:16},Popover:{wireframe:!0,padding:12,paddingSM:12},Popconfirm:{marginXS:8,paddingXXS:4},Card:{padding:8.5,paddingLG:12,fontWeightStrong:500},Dropdown:{marginXS:8,controlPaddingHorizontal:8},Tabs:{colorText:r.grayScale[8],colorFillAlter:r.grayScale[3]}},algorithm:[t.theme.compactAlgorithm,...r.isDark?[t.theme.darkAlgorithm]:[],(r,o=t.theme.defaultAlgorithm(r))=>({...o,colorInfo:r.colorPrimary,colorBgContainer:r.colorBgBase,colorBgElevated:r.colorBgBase,colorBgLayout:r.colorBgBase})]}}},78234:(r,o,e)=>{e.d(o,{D:()=>S});var t=e(18956),n=e(57358),a=2,i=.16,l=.05,c=.05,s=.15,d=5,u=4,p=[{index:7,opacity:.15},{index:6,opacity:.25},{index:5,opacity:.3},{index:5,opacity:.45},{index:5,opacity:.65},{index:5,opacity:.85},{index:4,opacity:.9},{index:3,opacity:.95},{index:2,opacity:.97},{index:1,opacity:.98}];function h(r){var o=r.r,e=r.g,n=r.b,a=(0,t.wE)(o,e,n);return{h:360*a.h,s:a.s,v:a.v}}function g(r){var o=r.r,e=r.g,n=r.b;return"#".concat((0,t.Ob)(o,e,n,!1))}function m(r,o,e){var t;return(t=Math.round(r.h)>=60&&Math.round(r.h)<=240?e?Math.round(r.h)-a*o:Math.round(r.h)+a*o:e?Math.round(r.h)+a*o:Math.round(r.h)-a*o)<0?t+=360:t>=360&&(t-=360),t}function b(r,o,e){return 0===r.h&&0===r.s?r.s:((t=e?r.s-i*o:o===u?r.s+i:r.s+l*o)>1&&(t=1),e&&o===d&&t>.1&&(t=.1),t<.06&&(t=.06),Number(t.toFixed(2)));var t}function f(r,o,e){var t;return(t=e?r.v+c*o:r.v-s*o)>1&&(t=1),Number(t.toFixed(2))}function C(r){for(var o=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},e=[],t=(0,n.RO)(r),a=d;a>0;a-=1){var i=h(t),l=g((0,n.RO)({h:m(i,a,!0),s:b(i,a,!0),v:f(i,a,!0)}));e.push(l)}e.push(g(t));for(var c=1;c<=u;c+=1){var s=h(t),C=g((0,n.RO)({h:m(s,c),s:b(s,c),v:f(s,c)}));e.push(C)}return"dark"===o.theme?p.map((function(r){var t,a,i,l=r.index,c=r.opacity;return g((t=(0,n.RO)(o.backgroundColor||"#141414"),i=100*c/100,{r:((a=(0,n.RO)(e[l])).r-t.r)*i+t.r,g:(a.g-t.g)*i+t.g,b:(a.b-t.b)*i+t.b}))})):e}var v={red:"#F5222D",volcano:"#FA541C",orange:"#FA8C16",gold:"#FAAD14",yellow:"#FADB14",lime:"#A0D911",green:"#52C41A",cyan:"#13C2C2",blue:"#1890FF",geekblue:"#2F54EB",purple:"#722ED1",magenta:"#EB2F96",grey:"#666666"},y={},k={};Object.keys(v).forEach((function(r){y[r]=C(v[r]),y[r].primary=y[r][5],k[r]=C(v[r],{theme:"dark",backgroundColor:"#141414"}),k[r].primary=k[r][5]})),y.red,y.volcano,y.gold,y.orange,y.yellow,y.lime,y.green,y.cyan,y.blue,y.geekblue,y.purple,y.magenta,y.grey;var w=e(41769),x=e(76686),B=e(53242),F=e(8923);function S(r){const o=!r.isDark,e=r.white??o?"#FFFFFF":"#000000",t=r.black??o?"#000000":"#FFFFFF",n=r.backgroundColor??e,a=(0,w.w)(n,t),i=(0,F.k)([(0,B.z)(r.primaryColor)[0],"100","50"]),l=r.successColor??"#52C41A",c=r.errorColor??"#F5222D",s=C(r.primaryColor,{theme:o?"default":"dark",backgroundColor:n});return{activeMenuItemBackgroundColor:a[4],activeTabBackgroundColor:a[0],alternateCellBackgroundColor:(0,x.j)(a[2],.65),alternateBackgroundColor:a[1],backgroundColor:n,black:t,cellBackgroundDuringNegativeTransition:(0,x.j)(c,.7),cellBackgroundDuringPositiveTransition:(0,x.j)(l,.7),cellBorderColor:a[5],headerActiveColor:r.primaryColor,disabledBackground:o?"#F5F5F5":n,disabledTextColor:o?(0,x.j)(t,.35):(0,x.j)(t,.25),dropHintBorderColor:(0,x.j)(i,.2),dropHintColor:(0,x.j)(i,.15),errorColor:c,grayScale:a,hoverColor:s[5],inactiveTabBackgroundColor:a[2],menuInlineSubmenuBg:"transparent",placeholderColor:a[6],primaryScale:s,selectedMenuItemBackground:s[0],selectionOverlayColor:(0,x.j)(i,.1),selectionMarkDarkColor:"#646464",selectionMarkLightColor:"#FFFFFF",selectionColor:s[0],shadowColor:"#000C11",successColor:l,textColor:o?a[11]:(0,x.j)(t,.65),warningColor:"#FAAD14",white:e,...r}}},24430:(r,o,e)=>{function t(r,o,e){const t=(e+1)%1;return t<1/6?r+6*(o-r)*t:t<.5?o:t<2/3?r+(o-r)*(2/3-t)*6:r}e.d(o,{p:()=>i});const n=/\d+/g,a=/\d+(\.\d*)?|\.\d+/g,i=function(r){const o=r.toLowerCase();if(o.startsWith("#"))return function(r){if(6!==r.length&&3!==r.length)throw new Error(`Hex color (${r}) is not a valid 3 or 6 character string`);const o=6===r.length?r:r.charAt(0).repeat(2)+r.charAt(1).repeat(2)+r.charAt(2).repeat(2);return[Number.parseInt(o.slice(0,2),16),Number.parseInt(o.slice(2,4),16),Number.parseInt(o.slice(4,6),16)]}(r.slice(1));if(o.startsWith("rgb"))return(r=>{const o=r.match(n);if(!o)throw new SyntaxError("Invalid rgb parameter");const e=o.slice(0,3).map((r=>Number(r)));return[e[0],e[1],e[2]]})(r);if(o.startsWith("hsl"))return(r=>{const o=r.match(a);if(!o)throw new SyntaxError("Invalid hsl parameter");const e=o.slice(0,3).map((r=>Number(r)));return function(r,o,e){let n,a,i;const l=r/360,c=o/100,s=e/100;if(0===c)i=s,a=s,n=s;else{const r=s<.5?s*(1+c):s+c-s*c,o=2*s-r;n=t(o,r,l+1/3),a=t(o,r,l),i=t(o,r,l-1/3)}return n=Math.round(255*n),a=Math.round(255*a),i=Math.round(255*i),[n,a,i]}(e[0],e[1],e[2])})(r);throw new Error("Unsupported color syntax. Supported syntaxes are rgb, hsl and hex.")}},76686:(r,o,e)=>{e.d(o,{j:()=>n});var t=e(17759);function n(r,o=1){return(0,t.e)({color:r,opacity:o})}},47353:(r,o,e)=>{function t(r,o,e){const t=r/255,n=o/255,a=e/255,i=Math.max(t,n,a),l=Math.min(t,n,a);let c=0,s=0,d=(i+l)/2;if(i!==l){const r=i-l;switch(s=d>.5?r/(2-i-l):r/(i+l),i){case t:c=(n-a)/r+(n<a?6:0);break;case n:c=(a-t)/r+2;break;case a:c=(t-n)/r+4}c/=6}return c=Math.round(360*c),s=Math.round(100*s),d=Math.round(100*d),[c,s,d]}e.d(o,{K:()=>t})},53242:(r,o,e)=>{if(e.d(o,{z:()=>a}),4871==e.j)var t=e(24430);if(4871==e.j)var n=e(47353);function a(r){return(0,n.K)(...(0,t.p)(r))}},8923:(r,o,e)=>{function t(r){return`hsl(${r[0]}, ${r[1]}%, ${r[2]}%)`}e.d(o,{k:()=>t})},26590:(r,o,e)=>{e.d(o,{J:()=>t});const t=function(r,o){return`rgba(${r.join(", ")}, ${o})`}},54815:(r,o,e)=>{e.d(o,{e:()=>t});const t=function(r){return`rgb(${r.join(", ")})`}},25027:(r,o,e)=>{e.d(o,{l:()=>n});const t=new Set;function n(r,o){t.has(r)||(t.add(r),console.warn(`%c ${r} `,"font-style: italic; border: 1px solid orange; border-radius: 5px","is deprecated and will not be supported in the next breaking release of Atoti UI.",o))}}}]);