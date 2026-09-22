"""
Extra long-form guides for /insights.

Each article follows the same shape as ARTICLES in app.py, with three extras:
  - `sections` items are (heading, [paragraph, paragraph, ...]) - a plain string also works
  - `faqs`             optional list of (question, answer) -> rendered + FAQPage schema
  - `related_services` optional list of service slugs to link to from the article

Dates: `published` / `updated` are ISO dates (YYYY-MM-DD). Bump `updated` whenever you
genuinely revise an article - it feeds <lastmod> in the sitemap and Article schema.
"""

NEW_ARTICLES = [
    {
        'slug': 'website-vs-web-app-vs-mobile-app-nigeria',
        'seo_title': 'Website, Web App or Mobile App? What You Need',
        'title': 'Website, Web App or Mobile App? What Your Nigerian Business Actually Needs',
        'description': 'Not sure whether to build a website, a web application or a mobile app? A plain-English guide to choosing the right one for your Nigerian business.',
        'intro': 'Many businesses ask for a mobile app when a good website would do the job, and others outgrow a simple website without realising they need a web application. The right choice depends on what your customers need to do - not on what sounds most impressive.',
        'published': '2026-09-21',
        'updated': '2026-09-21',
        'related_services': ['web-development', 'web-applications', 'mobile-app-development'],
        'sections': [
            ('The short answer', [
                'A website mostly presents information: who you are, what you offer, how to contact you. A web application lets people do things - log in, book, pay, upload, track an order or manage records. A mobile app is software installed from an app store, which can use phone features such as push notifications and the camera.',
                'Most small and medium businesses should start with a fast, well-built website. Add a web application when customers or staff need accounts, dashboards or workflows. Consider a native mobile app last, once you have proof that people would use it regularly.',
            ]),
            ('When a website is enough', [
                'If your main goals are to be found on Google, look credible, explain your services and collect enquiries, a website is the right tool. Company sites, professional-services firms, restaurants, schools, real estate agencies and consultants usually fall here.',
                'A good website also does most of the work that businesses imagine an app will do: it works on any phone, needs no installation, can be shared with a link and is indexed by search engines. An app store listing cannot rank on Google the way a well-structured website can.',
            ]),
            ('When you need a web application', [
                'Choose a web application when the product involves logins, user roles, saved data or business rules. Examples include a customer portal, an internal dashboard, a booking system, an agent or reseller platform, an online store with order management, or a system that replaces spreadsheets and WhatsApp coordination.',
                'Web applications still run in the browser, so you avoid app-store approval and can release fixes immediately. They can also be built as progressive web apps (PWAs), which can be added to a phone home screen and behave much like an app.',
            ]),
            ('When a mobile app is worth it', [
                'A native mobile app makes sense when you need deep phone features (background location, offline-first behaviour, hardware access), when customers will open the product several times a week, or when the app itself is the product.',
                'Before committing, weigh the extra costs: building and maintaining Android and iOS versions, app-store fees and review, updates that users must install, and the reality that many customers are wary of installing yet another app or have limited phone storage and data. A PWA is often the sensible middle step.',
            ]),
            ('A quick decision checklist', [
                'Ask three questions. Do people need to log in or store information with you? If no, start with a website. Do they need to do this every day or use phone hardware? If no, a web application or PWA is likely enough. Is the app store itself a distribution channel you need? Only then is a native app clearly justified.',
                'Whatever you choose, plan the foundations early: fast mobile performance, secure handling of user data, clear analytics and a URL structure that search engines can crawl. Retrofitting these later is more expensive than doing them at the start.',
            ]),
        ],
        'faqs': [
            ('Is a website cheaper than a mobile app?', 'In most cases yes. A website or web application is usually simpler to build and maintain than separate Android and iOS apps, though the final cost always depends on scope and features.'),
            ('Can a website work like an app?', 'Yes. A progressive web app (PWA) can be installed on a phone home screen, work with limited connectivity and send notifications while still being a website you can find on Google.'),
            ('Do I need a website if I already have an Instagram or WhatsApp business page?', 'Social profiles are useful, but you do not control them and they rarely rank for the searches customers make on Google. A website gives you a permanent, searchable home for your services, prices, proof of work and contact details.'),
        ],
        'keywords': ['website vs mobile app Nigeria', 'web app vs website', 'do I need a mobile app Nigeria'],
    },
    {
        'slug': 'how-to-get-your-website-on-google-nigeria',
        'title': 'How to Get Your Website on Google: A Step-by-Step Indexing Guide',
        'description': 'A practical walkthrough for getting a new website indexed by Google: Search Console, sitemaps, URL inspection and the common reasons pages stay invisible.',
        'intro': 'Publishing a website does not automatically put it on Google. Search engines must discover your pages, crawl them and decide they are worth storing in their index. This guide covers the steps that matter and the mistakes that quietly keep sites invisible.',
        'published': '2026-09-21',
        'updated': '2026-09-21',
        'related_services': ['seo-services', 'web-development', 'website-maintenance'],
        'sections': [
            ('Step 1: Check whether you are already indexed', [
                'Search Google for site:yourdomain.com. If pages appear, Google already knows about you. If nothing appears, the site is either brand new, blocked, or has not been discovered yet. This check shows what is indexed, not how well a page ranks.',
            ]),
            ('Step 2: Verify your site in Google Search Console', [
                'Google Search Console is free and is the most important SEO tool you can set up. Add your domain as a property and verify ownership - a DNS record for a domain property, or an HTML file or meta tag for a URL-prefix property. Once verified, you can see indexing status, search queries, crawl errors and mobile usability problems.',
                'Keep the verification method in place permanently. Removing it can revoke your access.',
            ]),
            ('Step 3: Submit an XML sitemap', [
                'A sitemap lists the URLs you want indexed. Make sure it contains only real, canonical, publicly accessible pages, then submit its address in the Sitemaps report in Search Console. A sitemap helps discovery; it does not guarantee indexing.',
                'Reference the sitemap in robots.txt as well so any crawler can find it.',
            ]),
            ('Step 4: Inspect and request indexing for key pages', [
                'Use the URL Inspection tool on your homepage and most important service pages. If a page is not indexed, request indexing. Use this for a handful of important pages rather than every URL - it is not a bulk tool.',
            ]),
            ('Why pages stay out of Google', [
                'The most common technical causes are a noindex tag left on from development, a robots.txt rule that blocks crawling, pages that return errors, redirects that loop, and duplicate URLs without a clear canonical. Check these first.',
                'The most common content causes are thin pages that add nothing new, near-duplicate pages, and pages with no internal links pointing to them. Link every important page from your navigation, footer or related content so crawlers and visitors can reach it.',
                'New sites also simply take time. Discovery and indexing can take days or weeks, and Google may choose not to index low-value pages at all.',
            ]),
            ('What to do after you are indexed', [
                'Indexing is only the start of visibility. To rank, each page must match what searchers want, load quickly on mobile and be supported by useful content and trustworthy references from other sites. Monitor the Performance report in Search Console to see which queries bring impressions, then improve the pages that are close to page one.',
            ]),
        ],
        'faqs': [
            ('How long does it take for a new website to appear on Google?', 'It varies. Some pages are indexed within days, others take weeks, and some are never indexed if Google judges them low value. Submitting a sitemap and linking pages internally speeds up discovery but does not guarantee a timeline.'),
            ('Do I have to pay to be listed on Google?', 'No. Being included in Google Search organic results is free. Paid ads are separate and do not affect organic indexing.'),
            ('Why is my site indexed but not ranking?', 'Indexed means Google has stored the page. Ranking depends on relevance, content quality, competition, page experience and authority. Improving content and earning quality references usually matters more than technical tweaks at that point.'),
        ],
        'keywords': ['how to get website on Google', 'Google Search Console Nigeria', 'website not showing on Google'],
    },
    {
        'slug': 'google-business-profile-for-nigerian-businesses',
        'title': 'Google Business Profile for Nigerian Businesses: A Local SEO Guide',
        'description': 'How to set up and optimise a Google Business Profile so nearby customers can find your Nigerian business on Google Search and Maps.',
        'intro': 'When someone searches for a service near them, Google often shows a map and a short list of businesses before any website. Your Google Business Profile is what earns a place there - and it is free.',
        'published': '2026-09-21',
        'updated': '2026-09-21',
        'related_services': ['seo-services', 'web-development', 'website-design'],
        'sections': [
            ('What a Google Business Profile does', [
                'A Business Profile is your listing on Google Search and Google Maps. It can show your name, category, hours, phone number, website, photos, services and customer reviews. For local searches such as a service plus a city or neighbourhood, it is often the first thing customers see.',
            ]),
            ('Set it up properly', [
                'Create or claim your profile and complete verification - Google chooses the available method for your business, such as phone, email, video or a mailed code. Use your real business name exactly as it appears in the real world. Adding extra keywords or a location to the name breaks Google\'s guidelines and can get the listing suspended.',
                'Choose the most accurate primary category, since it strongly influences the searches you can appear for, and add secondary categories only where they are genuinely true. If you visit customers rather than serving them at a shop, set the profile up as a service-area business and hide your address if customers do not visit you there.',
            ]),
            ('Keep your details consistent', [
                'Your business name, address and phone number should match across your website, social profiles and any directories you list on. Inconsistent details confuse both customers and search engines. Make sure your website contact page shows the same details as your profile.',
            ]),
            ('Photos, services and updates', [
                'Add clear, original photos of your premises, team, products and completed work. List your services with accurate descriptions and keep opening hours current, including holidays. Profiles that are complete and actively maintained give customers more reasons to choose you.',
            ]),
            ('Reviews', [
                'Ask happy customers to leave an honest review and make it easy by sending them your review link. Reply to every review professionally, including the negative ones. Do not buy reviews, offer rewards in exchange for them or review your own business - Google can remove them and penalise the profile.',
            ]),
            ('Connect it to your website', [
                'Link the profile to a fast website with a page for each core service and a clear contact page. The profile helps you appear in local results; the website provides the depth that convinces people to get in touch. Use the same wording for your services on both.',
            ]),
        ],
        'faqs': [
            ('Is Google Business Profile free?', 'Yes. Creating and managing a profile costs nothing.'),
            ('Can I have a profile without a shop?', 'Often yes, as a service-area business, provided you serve customers at their location or by appointment. Follow Google\'s eligibility guidelines for your type of business.'),
            ('Does a Business Profile replace a website?', 'No. The profile helps local visibility, while a website gives you full control over your content, lead capture and search presence beyond Maps.'),
        ],
        'keywords': ['Google Business Profile Nigeria', 'local SEO Nigeria', 'Google Maps business listing Nigeria'],
    },
    {
        'slug': 'how-long-does-it-take-to-build-a-website-in-nigeria',
        'title': 'How Long Does It Take to Build a Website in Nigeria?',
        'description': 'What determines a website project timeline in Nigeria, the stages every build goes through and how to avoid the delays that stall launches.',
        'intro': 'There is no single answer, because "a website" can be a few pages or a full platform. What matters is understanding the stages, what drives each one and which delays are in your hands.',
        'published': '2026-09-21',
        'updated': '2026-09-21',
        'related_services': ['web-development', 'website-design', 'ecommerce-development'],
        'sections': [
            ('The stages of a website project', [
                'Most projects move through discovery and planning, design, development, content and testing, and launch. Skipping discovery is the most common cause of rework later, because unclear requirements produce moving targets.',
            ]),
            ('What makes projects faster or slower', [
                'A focused business website with a handful of pages and content that is ready can often be built quickly. Timelines lengthen with more pages, custom design, integrations such as payments, user accounts, dashboards, product catalogues and custom features.',
                'A rough guide: a simple brochure-style site is usually the quickest, e-commerce takes longer because of catalogue, checkout and payment testing, and custom web applications take the longest because they involve business logic and data. Any specific quote should be based on a written scope.',
            ]),
            ('The biggest delay is usually content', [
                'Projects stall most often while waiting for text, logos, photos, product details and approvals - not while waiting for code. Prepare your service descriptions, business details, images and examples of past work before development starts, and nominate one person who can approve decisions quickly.',
            ]),
            ('Do not rush the parts that affect search', [
                'Before launch, check page titles, descriptions, headings, mobile performance, redirects from any old URLs, an XML sitemap and a working contact path. If you are replacing an existing site, plan redirects carefully so you do not lose the search visibility you already have.',
            ]),
            ('How to keep a project on schedule', [
                'Agree a written scope, milestones and review points up front. Limit changes after design approval, or treat them as a separate phase. Ask what happens after launch, since fixes, updates and improvements are part of running a site, not an afterthought.',
            ]),
        ],
        'faqs': [
            ('Can a website be built in a few days?', 'A very simple site can be, if the content and requirements are already clear. Anything with custom design, integrations or user accounts needs more time to build and test properly.'),
            ('Why is my website taking so long?', 'The usual reasons are unclear scope, late content or approvals, and extra features added mid-project. A written scope and clear milestones prevent most of these.'),
        ],
        'keywords': ['how long to build a website Nigeria', 'website development timeline Nigeria'],
    },
    {
        'slug': 'com-ng-vs-ng-vs-com-choosing-a-domain-name',
        'seo_title': '.com.ng vs .ng vs .com: Choosing a Nigerian Domain',
        'title': '.com.ng vs .ng vs .com: How to Choose a Domain Name for Your Nigerian Business',
        'description': 'Which domain extension should a Nigerian business choose - .com.ng, .ng or .com? Trade-offs, naming tips and the setup mistakes to avoid.',
        'intro': 'Your domain name is the address of your business online, and changing it later is painful. Here is how to think about the main extensions and how to set the domain up so it helps rather than hurts your search visibility.',
        'published': '2026-09-21',
        'updated': '2026-09-21',
        'related_services': ['web-development', 'seo-services', 'website-maintenance'],
        'sections': [
            ('The main options', [
                'A .com is the most familiar extension worldwide and is the natural choice if you want an international audience. A .ng or .com.ng is a Nigerian country-level domain that signals a Nigerian business to customers and to search engines. Each is a legitimate choice; the right one depends on who you serve.',
            ]),
            ('How the extension affects SEO', [
                'Country-level domains give search engines a clear signal about which country a site is intended for, which can help when your customers are mainly in Nigeria. A .com has no built-in country signal, so it relies on other signals such as content, addresses and links. Neither extension is a magic ranking factor - content quality and trust matter far more.',
            ]),
            ('Choosing the name itself', [
                'Prefer a name that is short, easy to spell aloud and matches your business name. Avoid hyphens, numbers and unusual spellings that customers will get wrong. Check that the name is not confusingly close to another brand, and consider securing the obvious variants if your budget allows.',
            ]),
            ('Protect your ownership', [
                'Register the domain in your own or your company\'s name, with an email address you control, and keep the login details safe. Do not let a developer or agency register it in their name. Enable auto-renewal and note the expiry date, because an expired domain can take your website and email down with it.',
            ]),
            ('Set it up correctly for search', [
                'Serve the site over HTTPS and choose one preferred version - with or without www - and permanently redirect the other to it. Make sure the canonical URLs and sitemap use that version. Duplicate versions of the same site split signals and confuse crawlers.',
            ]),
        ],
        'faqs': [
            ('Is .com.ng or .ng better for a Nigerian business?', 'Both signal a Nigerian focus. Choose whichever is available, easy to remember and consistent with your branding, and then use it consistently everywhere.'),
            ('Should I buy both a .com and a .ng?', 'If you can afford it, registering both protects your brand. Pick one as the main site and redirect the other to it so search engines see a single version.'),
        ],
        'keywords': ['.com.ng vs .ng', 'Nigerian domain name', 'choose domain name Nigeria'],
    },
]
