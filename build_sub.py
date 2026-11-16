import sys, pathlib
HEAD = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | Sher Badshah</title>
<link rel="stylesheet" href="../style.css">
</head>
<body>
<nav class="navbar"><div class="inner">
  <a class="brand" href="../index.html">Sher Badshah</a>
  <ul>
    <li><a href="../index.html">Home</a></li>
    <li><a {a_about}href="../about/index.html">About</a></li>
    <li><a {a_papers}href="../papers/index.html">Papers</a></li>
    <li><a {a_teaching}href="../teaching/index.html">Teaching</a></li>
    <li><a href="../files/sher_badshah_cv.pdf">CV</a></li>
  </ul>
</div></nav>
<div class="page">
<main>
<h1>{title}</h1>
'''
TAIL = '''</main>
<aside class="toc"><h6>On this page</h6><ul>
{toc}
</ul></aside>
</div>
<footer><div class="inner">© 2026 Sher Badshah</div></footer>
</body>
</html>
'''
import re
for name, title in [("about","About"),("papers","Papers"),("teaching","Teaching")]:
    body = pathlib.Path(f"_src/{name}.html").read_text()
    toc = "\n".join(f'<li><a href="#{i}">{t}</a></li>' for i,t in re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body))
    act = {f"a_{n}": ('class="active" ' if n==name else '') for n in ["about","papers","teaching"]}
    pathlib.Path(f"{name}/index.html").write_text(HEAD.format(title=title, **act) + body + TAIL.format(toc=toc))
