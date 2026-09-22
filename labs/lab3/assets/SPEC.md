# SPEC: Developer Portfolio Welcome Page
## 1. Purpose & Scope
- A personal portfolio welcome page for <Luis Emilio Amezquita Zapata>, a second-year software
engineering student.
- Non-Goals: no multi-page routing; no backend; no contact forms.
## 2. Invariants & Negative Constraints
- All styling MUST reside in `./style.css` (no inline style="..." attributes).
- The page MUST NOT load external CSS frameworks or CDNs (no Bootstrap, no Tailwind).
- The avatar image MUST use the relative path `./lab3/assets/avatar.png`.
- The layout MUST collapse into a single vertical column on screens narrower than 768px.
## 3. UI Content & Interface Contract
- Hero header: my full name "<Luis Emilio Amezquita Zapata>", the subtitle "<I am a triplet>", and
this bio: "<Student athlete at Stevens Institute of Technology. Aspirations of working as a robotic engineering making robots with well developed software.>".
- Action link: a button labelled "See my projects" that links to `#projects`.
- Projects section with id="projects": lists these items: <I want to make a website for people to use to help with their day to day lives>.
- Social link: GitHub (<https://github.com/luisemilio098>) MUST open in a new tab
(target="_blank").
## 4. Acceptance Checklist
- [ ] Valid semantic HTML5: the page uses <header>, <main>, and <footer>.
- [ ] The avatar image has width, height, and alt attributes.
- [ ] No horizontal scrollbar when the browser is narrowed to 375px.
- [ ] The GitHub link opens in a new tab and has rel="noopener".
- [ ] No placeholder links: href="#" appears nowhere.
## 5. Audit Protocol
- Inspect the generated code line by line with `git diff --staged` before committing.