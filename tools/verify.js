// 사용: node tools/verify.js
// index.html 기준으로 항목 수, 썸네일 파일 존재 여부, URL 중복을 확인한다.
const fs = require('fs');
const s = fs.readFileSync('index.html', 'utf8');
const m = s.match(/var ITEMS = (\[[\s\S]*?\n  \]);/);
const a = eval(m[1]);
let bad = 0;
a.forEach(x => { if (x.thumb && !fs.existsSync(x.thumb)) { console.log('MISSING', x.thumb); bad++; } });
const u = a.map(x => x.url);
console.log('count', a.length, 'missingThumbs', bad, 'dupUrls', u.length - new Set(u).size);
