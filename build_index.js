// Build self-contained index.html with inline stock data
const fs = require('fs');

const json = fs.readFileSync('data/stock_data.json', 'utf-8');
let html = fs.readFileSync('index.html', 'utf-8');

// Inject data block before </head>
const dataBlock = '\n<script>window.STOCK_DATA=' + json + ';</script>\n';
html = html.replace('</head>', dataBlock + '</head>');

// Replace loadCSV function
const oldLoadCSV = `async function loadCSV(filename) {
  const resp = await fetch('data/'+filename);
  const text = await resp.text();
  const lines = text.trim().split('\\n');
  if (lines.length<2) return [];
  // Detect BOM and header
  let header = lines[0].replace(/^﻿/,'').split(',');
  // Map columns: we need trade_date, open, high, low, close
  const dateIdx = header.findIndex(h=>h.toLowerCase().includes('trade_date')||h.toLowerCase()==='date');
  const openIdx = header.findIndex(h=>h.toLowerCase()==='open');
  const highIdx = header.findIndex(h=>h.toLowerCase()==='high');
  const lowIdx = header.findIndex(h=>h.toLowerCase()==='low');
  const closeIdx = header.findIndex(h=>h.toLowerCase()==='close');

  const data = [];
  for (let i=1; i<lines.length; i++) {
    const cols = lines[i].split(',');
    const dateStr = cols[dateIdx];
    // Parse date (handle both 2025-07-04 and 20250704)
    let date;
    if (dateStr.includes('-')) {
      date = new Date(dateStr+'T00:00:00');
    } else {
      const d=dateStr.trim();
      date = new Date(d.slice(0,4)+'-'+d.slice(4,6)+'-'+d.slice(6,8)+'T00:00:00');
    }
    if (isNaN(date.getTime())) continue;
    data.push({
      date: date.toISOString().split('T')[0],
      open: parseFloat(cols[openIdx]),
      high: parseFloat(cols[highIdx]),
      low: parseFloat(cols[lowIdx]),
      close: parseFloat(cols[closeIdx]),
    });
  }
  return data.sort((a,b)=>a.date.localeCompare(b.date));`;

const newLoadCSV = `async function loadCSV(filename) {
  const key = filename.replace('_daily.csv','');
  const raw = window.STOCK_DATA[key];
  if (!raw) return [];
  return raw.map(function(r){return {date:r[0],open:r[1],high:r[2],low:r[3],close:r[4]};});`;

html = html.replace(oldLoadCSV, newLoadCSV);

fs.writeFileSync('index.html', html);
console.log('index.html updated. Size: ' + (fs.statSync('index.html').size/1024).toFixed(0) + ' KB');
