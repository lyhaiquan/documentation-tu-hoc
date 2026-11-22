
(function(){
"use strict";
var KEY="giaoan-theo-mon-v1", TOTAL=197;
var st={start:"2026-11-23",done:{}};
try{var raw=localStorage.getItem(KEY);if(raw){var o=JSON.parse(raw);if(o&&typeof o==="object"){if(o.start)st.start=o.start;if(o.done)st.done=o.done;}}}catch(e){}
function save(){try{localStorage.setItem(KEY,JSON.stringify(st));}catch(e){}}
var WD=["T2","T3","T4","T5","T6","T7","CN"];
function pad(n){return n<10?"0"+n:""+n}
function addDays(d,n){var x=new Date(d.getTime());x.setDate(x.getDate()+n);return x}
function fmt(d){return pad(d.getDate())+"/"+pad(d.getMonth()+1)}
function parse(s){var p=(s||"").split("-");if(p.length!==3)return null;var d=new Date(+p[0],+p[1]-1,+p[2]);return isNaN(d.getTime())?null:d}
function monday(d){var x=new Date(d.getFullYear(),d.getMonth(),d.getDate());var k=(x.getDay()+6)%7;return addDays(x,-k)}
var startEl=document.getElementById("start");
startEl.value=st.start;
function dates(){
  var s=parse(st.start)||new Date();var m=monday(s);
  var wks=document.querySelectorAll("details.wk");
  for(var i=0;i<wks.length;i++){
    var w=+wks[i].getAttribute("data-w"),b=addDays(m,(w-1)*7);
    wks[i].querySelector(".rg").textContent=fmt(b)+" – "+fmt(addDays(b,6));
    var ds=wks[i].querySelectorAll(".day");
    for(var j=0;j<ds.length;j++){var d=+ds[j].getAttribute("data-d");ds[j].querySelector(".dt").textContent=fmt(addDays(b,d));}
    var sn=wks[i].querySelector(".sun");if(sn)sn.querySelector(".dt").textContent=fmt(addDays(b,6));
  }
}
function refresh(){
  var cbs=document.querySelectorAll(".day input[type=checkbox]"),n=0;
  for(var i=0;i<cbs.length;i++){
    var id=cbs[i].getAttribute("data-id"),on=!!st.done[id];cbs[i].checked=on;if(on)n++;
    cbs[i].closest(".day").classList.toggle("done",on);
  }
  var p=Math.round(100*n/TOTAL);
  document.getElementById("mt").style.width=p+"%";document.getElementById("pct").textContent=n+"/"+TOTAL+" ("+p+"%)";
  var wks=document.querySelectorAll("details.wk");
  for(var k=0;k<wks.length;k++){
    var ds=wks[k].querySelectorAll(".day"),c=0;
    for(var j=0;j<ds.length;j++){if(st.done[ds[j].querySelector("input").getAttribute("data-id")])c++;}
    wks[k].querySelector(".pc").textContent=c+"/"+ds.length;
  }
}
document.addEventListener("change",function(e){
  var t=e.target;if(t&&t.matches&&t.matches(".day input[type=checkbox]")){
    var id=t.getAttribute("data-id");if(t.checked)st.done[id]=1;else delete st.done[id];save();refresh();}
});
startEl.addEventListener("change",function(){if(parse(startEl.value)){st.start=startEl.value;save();dates();markToday();}});
document.getElementById("reset").addEventListener("click",function(){if(confirm("Xoá toàn bộ tiến độ đã đánh dấu?")){st.done={};save();refresh();}});
var cur="ALL";
document.getElementById("flt").addEventListener("click",function(e){
  var b=e.target.closest("button");if(!b)return;cur=b.getAttribute("data-s");
  var bs=this.querySelectorAll("button");for(var i=0;i<bs.length;i++){bs[i].classList.toggle("on",bs[i]===b);}
  var ds=document.querySelectorAll(".day");
  for(var j=0;j<ds.length;j++){ds[j].classList.toggle("hide",cur!=="ALL"&&ds[j].getAttribute("data-s")!==cur);}
  var sn=document.querySelectorAll(".sun");for(var k=0;k<sn.length;k++){sn[k].classList.toggle("hide",cur!=="ALL");}
  if(cur!=="ALL"){var wks=document.querySelectorAll("details.wk");for(var m=0;m<wks.length;m++){wks[m].open=!!wks[m].querySelector(".day:not(.hide)");}}
});
function markToday(){
  var old=document.querySelector(".day.today");if(old)old.classList.remove("today");
  var s=parse(st.start);if(!s)return null;var m=monday(s);var now=new Date();now=new Date(now.getFullYear(),now.getMonth(),now.getDate());
  var diff=Math.round((now-m)/86400000);if(diff<0)return null;
  var w=Math.floor(diff/7)+1,d=diff%7;if(d>5)return document.getElementById("w-"+w);
  var el=document.querySelector('.day[data-w="'+w+'"][data-d="'+d+'"]');if(el){el.classList.add("today");return el;}
  return document.getElementById("w-"+w);
}
document.getElementById("goto").addEventListener("click",function(){
  var el=markToday();
  if(!el){var first=document.querySelector(".day:not(.done)");el=first;}
  if(el){var w=el.closest("details.wk");if(w)w.open=true;el.scrollIntoView({behavior:"smooth",block:"center"});}
});
dates();refresh();
var t=markToday();
var firstOpen=t&&t.closest?t.closest("details.wk"):null;
if(!firstOpen){var nd=document.querySelector(".day:not(.done)");firstOpen=nd?nd.closest("details.wk"):document.querySelector("details.wk");}
if(firstOpen)firstOpen.open=true;
if(location.hash){var h=document.getElementById(location.hash.slice(1));if(h){var ww=h.closest("details.wk");if(ww)ww.open=true;}}
})();
