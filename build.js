/*
 * build.js — يُنتج نسخة مستقلة بملف واحد من الموقع.
 *
 *   node build.js
 *
 * المخرجات:
 *   dist/index.html    صفحة كاملة تعمل بمفردها (بلا ملفات جانبية)
 *   dist/artifact.html محتوى الصفحة فقط (للنشر كـ Artifact)
 *
 * الصور والأنماط والسكربت تُدمج داخل الملف، وخطوط جوجل تبقى رابطاً خارجياً.
 */
const fs = require('fs');
const path = require('path');

const root = __dirname;
const read = (p) => fs.readFileSync(path.join(root, p), 'utf8');
const dataUri = (p, mime) =>
  'data:' + mime + ';base64,' + fs.readFileSync(path.join(root, p)).toString('base64');

const html = read('index.html');
const css = read('assets/css/style.css');
const js = read('assets/js/app.js');

const logo = dataUri('assets/img/logo.jpg', 'image/jpeg');
const logo2x = dataUri('assets/img/logo@2x.png', 'image/png');
const favicon = dataUri('assets/img/favicon.png', 'image/png');
const favicon32 = dataUri('assets/img/favicon-32.png', 'image/png');

/* split/join وليس replace: نص البديل قد يحتوي $$ فيفسده محرك الاستبدال */
let out = html
  .split('<link rel="stylesheet" href="assets/css/style.css">').join('<style>\n' + css + '\n</style>')
  .split('<script src="assets/js/app.js"></script>').join('<script>\n' + js + '\n</script>')
  .split('assets/img/logo@2x.png').join(logo2x)
  .split('assets/img/favicon-32.png').join(favicon32)
  .split('assets/img/favicon.png').join(favicon)
  .split('assets/img/logo.jpg').join(logo);

fs.mkdirSync(path.join(root, 'dist'), { recursive: true });
fs.writeFileSync(path.join(root, 'dist/index.html'), out, 'utf8');

/* نسخة الـ Artifact: بلا doctype/html/head/body — تُغلَّف عند النشر */
const head = out.slice(out.indexOf('<head>') + 6, out.indexOf('</head>'));
const body = out.slice(out.indexOf('<body>') + 6, out.lastIndexOf('</body>'));

/* اسم أقصر داخل معرض الـ Artifacts */
const artifact =
  '<title>مكتب عقار اليوم للعقارات</title>' + '\n' +
  head.match(/<link rel="preconnect"[\s\S]*?display=swap">/)[0] + '\n' +
  head.match(/<style>[\s\S]*?<\/style>/)[0] + '\n' +
  '<div dir="rtl" lang="ar" class="aqar-root">\n' + body + '\n</div>';

fs.writeFileSync(path.join(root, 'dist/artifact.html'), artifact, 'utf8');

const kb = (s) => (Buffer.byteLength(s, 'utf8') / 1024).toFixed(0) + ' KB';
console.log('dist/index.html    ' + kb(out));
console.log('dist/artifact.html ' + kb(artifact));
