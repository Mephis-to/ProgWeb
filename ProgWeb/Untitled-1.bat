const http = require('node:http');

const courses = [
  { slug: 'html-basics', title: 'HTML Basics', description: 'Learn page structure, semantic elements, links, images, and forms.' },
  { slug: 'html-accessibility', title: 'Accessible HTML', description: 'Create inclusive pages with semantic markup and accessible forms.' },
];

const escapeHtml = (text) => String(text).replace(/[&<>"']/g, (char) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
})[char]);

function renderPage(title, body) {
  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${escapeHtml(title)} | HTML Courses</title></head>
<body><header><a href="/">HTML Courses</a></header><main>${body}</main></body></html>`;
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url, 'http://localhost');
  res.setHeader('X-Content-Type-Options', 'nosniff');

  if (req.method !== 'GET') {
    res.writeHead(405, { Allow: 'GET' });
    return res.end('Method not allowed');
  }
  if (url.pathname === '/api/courses') {
    res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
    return res.end(JSON.stringify(courses));
  }
  if (url.pathname === '/') {
    const list = courses.map((course) => `<li><a href="/courses/${course.slug}">${escapeHtml(course.title)}</a> — ${escapeHtml(course.description)}</li>`).join('');
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    return res.end(renderPage('Courses', `<h1>HTML Courses</h1><ul>${list}</ul>`));
  }
  const match = url.pathname.match(/^\/courses\/([a-z0-9-]+)$/);
  const course = match && courses.find((item) => item.slug === match[1]);
  if (course) {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    return res.end(renderPage(course.title, `<h1>${escapeHtml(course.title)}</h1><p>${escapeHtml(course.description)}</p><a href="/">All courses</a>`));
  }
  res.writeHead(404, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(renderPage('Not found', '<h1>Course not found</h1><a href="/">Browse courses</a>'));
});

const port = Number(process.env.PORT) || 3000;
server.listen(port, () => console.log(`HTML courses server: http://localhost:${port}`));
