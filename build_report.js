// Build self-contained report.html with inline stock data
const fs = require('fs');

// 1. Read JSON data generated from CSVs
const json = fs.readFileSync('data/stock_data.json', 'utf-8');
const stocks = JSON.parse(json);

// 2. Read report template
let html = fs.readFileSync('report.html', 'utf-8');

// 3. Inject data block before </head>
const dataBlock = '\n<script>window.STOCK_DATA=' + JSON.stringify(stocks) + ';</script>\n';
html = html.replace('</head>', dataBlock + '</head>');

// 4. Replace loadCSV function to use inline data instead of fetch
const oldLoadCSV = `async function loadCSV(fn){
  const r=await fetch('data/'+fn);const t=await r.text();const ls=t.trim().split('\\n');if(ls.length<2)return[];
  const h=ls[0].replace(/^﻿/,'').split(',');
  const di=h.findIndex(c=>c.toLowerCase().includes('trade_date')||c.toLowerCase()==='date');
  const oi=h.findIndex(c=>c.toLowerCase()==='open'),hi=h.findIndex(c=>c.toLowerCase()==='high');
  const li=h.findIndex(c=>c.toLowerCase()==='low'),ci=h.findIndex(c=>c.toLowerCase()==='close');
  const d=[];for(let i=1;i<ls.length;i++){const cs=ls[i].split(',');const ds=cs[di];
    let dt;if(ds.includes('-'))dt=new Date(ds+'T00:00:00');else{const x=ds.trim();dt=new Date(x.slice(0,4)+'-'+x.slice(4,6)+'-'+x.slice(6,8)+'T00:00:00');}
    if(isNaN(dt.getTime()))continue;
    d.push({date:dt.toISOString().split('T')[0],open:+cs[oi],high:+cs[hi],low:+cs[li],close:+cs[ci]});}
  return d.sort((a,b)=>a.date.localeCompare(b.date));
}`;

const newLoadCSV = `async function loadCSV(fn){
  const key = fn.replace('_daily.csv','');
  const raw = window.STOCK_DATA[key];
  if (!raw) return [];
  return raw.map(function(r){return {date:r[0],open:r[1],high:r[2],low:r[3],close:r[4]};});
}`;

html = html.replace(oldLoadCSV, newLoadCSV);

// 5. Write output
fs.writeFileSync('report.html', html);
const sizeKB = (fs.statSync('report.html').size / 1024).toFixed(0);
console.log('Done. report.html size: ' + sizeKB + ' KB');
