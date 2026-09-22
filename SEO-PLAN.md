# EntrixII — SEO changes and next steps

## The big one
Every `/services/<slug>` page (12 pages, all listed in your sitemap at top priority) was returning **HTTP 500**.
`service_detail.html` used a Python-style list comprehension inside Jinja, which Jinja does not support.
FAQ schema is now built in Python (`faq_schema()` in `app.py`). All pages now return 200.

## What changed

**Crawlability / indexing**
- Sitemap: honest `<lastmod>` (was "today" on every request), `become-agent` added, `changefreq`/`priority` dropped (Google ignores them).
- One URL per page: 301 for `www` -> apex, `http` -> `https` (only when the proxy sends `X-Forwarded-Proto: http`), and trailing slash -> no slash.
- Private pages (`/admin*`, `/agent-login`, `/agent-register`, `/agent-pending`, `/agent-dashboard`): `noindex` meta + `X-Robots-Tag` header. Login pages are deliberately *not* blocked in robots.txt so Google can read the noindex.
- Real 404 page now used (Flask was showing its default one), with `noindex`.
- `/favicon.ico` route (Google requests it by default), web manifest, PNG icons, apple-touch-icon.
- Removed the three identical `hreflang` tags (single-language site; they added nothing).

**On-page**
- Clean one-line `<title>`/description on every page; no duplicates; lengths tuned to SERP limits.
- Homepage title + hero now say Nigeria/Africa and use the "Entrix II" brand consistently.
- Homepage service cards now link to their service pages (they were plain text).
- Sitewide footer link block to every service, location, industry and guide.
- Heading hierarchy fixed (cards/FAQs were `h2` under `h2`); `work`/`contact` H1s now descriptive.
- Contact page now shows email, phone/WhatsApp and service area (trust + local signals).
- Service pages: audience, project process, related guides, cross-links to locations/industries.

**Structured data (all validated as JSON)**
- Organization + WebSite in one `@graph` with `@id`s, `alternateName` (Entrix / EntrixII), phone, area served.
- `BreadcrumbList` on every inner page; `Service`, `Article` (with dates), `FAQPage`, `CollectionPage`, `ContactPage`, `CreativeWork`.

**Content**
- 5 new long-form guides (`seo_content.py`) on real search topics: website vs web app vs mobile app, getting indexed on Google, Google Business Profile, build timelines, .com.ng vs .ng vs .com. Each has FAQs, table of contents and internal links.

**Speed / Core Web Vitals**
- Portfolio images converted to WebP: about 1.7 MB -> about 140 KB, with width/height set (no layout shift).
- Google Fonts no longer render-blocking; `<noscript>` fallback also hides the loader for no-JS visitors.
- Static files are cache-busted (`?v=`) and cached for a year; gzip/brotli via Flask-Compress (optional import).
- Proper 1200x630 social share image.

## Deploy
1. Copy these files over your project (they replace the originals).
2. `pip install -r requirements.txt`
3. Delete: root `robots.txt`, root `sitemap.xml`, `app.py.tmp`, `static/images/crownbee.jpg`, `jacyani.jpg`, `michieplus.jpg` (unused now).
4. Confirm `google1236e1335ed123fa.html` exists next to `app.py` (it was not in the zip; the verification route serves it).
5. Deploy, then open `/sitemap.xml`, `/robots.txt` and a few `/services/...` pages.

## Do this in the first week
- Google Search Console: add the domain property, submit `https://entrixii.com.ng/sitemap.xml`, request indexing for the homepage, `/services` and 3-4 service pages.
- Bing Webmaster Tools: import from Search Console.
- Google Business Profile (see the guide on your own site) with the same name, phone and website as the contact page.
- Ask the owners of your live client sites to add a "Website by Entrix II" link in their footer pointing to your homepage. Relevant links from real client sites are the most valuable off-page signal you can get quickly.
- Complete LinkedIn, Instagram, X and GitHub bios with the same name, description and URL.

## Trust and content (biggest remaining lever)
- Name the founder and add a short bio + photo on `/about`, then add `Person` schema. Google's quality guidelines weigh who is behind a site.
- Make sure every claim on `/work` is true. Case studies for concept projects (Verrazzano, Becca Treats) should be clearly labelled as concepts; listing tech stacks you did not use hurts credibility.
- Add real client quotes or metrics where you have them.
- Publish one useful guide every 2-4 weeks. Only add a new city page when you have something genuinely local to say - thin near-duplicate city pages can hurt.
- Target realistic queries first: "web developer in Abuja", "Paystack integration developer Nigeria", "real estate website developer Nigeria". "Web development Nigeria" is dominated by established agencies.

## Notes
- FAQ rich results are now shown only for a few site types, so FAQ markup helps understanding but will not show dropdowns in results.
- No one can guarantee a ranking. This gives you a technically clean, fast, well-linked site; results come from content, links and time. Track progress in Search Console (impressions -> clicks -> positions).
- Security housekeeping (not SEO): `.env` was inside the zip you uploaded, so treat those credentials as exposed if the archive was shared anywhere, and set a real `SECRET_KEY` in production (the code falls back to a dev value).
