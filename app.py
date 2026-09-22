from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, send_from_directory, abort, session
)
import sqlite3
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
from dotenv import load_dotenv
import re
import json
from urllib.parse import urlparse
from markupsafe import Markup

from seo_content import NEW_ARTICLES

load_dotenv()

# ============================================================
# DATABASE
# ============================================================

DATABASE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "entrix.db"
)


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT,
            nin TEXT,
            date_of_birth TEXT,
            state TEXT,
            address TEXT,
            occupation TEXT,
            motivation TEXT,
            heard_from TEXT,
            bank_name TEXT,
            account_number TEXT,
            account_name TEXT,
            password_hash TEXT NOT NULL,
            is_approved INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            company TEXT,
            service TEXT,
            notes TEXT,
            budget REAL,
            agreed_price REAL,
            paid_amount REAL,
            paid_confirmed_at TIMESTAMP,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (agent_id) REFERENCES agents(id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Migrate agents
    agent_columns = [
        ("phone", "TEXT"),
        ("nin", "TEXT"),
        ("date_of_birth", "TEXT"),
        ("state", "TEXT"),
        ("address", "TEXT"),
        ("occupation", "TEXT"),
        ("motivation", "TEXT"),
        ("heard_from", "TEXT"),
        ("bank_name", "TEXT"),
        ("account_number", "TEXT"),
        ("account_name", "TEXT"),
        ("is_approved", "INTEGER NOT NULL DEFAULT 0"),
    ]
    existing_agent_cols = {
        row[1] for row in conn.execute("PRAGMA table_info(agents)").fetchall()
    }
    for col_name, col_type in agent_columns:
        if col_name not in existing_agent_cols:
            try:
                conn.execute(f"ALTER TABLE agents ADD COLUMN {col_name} {col_type}")
            except sqlite3.OperationalError:
                pass

    # Migrate leads
    lead_columns = [
        ("budget", "REAL"),
        ("agreed_price", "REAL"),
        ("paid_amount", "REAL"),
        ("paid_confirmed_at", "TIMESTAMP"),
    ]
    existing_lead_cols = {
        row[1] for row in conn.execute("PRAGMA table_info(leads)").fetchall()
    }
    for col_name, col_type in lead_columns:
        if col_name not in existing_lead_cols:
            try:
                conn.execute(f"ALTER TABLE leads ADD COLUMN {col_name} {col_type}")
            except sqlite3.OperationalError:
                pass

    conn.commit()
    conn.close()


def create_default_agent():
    email = os.environ.get("AGENT_EMAIL")
    password = os.environ.get("AGENT_PASSWORD")
    name = os.environ.get("AGENT_NAME", "Lead Agent")

    if not email or not password:
        return

    conn = get_db()
    existing = conn.execute(
        "SELECT id FROM agents WHERE email = ?", (email,)
    ).fetchone()

    if not existing:
        conn.execute(
            "INSERT INTO agents (name, email, password_hash, is_approved) VALUES (?, ?, ?, 1)",
            (name, email, generate_password_hash(password)),
        )
        conn.commit()

    conn.close()


def create_default_admin():
    name = os.environ.get("ADMIN_NAME", "Site Admin")
    email = os.environ.get("ADMIN_EMAIL")
    password = os.environ.get("ADMIN_PASSWORD")

    if not email or not password:
        return

    conn = get_db()
    existing = conn.execute("SELECT id FROM admins LIMIT 1").fetchone()

    if not existing:
        conn.execute(
            "INSERT INTO admins (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, generate_password_hash(password)),
        )
        conn.commit()

    conn.close()


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-this")
init_db()
create_default_agent()
create_default_admin()


# ============================================================
# LEAD STATUSES
# ============================================================

AGENT_CAN_SET = {"accepted", "lost"}  # what agents can change
COMMISSION_RATE = 0.30


@app.template_filter("naira")
def naira_filter(value):
    try:
        return f"₦{float(value):,.2f}"
    except (TypeError, ValueError):
        return "—"


@app.template_filter("commission_of")
def commission_of_filter(value):
    try:
        return float(value) * COMMISSION_RATE
    except (TypeError, ValueError):
        return 0


# ============================================================
# GOOGLE VERIFICATION
# ============================================================

@app.route('/google1236e1335ed123fa.html')
def google_verification():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'google1236e1335ed123fa.html')


# ============================================================
# CONFIG
# ============================================================

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
MAIL_RECIPIENT = os.environ.get('MAIL_RECIPIENT', 'entrix2026@gmail.com')

SUPPORT_PHONE = "+2347068133655"

SITE = {
    'name': 'Entrix II',
    'url': 'https://entrixii.com.ng',
    'tagline': "building what's next",
    'description': ('Entrix II is a developer-led digital studio building websites, web applications, '
                    'e-commerce platforms, custom software and SEO systems for businesses in Nigeria '
                    'and across Africa.'),
}

SOCIAL = {
    'github': 'https://github.com/EntrixII',
    'twitter': 'https://twitter.com/is_real999',
    'linkedin': 'https://www.linkedin.com/in/entrix-the-second-b7586b42b/',
    'instagram': 'https://instagram.com/entrix_the_second',
    'facebook': '#',
    'whatsapp': 'https://wa.me/2347068133655',
    'email': 'entrix2026@gmail.com',
}

SERVICES = [
    {'id':'website-development','slug':'web-development','title':'Web Development','icon':'💻','short':'Professional business websites and high-performance web builds for Nigerian and African businesses.','description':'Custom, responsive websites engineered for speed, trust, search visibility and conversions. We build company websites, corporate sites, landing pages and content-driven websites without unnecessary bloat.','features':['Responsive, mobile-first builds','Semantic, crawlable architecture','Fast-loading pages and Core Web Vitals focus','CMS and custom backend options','Analytics and Search Console readiness'],'audience':'businesses, startups, professionals and organizations','faqs':[('How much does web development cost in Nigeria?','Pricing depends on scope, number of pages, content, integrations and whether the site needs a custom backend. We scope projects before quoting so the price matches the actual work.'),('Can you build a website for a Nigerian business?','Yes. Entrix II works with businesses in Nigeria and can build sites around local audiences, mobile usage, contact workflows and payment requirements.')], 'keywords':['web development Nigeria','web developer Nigeria','website development Nigeria','web development company Nigeria','web development Africa']},
    {'id':'website-design','slug':'website-design','title':'Website Design & Redesign','icon':'🎨','short':'Modern website design and redesign services focused on credibility, usability and conversion.','description':'We redesign outdated websites and create new interfaces that make businesses easier to understand, trust and contact. Design decisions are connected to UX, performance and search—not decoration alone.','features':['UI/UX direction and page hierarchy','Responsive layouts','Conversion-focused calls to action','Accessibility-conscious components','Design systems for consistent pages'],'audience':'businesses with outdated or underperforming websites','faqs':[('Can you redesign an existing website?','Yes. We can audit the current structure, identify usability and performance problems, then redesign or rebuild the parts that matter most.'),('Will redesigning my site hurt SEO?','A redesign can preserve or improve SEO when URLs, metadata, redirects, internal links and important content are handled carefully.')], 'keywords':['website design Nigeria','web design Nigeria','website redesign Nigeria','web designer Nigeria','website design Africa']},
    {'id':'ecommerce','slug':'ecommerce-development','title':'E-commerce Development','icon':'🛒','short':'Online stores, product catalogs, checkout flows and payment integrations for African businesses.','description':'Build an online store that can manage products, customers, orders and payments. We can integrate business-specific workflows and Nigerian payment providers where appropriate.','features':['Product and category architecture','Cart and checkout flows','Payment gateway integration','Order and customer workflows','Mobile-first shopping experience'],'audience':'retailers, brands, creators and businesses selling online','faqs':[('Can you integrate Paystack?','Yes. Paystack can be integrated where it fits the project, alongside other supported payment or business APIs.'),('Can you build an e-commerce site for Nigeria?','Yes. We can tailor the storefront, checkout, currency, payment flow and delivery information to the business and its customers.')], 'keywords':['ecommerce development Nigeria','online store development Nigeria','ecommerce website Nigeria','Paystack website development','ecommerce development Africa']},
    {'id':'web-applications','slug':'web-applications','title':'Web Application Development','icon':'🧩','short':'Custom web applications, portals, dashboards and business platforms built around real workflows.','description':'We build software that does more than present information: authenticated dashboards, portals, booking systems, customer areas, admin systems and database-driven applications.','features':['Authentication and user roles','Dashboards and admin panels','Database-driven workflows','REST API integrations','Business rules and automation'],'audience':'startups, SMEs and organizations with custom workflows','faqs':[('What is a web application?','A web application lets users perform tasks online—such as logging in, managing records, booking services, processing orders or using a dashboard.'),('Can you connect an app to an existing API?','Yes. API integration can connect the application to payment, messaging, analytics, CRM and other external systems.')], 'keywords':['web application development Nigeria','web app developer Nigeria','custom web applications Nigeria','software development Nigeria','web applications Africa']},
    {'id':'custom-software','slug':'custom-software-development','title':'Custom Software Development','icon':'⚙️','short':'Business software designed around workflows that off-the-shelf tools cannot handle well.','description':'Custom software can replace spreadsheets, disconnected tools and repetitive manual processes with a system built around the way a business actually operates.','features':['Requirements discovery','Custom business logic','Admin and staff dashboards','Database architecture','Deployment and maintainable code'],'audience':'businesses with specialized processes or operational bottlenecks','faqs':[('When should a business consider custom software?','Custom software makes sense when existing tools cannot support an important workflow, when manual work is expensive, or when the business needs tighter control of its data and processes.'),('Do you build internal business tools?','Yes. Internal dashboards, portals, workflow tools and database-backed systems are common custom software projects.')], 'keywords':['custom software development Nigeria','software company Nigeria','business software Nigeria','software developers Nigeria','custom software Africa']},
    {'id':'seo','slug':'seo-services','title':'SEO Services','icon':'🔍','short':'Technical, on-page and content-focused SEO for businesses targeting Nigeria and African markets.','description':'SEO starts with a site that search engines can crawl and users can trust. We work on technical foundations, page targeting, internal links, metadata, structured data, performance and useful content.','features':['Technical SEO audits','On-page optimization','Internal linking and information architecture','Structured data implementation','Search Console and indexing setup'],'audience':'businesses that want qualified organic traffic','faqs':[('Can you help my website rank on Google in Nigeria?','We can improve the technical and content foundations that influence organic visibility, but no ethical SEO provider can guarantee a specific Google position.'),('How long does SEO take?','SEO is cumulative. Technical fixes can be discovered relatively quickly, while competitive queries usually require sustained useful content, authority and ongoing optimization.')], 'keywords':['SEO Nigeria','SEO services Nigeria','SEO company Nigeria','technical SEO Nigeria','SEO Africa']},
    {'id':'mobile-applications','slug':'mobile-app-development','title':'Mobile App Development','icon':'📱','short':'Mobile-focused digital experiences and app-ready interfaces for businesses and products.','description':'We design and develop mobile-first experiences and progressive web applications, with product architecture that can support a future native app where needed.','features':['Mobile-first product UX','Progressive web applications','Responsive application interfaces','API-backed experiences','Cross-device testing'],'audience':'businesses and startups building mobile customer experiences','faqs':[('Do you build mobile apps?','We build mobile-first web experiences and progressive web applications. Native app requirements can be scoped separately depending on the product.'),('Can a website behave like an app?','A well-built progressive web app can provide app-like navigation and functionality while remaining accessible through the web.')], 'keywords':['mobile app development Nigeria','mobile application development Nigeria','PWA development Nigeria','mobile app developer Nigeria','app development Africa']},
    {'id':'ui-ux','slug':'ui-ux-design','title':'UI/UX Design','icon':'🎯','short':'User interface and user experience design for websites, web apps and digital products.','description':'We turn business requirements into clear user journeys, page structures and interfaces that reduce friction and make digital products easier to use.','features':['User journeys and information architecture','Wireframes and interface concepts','Responsive component design','Usability-focused layouts','Design handoff for development'],'audience':'teams creating or improving digital products','faqs':[('Do you design before development?','Yes. For larger projects, clarifying the user journey and interface before development reduces rework and helps define the right product scope.'),('Can you improve an existing interface?','Yes. Existing products can be reviewed for navigation, hierarchy, clarity and conversion opportunities.')], 'keywords':['UI UX design Nigeria','UX designer Nigeria','UI design Nigeria','product design Nigeria','UX design Africa']},
    {'id':'ai-automation','slug':'ai-automation','title':'AI & Business Automation','icon':'🤖','short':'Practical AI integrations and automation that reduce repetitive work and improve digital workflows.','description':'We integrate AI and automation where they solve a real business problem: classification, content workflows, support tools, data processing, notifications and repetitive operational tasks.','features':['AI-powered website features','Workflow automation','Third-party API integrations','Data processing workflows','Human-in-the-loop systems'],'audience':'businesses looking to reduce repetitive digital work','faqs':[('Can AI be added to an existing website?','Yes, if there is a useful workflow for it. AI can be integrated into support, search, content, internal tools and other product features.'),('Do you automate business tasks?','Yes. Automation can connect forms, databases, APIs, email, notifications and AI services into a repeatable workflow.')], 'keywords':['AI automation Nigeria','AI development Nigeria','business automation Nigeria','AI integration Nigeria','AI services Africa']},
    {'id':'api-integration','slug':'api-integration','title':'API & System Integration','icon':'🔗','short':'Connect websites and applications to payments, CRMs, messaging, analytics and other services.','description':'We integrate APIs so systems can exchange data reliably. This can include payments, authentication, email, messaging, maps, analytics and business platforms.','features':['REST API integration','Webhook handling','Authentication and tokens','Data mapping and validation','Error handling and monitoring'],'audience':'businesses connecting multiple digital systems','faqs':[('Can you integrate third-party APIs?','Yes. We can connect a website or application to external services when their API and terms support the required workflow.'),('Can APIs automate payments or notifications?','Yes. APIs and webhooks can trigger actions such as payment confirmation, order updates and notifications.')], 'keywords':['API integration Nigeria','API development Nigeria','software integration Nigeria','web API developer Nigeria','API integration Africa']},
    {'id':'payment-integration','slug':'payment-integration','title':'Payment Integration','icon':'💳','short':'Secure payment flows and payment-provider integrations for websites and applications.','description':'We integrate supported payment providers into websites and applications, with attention to checkout UX, transaction verification, webhooks and order state.','features':['Payment checkout integration','Transaction verification','Webhook handling','Order/payment status logic','Test and production configuration'],'audience':'businesses accepting payments online','faqs':[('Can you integrate Nigerian payment gateways?','Yes. The right provider depends on the project, account requirements and the payment methods the business needs.'),('How do you verify online payments?','A robust integration verifies transactions server-side and handles provider callbacks/webhooks rather than trusting only the browser response.')], 'keywords':['payment integration Nigeria','online payment integration Nigeria','Paystack integration Nigeria','Flutterwave integration Nigeria','payment gateway integration Africa']},
    {'id':'maintenance','slug':'website-maintenance','title':'Website Maintenance & Support','icon':'🛠️','short':'Ongoing website updates, technical fixes, performance improvements and SEO maintenance.','description':'Websites need maintenance after launch. We can help with updates, bug fixes, performance work, content changes, technical SEO and feature improvements.','features':['Bug fixes and updates','Performance monitoring','Technical SEO maintenance','Content and feature changes','Security-conscious maintenance practices'],'audience':'businesses with an existing website or application','faqs':[('Can you maintain a website built by someone else?','Yes. We can review the codebase and hosting setup first, then scope maintenance based on what is safely maintainable.'),('Do you offer ongoing SEO maintenance?','Yes. Ongoing work can include technical fixes, content improvements, internal linking and monitoring of search visibility.')], 'keywords':['website maintenance Nigeria','website support Nigeria','website management Nigeria','web maintenance services Nigeria','website maintenance Africa']},
]

REGIONS = [
    {'slug':'nigeria','name':'Nigeria','title':'Digital Services & Web Development in Nigeria','intro':'Entrix II is a developer-led digital studio serving businesses across Nigeria with websites, software, e-commerce, SEO, automation and other digital services.','body':['Nigerian businesses often need more than a brochure website. The right digital system may need mobile-first UX, local payment integrations, lead capture, business dashboards, search visibility and room to grow.','Entrix II builds around those requirements rather than forcing every business into the same template. Projects can range from a professional company website to a custom web application or e-commerce platform.'], 'keywords':['web development Nigeria','digital agency Nigeria','software development Nigeria','SEO Nigeria','website design Nigeria']},
    {'slug':'africa','name':'Africa','title':'Digital Services & Software Development for African Businesses','intro':'Entrix II builds digital products for businesses and organizations across African markets, with an emphasis on performance, mobile usability and practical business workflows.','body':['African businesses operate across different markets, payment providers, languages and customer behaviors. A useful digital product needs flexible architecture and a clear understanding of the business it supports.','Entrix II can work remotely with African clients on websites, e-commerce, custom software, SEO, API integrations and automation.'], 'keywords':['web development Africa','software development Africa','digital agency Africa','website design Africa','SEO Africa']},
    {'slug':'abuja','name':'Abuja','title':'Web Development & Digital Services in Abuja','intro':'Entrix II provides website development, software, e-commerce, SEO and digital product services for businesses in Abuja and clients across Nigeria.','body':['For Abuja businesses, a website often needs to support trust, lead generation and professional presentation while working reliably on mobile devices. We build digital experiences around those goals.','From corporate websites and real estate platforms to custom dashboards and online stores, each project is scoped around the business workflow and audience.'], 'keywords':['web development Abuja','web design Abuja','software development Abuja','SEO Abuja','website developer Abuja']},
    {'slug':'lagos','name':'Lagos','title':'Web Development & Digital Services in Lagos','intro':'Entrix II works remotely with Lagos businesses on high-performance websites, e-commerce platforms, web applications, SEO and custom software.','body':['Lagos businesses compete in a crowded digital market, so speed, clarity, trust and discoverability matter. We combine technical development with UX and SEO fundamentals to create useful digital products.','Projects can be built for startups, SMEs, professional services, retail brands and organizations that need a stronger online presence or a custom digital workflow.'], 'keywords':['web development Lagos','web design Lagos','software development Lagos','SEO Lagos','website developer Lagos']},
    {'slug':'kaduna','name':'Kaduna','title':'Web Development & Digital Services in Kaduna','intro':'Entrix II provides web development, e-commerce, SEO and custom software services for Kaduna businesses and organizations.','body':['A strong digital presence can help Kaduna businesses reach customers beyond their immediate area. We build responsive websites and applications that make services, products and contact paths clear.','Whether the project is a company website, online store, dashboard or custom business system, the goal is a maintainable product that supports the organization after launch.'], 'keywords':['web development Kaduna','web design Kaduna','software development Kaduna','SEO Kaduna','website developer Kaduna']},
]

INDUSTRIES = [
    {'slug':'real-estate','name':'Real Estate','title':'Web Development & Digital Services for Real Estate Businesses','intro':'Websites, property platforms, lead-generation systems and SEO for real estate businesses in Nigeria and Africa.','body':['Real estate websites need more than attractive property photos. Buyers and investors need clear listings, location information, trust signals and simple ways to enquire.','Entrix II can build property websites, listing systems, lead forms, search interfaces and supporting SEO content around the way an agency or developer actually works.']},
    {'slug':'ecommerce-retail','name':'E-commerce & Retail','title':'E-commerce Development for Retail Businesses in Nigeria','intro':'Online stores, payment integrations, product catalogs and conversion-focused shopping experiences for Nigerian retailers.','body':['A useful retail website should make products easy to discover, understand and buy on a phone. Checkout, payment verification and order handling are part of the product—not afterthoughts.','We build online stores and supporting systems that can grow from a simple catalog into a more capable commerce platform.']},
    {'slug':'professional-services','name':'Professional Services','title':'Websites & Digital Systems for Professional Services Firms','intro':'Professional websites, lead-generation systems and custom web tools for consultants, firms and service businesses.','body':['Professional service businesses compete on credibility. A strong website should explain expertise clearly, make enquiries easy and provide useful evidence such as case studies and service information.','Entrix II combines design, development and search foundations to create a digital presence that supports business development.']},
    {'slug':'hospitality','name':'Hospitality','title':'Web Development for Hotels, Restaurants & Hospitality Businesses','intro':'Mobile-friendly websites, booking flows, menus, online ordering and digital systems for hospitality businesses.','body':['Hospitality customers often make decisions on mobile. Fast pages, clear offers, location details, menus, booking or enquiry paths and strong visual presentation all matter.','We can build a hospitality website around the customer journey while keeping the technical foundation maintainable.']},
    {'slug':'startups','name':'Startups','title':'Web Development & MVP Software for Startups','intro':'MVP websites, web applications, dashboards and product interfaces for startups building and validating digital products.','body':['Startups need to move quickly without building a technical dead end. We focus on the smallest useful architecture that can validate an idea while leaving room for future features.','Projects can include landing pages, MVPs, authenticated applications, dashboards, APIs and payment flows.']},
    {'slug':'education','name':'Education','title':'Websites & Web Applications for Education Businesses','intro':'Websites, portals, dashboards and digital experiences for schools, training businesses and education-focused organizations.','body':['Education organizations may need public websites alongside private workflows such as registrations, portals, forms and dashboards.','Entrix II can scope these pieces separately or combine them into a coherent digital platform.']},
    {'slug':'fashion','name':'Fashion & Lifestyle','title':'E-commerce & Websites for Fashion and Lifestyle Brands','intro':'Brand-led websites, online stores and digital experiences for fashion, beauty and lifestyle businesses.','body':['Fashion and lifestyle brands need strong presentation without sacrificing usability. Product discovery, mobile performance, checkout and clear brand storytelling all contribute to the customer experience.','We build responsive digital storefronts and supporting systems around the brand and its sales process.']},
    {'slug':'nonprofits','name':'Nonprofits & Organizations','title':'Web Development for Nonprofits & Organizations','intro':'Accessible websites, information hubs, forms and custom digital systems for organizations in Nigeria and Africa.','body':['Organizations often need websites that make information easy to find while supporting forms, contact workflows, events, programs or donations where applicable.','We can structure the site around the audiences and tasks that matter most to the organization.']},
    {'slug':'corporate','name':'Corporate Businesses','title':'Corporate Website Development in Nigeria','intro':'Professional corporate websites, service pages, case studies and digital systems for established businesses.','body':['Corporate websites need clear information architecture, strong credibility signals, fast performance and maintainable content.','Entrix II builds corporate sites with reusable page structures, technical SEO foundations and conversion paths for enquiries.']},
    {'slug':'saas','name':'SaaS & Digital Products','title':'Web Application Development for SaaS & Digital Products','intro':'Interfaces, dashboards, authentication, APIs and web applications for SaaS companies and digital products.','body':['Digital products need a reliable interface and backend architecture that supports real users, not just a marketing page.','Entrix II can contribute to product UI, web application development, dashboards, APIs, authentication and integrations.']},
]

ARTICLES = [
    {'slug':'how-much-does-a-website-cost-in-nigeria','title':'How Much Does a Website Cost in Nigeria?','description':'A practical guide to the factors that determine website development pricing in Nigeria, from simple business sites to custom web applications.','intro':'Website prices in Nigeria vary because “website” can mean anything from a few static pages to a database-backed application. The useful question is what the business needs the site to do.','sections':[('What affects the price?','Page count, custom design, content, forms, e-commerce, integrations, authentication, dashboards, hosting and ongoing maintenance all affect scope. A five-page company website is fundamentally different from a platform with customer accounts and payments.'),('What should a business budget for?','Instead of choosing a price from a generic package, list the pages, features, integrations and content requirements first. Then compare quotes based on what is actually included.'),('How to avoid a cheap rebuild later','A low upfront price can become expensive if the site is difficult to maintain, slow on mobile, impossible to edit or poorly structured for search. Ask what platform is being used, who owns the code and domain, and what happens after launch.')], 'keywords':['website cost Nigeria','how much website costs in Nigeria','website development price Nigeria']},
    {'slug':'seo-for-small-businesses-in-nigeria','title':'SEO for Small Businesses in Nigeria: A Practical Guide','description':'A practical SEO checklist for Nigerian businesses that want more qualified visibility from Google.','intro':'Small businesses do not need to publish hundreds of pages to begin SEO. They need a technically accessible website, clear service pages, useful information and a consistent way to demonstrate relevance and trust.','sections':[('Start with the pages that matter','Create strong pages for your core services and the audiences you actually serve. Each page should answer the user’s intent instead of repeating the same paragraph with different keywords.'),('Make the site easy to crawl','Use descriptive titles, headings, internal links, canonical URLs, XML sitemaps, clean URLs and mobile-friendly layouts. Fix broken links and avoid blocking important resources from crawlers.'),('Build evidence of expertise','Case studies, original insights, useful guides, genuine business information and references from relevant sites can strengthen a business’s overall search presence over time.')], 'keywords':['SEO for small businesses Nigeria','small business SEO Nigeria','Google SEO Nigeria']},
    {'slug':'website-seo-checklist-nigeria','title':'Website SEO Checklist for Nigerian Businesses','description':'A technical and on-page SEO checklist for businesses launching or improving a website in Nigeria.','intro':'Before chasing competitive keywords, make sure the site can be crawled, understood and trusted. This checklist covers the foundations that should be in place first.','sections':[('Technical foundations','Use HTTPS, fast pages, responsive design, a crawlable navigation structure, canonical URLs, an XML sitemap and a sensible robots.txt file.'),('Page-level optimization','Give each important page a unique title and description, one clear primary heading, useful copy, descriptive image alt text and contextual internal links.'),('Local relevance','If the business serves a defined Nigerian market, make the service area clear in useful content. Keep business details consistent across legitimate profiles and directories; do not create duplicate city pages with near-identical copy.')], 'keywords':['SEO checklist Nigeria','technical SEO checklist Nigeria','website SEO Nigeria']},
    {'slug':'paystack-integration-guide-for-business-websites','title':'Paystack Integration for Business Websites: What to Plan','description':'Key technical and UX considerations when integrating online payments into a business website.','intro':'Payment integration is not just a button. A reliable checkout needs transaction verification, clear order states, error handling and a customer experience that works on mobile.','sections':[('Plan the payment flow','Decide what happens before payment, during checkout, after success and after failure. The application should have a clear internal order state rather than assuming every browser response means payment succeeded.'),('Verify transactions server-side','Payment providers expose mechanisms for verification and webhooks. Use the provider’s current documentation and credentials, and never expose secret keys in frontend code.'),('Design for real customers','Explain what the customer is buying, show the total clearly and provide a useful confirmation path. Mobile checkout should be tested carefully because many customers will use phones.')], 'keywords':['Paystack integration Nigeria','payment integration Nigeria','online payments Nigeria']},
    {'slug':'how-to-choose-a-web-development-company-in-nigeria','title':'How to Choose a Web Development Company in Nigeria','description':'Questions to ask before hiring a Nigerian web developer or digital agency.','intro':'The best developer is not necessarily the one with the cheapest quote. Look for evidence that they can understand your requirements, build the product, communicate clearly and leave you with a maintainable system.','sections':[('Review real work','Ask for live examples and case studies. Look at the actual sites on mobile, test forms and check whether the work matches your needs.'),('Ask who owns the assets','Clarify domain ownership, hosting access, source code, design files and third-party accounts. Your business should not be locked out of its own digital property.'),('Ask about after-launch support','A site needs updates, fixes and sometimes new features. Know whether maintenance is included, optional or charged separately.')], 'keywords':['web development company Nigeria','best web developer Nigeria','hire web developer Nigeria']},
]

PROJECTS = [
    {'id':'jecyani-properties','title':'Jecyani Properties','category':'Real Estate','url':'https://jecyaniproperties.com/','live':True,'description':'A modern real estate platform showcasing properties with a sleek, trust-driven interface. Built for speed and conversion.','image':'jacyani.webp','technologies':['Flask','Tailwind CSS','JavaScript','PostgreSQL'],'challenge':'The client needed a digital presence that reflected their premium property portfolio while being easy to manage.','solution':'We built a custom CMS with property listings, advanced search, and a streamlined contact system.'},
    {'id':'crownbee-global','title':'Crownbee Global Services','category':'Real Estate','url':'https://crownbeeglobalservices.com/','live':True,'description':'A corporate website for international real estate services, emphasizing trust and global reach.','image':'crownbee.webp','technologies':['React','Node.js','MongoDB','AWS'],'challenge':'Showcasing a diverse portfolio across multiple countries with a unified brand voice.','solution':'A multi-language site with dynamic content blocks and a powerful backend.'},
    {'id':'verrazzano','title':'Verrazzano','category':'Furniture','url':None,'live':False,'description':'A high-end furniture brand concept. This case study explores e-commerce and immersive product presentation.','image':'image.WebP','technologies':['Next.js','Three.js','Stripe','GraphQL'],'challenge':'Creating a digital showroom that feels as luxurious as the physical products.','solution':'A 3D product viewer with AR preview, integrated with a headless CMS for inventory.'},
    {'id':'michie-plus','title':'Michie Plus','category':'E-commerce','url':'https://michieplus.com.ng/','live':True,'description':'A full-featured e-commerce platform for fashion and lifestyle. Currently a case study of scalable architecture.','image':'michieplus.webp','technologies':['Vue.js','Django','PostgreSQL','Redis','Celery'],'challenge':'Handling high traffic during flash sales with a seamless checkout experience.','solution':'Microservices architecture with a message queue for order processing, and a responsive Vue storefront.'},
    {'id':'becca-treats','title':'Becca Treats','category':'Food & Treats','url':None,'live':False,'description':'A delightful brand for homemade treats. This case study focuses on brand storytelling and online ordering.','image':'image.WebP','technologies':['WordPress','WooCommerce','Custom Theme','SEO'],'challenge':'Translating the warmth of a local bakery into a digital experience.','solution':'A custom WordPress theme with a focus on visuals and a simple ordering flow.'},
]


# ============================================================
# SEO CONTENT + CONSTANTS
# ============================================================

# Bump CONTENT_UPDATED whenever you genuinely change page content. It feeds <lastmod>
# in the sitemap. (Google ignores lastmod once it learns it is always "today".)
CONTENT_PUBLISHED = '2026-09-08'
CONTENT_UPDATED = '2026-09-21'

PROD_HOST = urlparse(SITE['url']).netloc

# Pages that must never appear in search results.
PRIVATE_PREFIXES = (
    '/admin', '/agent-dashboard', '/agent-login', '/agent-register',
    '/agent-pending', '/agent-logout', '/agent/',
)

# Pixel sizes of the portfolio images (prevents layout shift -> better CLS).
PROJECT_IMAGE_DIMS = {
    'jacyani.webp': (1366, 766),
    'crownbee.webp': (1366, 766),
    'michieplus.webp': (1366, 766),
    'image.WebP': (720, 1080),
}
for _p in PROJECTS:
    _w, _h = PROJECT_IMAGE_DIMS.get(_p['image'], (1366, 766))
    _p['image_w'], _p['image_h'] = _w, _h

for _a in ARTICLES:
    _a.setdefault('published', CONTENT_PUBLISHED)
    _a.setdefault('updated', CONTENT_UPDATED)
ARTICLES.extend(NEW_ARTICLES)


# ============================================================
# EMAIL HELPERS
# ============================================================

def _send_email(to_email, subject, body):
    if not MAIL_USERNAME or not MAIL_PASSWORD:
        app.logger.warning('MAIL_USERNAME / MAIL_PASSWORD not set — email not sent.')
        return False
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = MAIL_USERNAME
    msg['To'] = to_email
    msg.set_content(body)
    try:
        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT, timeout=10) as smtp:
            smtp.starttls()
            smtp.login(MAIL_USERNAME, MAIL_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as exc:
        app.logger.error(f'Failed to send email: {exc}')
        return False


def send_contact_email(form):
    if not MAIL_USERNAME or not MAIL_PASSWORD:
        app.logger.warning('MAIL_USERNAME / MAIL_PASSWORD not set — contact email not sent.')
        return False
    name=form.get('name','').strip(); email=form.get('email','').strip(); company=form.get('company','').strip(); service=form.get('service','').strip(); description=form.get('description','').strip(); budget=form.get('budget','').strip()
    service_title=next((s['title'] for s in SERVICES if s['id']==service),service)
    msg=EmailMessage(); msg['Subject']=f'New project inquiry from {name or "website visitor"}'; msg['From']=MAIL_USERNAME; msg['To']=MAIL_RECIPIENT
    if email: msg['Reply-To']=email
    msg.set_content(f"New message from the Entrix II contact form\n\nName: {name}\nEmail: {email}\nCompany: {company or '—'}\nService: {service_title or '—'}\nBudget: {budget or '—'}\n\nProject description:\n{description}\n")
    try:
        with smtplib.SMTP(MAIL_SERVER,MAIL_PORT,timeout=10) as smtp:
            smtp.starttls(); smtp.login(MAIL_USERNAME,MAIL_PASSWORD); smtp.send_message(msg)
        return True
    except Exception as exc:
        app.logger.error(f'Failed to send contact email: {exc}'); return False


def send_agent_approved_email(agent_name, agent_email):
    login_url = url_for('agent_login', _external=True)
    body = f"""Hi {agent_name},

Good news — your Entrix II agent account has been approved.

You can now log in to the Agent Portal and start submitting leads:

{login_url}

Your login email: {agent_email}

If you have any questions, just reply to this email.

— Entrix II
{SITE['url']}
"""
    return _send_email(
        agent_email,
        "Your Entrix II agent account has been approved",
        body,
    )


def send_agreed_price_email(agent_name, agent_email, lead_name, agreed_price):
    commission = float(agreed_price) * COMMISSION_RATE
    dashboard_url = url_for('agent_login', _external=True)
    body = f"""Hi {agent_name},

The agreed price for the lead "{lead_name}" has been set by the Entrix II team.

Agreed price: ₦{float(agreed_price):,.2f}
Your commission (30%): ₦{commission:,.2f}

You can track progress from your dashboard:

{dashboard_url}

Once the project is completed and payment is processed, we will notify you again.

— Entrix II
{SITE['url']}
"""
    return _send_email(
        agent_email,
        f"Agreed price set for {lead_name}",
        body,
    )


def send_paid_email(agent_name, agent_email, lead_name, paid_amount):
    dashboard_url = url_for('agent_login', _external=True)
    body = f"""Hi {agent_name},

You have been paid ₦{float(paid_amount):,.2f} for the lead "{lead_name}".

Please log into your dashboard and confirm receipt:

{dashboard_url}

If you do not see the payment in your account, please contact support:

{SUPPORT_PHONE}

— Entrix II
{SITE['url']}
"""
    return _send_email(
        agent_email,
        f"You've been paid for {lead_name}",
        body,
    )


# ============================================================
# AUTH DECORATORS
# ============================================================

def agent_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "agent_id" not in session:
            return redirect(url_for("agent_login"))

        conn = get_db()
        agent = conn.execute(
            "SELECT is_approved FROM agents WHERE id = ?",
            (session["agent_id"],),
        ).fetchone()
        conn.close()

        if not agent or agent["is_approved"] != 1:
            session.clear()
            flash("Your account is not approved yet.", "error")
            return redirect(url_for("agent_login"))

        return view(*args, **kwargs)

    return wrapped_view


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)
    return wrapped_view


@app.context_processor
def inject_globals():
    path = request.path
    return {
        'site': SITE,
        'social': SOCIAL,
        'projects': PROJECTS,
        'services': SERVICES,
        'regions': REGIONS,
        'industries': INDUSTRIES,
        'articles': ARTICLES,
        'now': datetime.now(),
        'support_phone': SUPPORT_PHONE,
        'commission_rate': COMMISSION_RATE,
        # --- SEO ---
        'noindex': path.startswith(PRIVATE_PREFIXES),
        'canonical_url': SITE['url'] + (path.rstrip('/') or '/'),
    }


# ============================================================
# SEO INFRASTRUCTURE
# ============================================================

try:  # gzip/brotli - big Core Web Vitals win. Optional: pip install Flask-Compress
    from flask_compress import Compress
    Compress(app)
except ImportError:
    pass


@app.template_filter('squish')
def squish_filter(value):
    """Collapse whitespace/newlines so <title> and meta descriptions are one clean line."""
    return Markup(re.sub(r'\s+', ' ', str(value)).strip())


@app.template_filter('slugify')
def slugify_filter(value):
    return re.sub(r'[^a-z0-9]+', '-', str(value).lower()).strip('-')


@app.template_filter('prettydate')
def prettydate_filter(value):
    try:
        d = datetime.strptime(value, '%Y-%m-%d')
        return f"{d.day} {d.strftime('%B %Y')}"
    except (TypeError, ValueError):
        return value


@app.template_global()
def faq_schema(faqs):
    """FAQPage JSON-LD built in Python (Jinja cannot do list comprehensions)."""
    return {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        'mainEntity': [
            {'@type': 'Question', 'name': q,
             'acceptedAnswer': {'@type': 'Answer', 'text': a}}
            for q, a in faqs
        ],
    }


@app.template_global()
def breadcrumb_schema(trail):
    return {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': i, 'name': c['name'], 'item': c['url']}
            for i, c in enumerate(trail, start=1)
        ],
    }


def crumbs(*items, visible=True):
    """crumbs(('Services', '/services'), ('Web Development', '/services/web-development'))"""
    trail = [{'name': 'Home', 'url': SITE['url'] + '/'}]
    for name, url in items:
        trail.append({'name': name, 'url': url if url.startswith('http') else SITE['url'] + url})
    return {'trail': trail, 'visible': visible}


@app.context_processor
def static_cache_busting():
    """Adds ?v=<mtime> to static URLs so they can be cached for a year safely."""
    def dated_url_for(endpoint, **values):
        external = values.pop('_external', False)
        if endpoint == 'static' and values.get('filename'):
            fp = os.path.join(app.static_folder, values['filename'])
            if os.path.isfile(fp):
                values['v'] = int(os.stat(fp).st_mtime)
        path = url_for(endpoint, **values)
        return SITE['url'] + path if external else path
    return {'url_for': dated_url_for}


@app.before_request
def enforce_canonical_url():
    """One URL per page: no www, no trailing slash, https (only when the proxy says it is http)."""
    if request.method not in ('GET', 'HEAD'):
        return None
    host = request.host.split(':')[0].lower()
    on_prod = host in (PROD_HOST, 'www.' + PROD_HOST)
    path = request.path
    target = path
    if len(path) > 1 and path.endswith('/') and not path.startswith('/static/'):
        target = path.rstrip('/') or '/'
    needs_redirect = target != path
    if on_prod:
        if host.startswith('www.'):
            needs_redirect = True
        proto = request.headers.get('X-Forwarded-Proto', 'https').split(',')[0].strip().lower()
        if proto == 'http':
            needs_redirect = True
    if not needs_redirect:
        return None
    base = SITE['url'] if on_prod else request.host_url.rstrip('/')
    qs = request.query_string.decode('utf-8')
    return redirect(base + target + ('?' + qs if qs else ''), code=301)


@app.after_request
def add_seo_headers(resp):
    path = request.path
    if path.startswith(PRIVATE_PREFIXES):
        resp.headers['X-Robots-Tag'] = 'noindex, nofollow'
    if path.startswith('/static/') and 'v' in request.args and resp.status_code == 200:
        resp.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
    resp.headers.setdefault('X-Content-Type-Options', 'nosniff')
    resp.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
    return resp


@app.errorhandler(404)
def page_not_found(_err):
    return render_template('404.html', noindex=True), 404


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico', mimetype='image/x-icon')


@app.route('/site.webmanifest')
def webmanifest():
    manifest = {
        'name': SITE['name'],
        'short_name': SITE['name'],
        'description': SITE['description'],
        'start_url': '/',
        'display': 'browser',
        'background_color': '#05060a',
        'theme_color': '#05060a',
        'icons': [
            {'src': url_for('static', filename='images/icon-192.png'), 'sizes': '192x192', 'type': 'image/png'},
            {'src': url_for('static', filename='images/icon-512.png'), 'sizes': '512x512', 'type': 'image/png'},
        ],
    }
    return app.response_class(json.dumps(manifest), mimetype='application/manifest+json')


# ============================================================
# PUBLIC ROUTES
# ============================================================

@app.route('/')
def home(): return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html', breadcrumbs=crumbs(('About', url_for('about')), visible=False))

@app.route('/vision')
def vision():
    return render_template('vision.html', breadcrumbs=crumbs(('Vision', url_for('vision')), visible=False))

@app.route('/services')
def services():
    return render_template('services.html', breadcrumbs=crumbs(('Services', url_for('services'))))

@app.route('/work')
def work():
    return render_template('work.html', projects=PROJECTS,
                           breadcrumbs=crumbs(('Work', url_for('work'))))

@app.route('/work/<slug>')
def project_detail(slug):
    project = next((p for p in PROJECTS if p['id'] == slug), None)
    if not project: abort(404)
    return render_template(
        'project_detail.html', project=project,
        og_image=SITE['url'] + url_for('static', filename='images/' + project['image']),
        breadcrumbs=crumbs(('Work', url_for('work')), (project['title'], url_for('project_detail', slug=slug))),
    )

@app.route('/services/<slug>')
def service_detail(slug):
    service = next((s for s in SERVICES if s['slug'] == slug), None)
    if not service: abort(404)
    related_articles = [a for a in ARTICLES if slug in a.get('related_services', [])][:3]
    return render_template(
        'service_detail.html', service=service, related_articles=related_articles,
        breadcrumbs=crumbs(('Services', url_for('services')), (service['title'], url_for('service_detail', slug=slug))),
    )

@app.route('/locations/<slug>')
def region_detail(slug):
    region = next((r for r in REGIONS if r['slug'] == slug), None)
    if not region: abort(404)
    return render_template(
        'region_detail.html', region=region,
        breadcrumbs=crumbs((region['name'], url_for('region_detail', slug=slug))),
    )

@app.route('/industries/<slug>')
def industry_detail(slug):
    industry = next((i for i in INDUSTRIES if i['slug'] == slug), None)
    if not industry: abort(404)
    return render_template(
        'industry_detail.html', industry=industry,
        breadcrumbs=crumbs((industry['name'], url_for('industry_detail', slug=slug))),
    )

@app.route('/insights')
def insights():
    items = [{'@type': 'ListItem', 'position': i, 'name': a['title'], 'url': SITE['url'] + '/insights/' + a['slug']}
             for i, a in enumerate(ARTICLES, start=1)]
    return render_template('insights.html', articles_schema=items,
                           breadcrumbs=crumbs(('Insights', url_for('insights'))))

@app.route('/insights/<slug>')
def article_detail(slug):
    article = next((a for a in ARTICLES if a['slug'] == slug), None)
    if not article: abort(404)
    related_services = [s for s in SERVICES if s['slug'] in article.get('related_services', [])] or SERVICES[:4]
    related_articles = [a for a in ARTICLES if a['slug'] != slug][:3]
    return render_template(
        'article_detail.html', article=article,
        related_services=related_services, related_articles=related_articles,
        og_type='article',
        breadcrumbs=crumbs(('Insights', url_for('insights')), (article['title'], url_for('article_detail', slug=slug))),
    )


# ============================================================
# AGENT AUTH
# ============================================================

@app.route('/agent-login', methods=['GET', 'POST'])
def agent_login():

    if "agent_id" in session:
        return redirect(url_for("agent_dashboard"))

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter your email and password.", "error")
            return render_template("agent-login.html")

        conn = get_db()
        agent = conn.execute(
            "SELECT * FROM agents WHERE email = ?", (email,)
        ).fetchone()
        conn.close()

        if agent and check_password_hash(agent["password_hash"], password):

            if not agent["is_approved"]:
                if agent["is_approved"] == -1:
                    flash("Your agent account has been rejected. Contact the administrator.", "error")
                else:
                    flash("Your account is pending admin approval. Please try again later.", "error")
                return render_template("agent-login.html")

            session.clear()
            session["agent_id"] = agent["id"]
            session["agent_name"] = agent["name"]
            session["agent_email"] = agent["email"]
            return redirect(url_for("agent_dashboard"))

        flash("Invalid email or password.", "error")

    return render_template("agent-login.html")


@app.route('/become-agent')
def become_agent():
    return render_template('become-agent.html',
                           breadcrumbs=crumbs(('Become an Agent', url_for('become_agent')), visible=False))


@app.route('/agent-register', methods=['GET', 'POST'])
def agent_register():

    if "agent_id" in session:
        return redirect(url_for("agent_dashboard"))

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        nin = request.form.get("nin", "").strip()
        dob = request.form.get("date_of_birth", "").strip()
        state = request.form.get("state", "").strip()
        address = request.form.get("address", "").strip()
        occupation = request.form.get("occupation", "").strip()
        motivation = request.form.get("motivation", "").strip()
        heard_from = request.form.get("heard_from", "").strip()
        bank_name = request.form.get("bank_name", "").strip()
        account_number = request.form.get("account_number", "").strip()
        account_name = request.form.get("account_name", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not name or not email or not password:
            flash("Please fill in all required fields.", "error")
            return render_template("agent-register.html")
        if not phone or not nin or not state:
            flash("Phone, NIN and State are required.", "error")
            return render_template("agent-register.html")
        if password != confirm:
            flash("Passwords do not match.", "error")
            return render_template("agent-register.html")
        if len(password) < 8:
            flash("Password must be at least 8 characters.", "error")
            return render_template("agent-register.html")
        if not nin.isdigit() or len(nin) != 11:
            flash("NIN must be exactly 11 digits.", "error")
            return render_template("agent-register.html")
        if account_number and (not account_number.isdigit() or len(account_number) != 10):
            flash("Account number must be exactly 10 digits.", "error")
            return render_template("agent-register.html")

        conn = get_db()

        if conn.execute("SELECT id FROM agents WHERE email = ?", (email,)).fetchone():
            conn.close()
            flash("An account with that email already exists.", "error")
            return render_template("agent-register.html")

        if conn.execute("SELECT id FROM agents WHERE nin = ?", (nin,)).fetchone():
            conn.close()
            flash("That NIN is already registered.", "error")
            return render_template("agent-register.html")

        conn.execute(
            """
            INSERT INTO agents (
                name, email, phone, nin, date_of_birth, state, address,
                occupation, motivation, heard_from,
                bank_name, account_number, account_name,
                password_hash, is_approved
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (
                name, email, phone, nin, dob, state, address,
                occupation, motivation, heard_from,
                bank_name, account_number, account_name,
                generate_password_hash(password),
            ),
        )
        conn.commit()
        conn.close()

        return redirect(url_for("agent_pending"))

    return render_template("agent-register.html")


@app.route('/agent-pending')
def agent_pending():
    return render_template('agent-pending.html')


# ============================================================
# AGENT DASHBOARD
# ============================================================

@app.route('/agent-dashboard')
@agent_required
def agent_dashboard():
    conn = get_db()

    leads = conn.execute(
        "SELECT * FROM leads WHERE agent_id = ? ORDER BY created_at DESC",
        (session["agent_id"],),
    ).fetchall()

    def sum_commission(rows, amount_field):
        total = 0.0
        for r in rows:
            v = r[amount_field]
            if v:
                total += float(v) * COMMISSION_RATE
        return total

    stats = {
        "total": len(leads),
        "pending": sum(1 for l in leads if l["status"] == "pending"),
        "rejected": sum(1 for l in leads if l["status"] == "rejected"),
        "lost": sum(1 for l in leads if l["status"] == "lost"),
        "approved": sum(1 for l in leads if l["status"] == "approved"),
        "in_progress": sum(
            1 for l in leads
            if l["status"] in {"accepted", "building", "completion", "prepare_to_be_paid"}
        ),
        "awaiting_confirmation": sum(1 for l in leads if l["status"] == "paid"),
        "completed": sum(1 for l in leads if l["status"] == "paid_confirmed"),

        "estimated": sum_commission(leads, "budget"),
        "awaiting_amount": sum_commission(
            [l for l in leads if l["status"] in {"accepted", "building", "completion", "prepare_to_be_paid"}],
            "agreed_price",
        ),
        "earned": sum(
            float(l["paid_amount"]) for l in leads
            if l["status"] == "paid_confirmed" and l["paid_amount"]
        ),
    }

    conn.close()

    return render_template(
        "agent-dashboard.html",
        agent_name=session.get("agent_name"),
        agent_email=session.get("agent_email"),
        leads=leads,
        stats=stats,
    )


@app.route('/agent/lead/new', methods=['POST'])
@agent_required
def agent_add_lead():
    budget_raw = request.form.get("budget", "").strip()
    budget = None
    if budget_raw:
        try:
            budget = float(budget_raw)
        except ValueError:
            flash("Budget must be a number.", "error")
            return redirect(url_for("agent_dashboard"))

    conn = get_db()
    conn.execute(
        """
        INSERT INTO leads (agent_id, name, email, phone, company, service, notes, budget)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            session["agent_id"],
            request.form.get("name", "").strip(),
            request.form.get("email", "").strip(),
            request.form.get("phone", "").strip(),
            request.form.get("company", "").strip(),
            request.form.get("service", "").strip(),
            request.form.get("notes", "").strip(),
            budget,
        ),
    )
    conn.commit()
    conn.close()
    flash("Lead submitted for admin review.", "success")
    return redirect(url_for("agent_dashboard"))


@app.route('/agent/lead/<int:lead_id>/budget', methods=['POST'])
@agent_required
def agent_update_lead_budget(lead_id):
    budget_raw = request.form.get("budget", "").strip()
    budget = None
    if budget_raw:
        try:
            budget = float(budget_raw)
        except ValueError:
            flash("Budget must be a number.", "error")
            return redirect(url_for("agent_dashboard"))

    conn = get_db()
    lead = conn.execute(
        "SELECT * FROM leads WHERE id = ? AND agent_id = ?",
        (lead_id, session["agent_id"]),
    ).fetchone()

    if not lead:
        conn.close()
        flash("Lead not found.", "error")
        return redirect(url_for("agent_dashboard"))

    if lead["status"] in ("paid", "paid_confirmed"):
        conn.close()
        flash("You cannot change the budget for a completed lead.", "error")
        return redirect(url_for("agent_dashboard"))

    conn.execute("UPDATE leads SET budget = ? WHERE id = ?", (budget, lead_id))
    conn.commit()
    conn.close()
    flash("Budget updated.", "success")
    return redirect(url_for("agent_dashboard"))


@app.route('/agent/lead/<int:lead_id>/accept', methods=['POST'])
@agent_required
def agent_accept_lead(lead_id):
    conn = get_db()
    lead = conn.execute(
        "SELECT * FROM leads WHERE id = ? AND agent_id = ?",
        (lead_id, session["agent_id"]),
    ).fetchone()

    if not lead:
        conn.close()
        flash("Lead not found.", "error")
        return redirect(url_for("agent_dashboard"))

    if lead["status"] != "approved":
        conn.close()
        flash("You can only accept a lead that has been approved by admin.", "error")
        return redirect(url_for("agent_dashboard"))

    conn.execute("UPDATE leads SET status = 'accepted' WHERE id = ?", (lead_id,))
    conn.commit()
    conn.close()
    flash("Lead marked as accepted. Admin will take it from here.", "success")
    return redirect(url_for("agent_dashboard"))


@app.route('/agent/lead/<int:lead_id>/lose', methods=['POST'])
@agent_required
def agent_lose_lead(lead_id):
    conn = get_db()
    lead = conn.execute(
        "SELECT * FROM leads WHERE id = ? AND agent_id = ?",
        (lead_id, session["agent_id"]),
    ).fetchone()

    if not lead:
        conn.close()
        flash("Lead not found.", "error")
        return redirect(url_for("agent_dashboard"))

    if lead["status"] not in ("approved", "accepted"):
        conn.close()
        flash("You cannot mark this lead as lost at this stage.", "error")
        return redirect(url_for("agent_dashboard"))

    conn.execute("UPDATE leads SET status = 'lost' WHERE id = ?", (lead_id,))
    conn.commit()
    conn.close()
    flash("Lead marked as lost.", "success")
    return redirect(url_for("agent_dashboard"))


@app.route('/agent/lead/<int:lead_id>/confirm', methods=['POST'])
@agent_required
def agent_confirm_receipt(lead_id):
    conn = get_db()
    lead = conn.execute(
        "SELECT * FROM leads WHERE id = ? AND agent_id = ?",
        (lead_id, session["agent_id"]),
    ).fetchone()

    if not lead:
        conn.close()
        flash("Lead not found.", "error")
        return redirect(url_for("agent_dashboard"))

    if lead["status"] != "paid":
        conn.close()
        flash("This lead is not awaiting confirmation.", "error")
        return redirect(url_for("agent_dashboard"))

    conn.execute(
        "UPDATE leads SET status = 'paid_confirmed', paid_confirmed_at = CURRENT_TIMESTAMP WHERE id = ?",
        (lead_id,),
    )
    conn.commit()
    conn.close()
    flash("Payment confirmed. Thank you!", "success")
    return redirect(url_for("agent_dashboard"))


@app.route('/agent-logout')
def agent_logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("agent_login"))


# ============================================================
# ADMIN AUTH
# ============================================================

@app.route('/admin-register', methods=['GET', 'POST'])
def admin_register():

    conn = get_db()
    admin_count = conn.execute("SELECT COUNT(*) FROM admins").fetchone()[0]

    if admin_count > 0:
        conn.close()
        flash("Admin setup is already complete.", "error")
        return redirect(url_for("admin_login"))

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not name or not email or not password:
            conn.close()
            flash("Please fill in all fields.", "error")
            return render_template("admin-register.html")

        if password != confirm:
            conn.close()
            flash("Passwords do not match.", "error")
            return render_template("admin-register.html")

        if len(password) < 8:
            conn.close()
            flash("Password must be at least 8 characters.", "error")
            return render_template("admin-register.html")

        conn.execute(
            "INSERT INTO admins (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, generate_password_hash(password)),
        )
        conn.commit()
        conn.close()
        flash("Admin account created. Please log in.", "success")
        return redirect(url_for("admin_login"))

    conn.close()
    return render_template("admin-register.html")


@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():

    if session.get("admin_logged_in"):
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter your email and password.", "error")
            return render_template("admin-login.html")

        conn = get_db()
        admin = conn.execute(
            "SELECT * FROM admins WHERE email = ?", (email,)
        ).fetchone()
        conn.close()

        if admin and check_password_hash(admin["password_hash"], password):
            session.clear()
            session["admin_logged_in"] = True
            session["admin_id"] = admin["id"]
            session["admin_name"] = admin["name"]
            session["admin_email"] = admin["email"]
            return redirect(url_for("admin_dashboard"))

        flash("Invalid admin credentials.", "error")

    return render_template("admin-login.html")


@app.route('/admin-logout')
def admin_logout():
    session.clear()
    flash("Signed out of admin.", "success")
    return redirect(url_for("admin_login"))


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@app.route('/admin')
@admin_required
def admin_dashboard():
    conn = get_db()

    agents = conn.execute("""
        SELECT a.*,
            (SELECT COUNT(*) FROM leads WHERE agent_id = a.id) AS lead_count
        FROM agents a
        ORDER BY a.created_at DESC
    """).fetchall()

    leads = conn.execute("""
        SELECT l.*, a.name AS agent_name, a.email AS agent_email
        FROM leads l
        JOIN agents a ON a.id = l.agent_id
        ORDER BY l.created_at DESC
    """).fetchall()

    stats = {
        "total_agents": conn.execute("SELECT COUNT(*) FROM agents").fetchone()[0],
        "pending_agents": conn.execute(
            "SELECT COUNT(*) FROM agents WHERE is_approved = 0"
        ).fetchone()[0],
        "total_leads": conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0],
        "pending_leads": conn.execute(
            "SELECT COUNT(*) FROM leads WHERE status = 'pending'"
        ).fetchone()[0],
        "accepted_leads": conn.execute(
            "SELECT COUNT(*) FROM leads WHERE status = 'accepted'"
        ).fetchone()[0],
        "building_leads": conn.execute(
            "SELECT COUNT(*) FROM leads WHERE status = 'building'"
        ).fetchone()[0],
        "completion_leads": conn.execute(
            "SELECT COUNT(*) FROM leads WHERE status = 'completion'"
        ).fetchone()[0],
        "prepare_leads": conn.execute(
            "SELECT COUNT(*) FROM leads WHERE status = 'prepare_to_be_paid'"
        ).fetchone()[0],
        "awaiting_confirm": conn.execute(
            "SELECT COUNT(*) FROM leads WHERE status = 'paid'"
        ).fetchone()[0],
        "successful_leads": conn.execute(
            "SELECT COUNT(*) FROM leads WHERE status = 'paid_confirmed'"
        ).fetchone()[0],
    }

    conn.close()

    return render_template(
        "admin.html", agents=agents, leads=leads, stats=stats
    )


@app.route('/admin/agent/<int:agent_id>')
@admin_required
def admin_view_agent(agent_id):
    conn = get_db()

    agent = conn.execute(
        "SELECT * FROM agents WHERE id = ?", (agent_id,)
    ).fetchone()

    if not agent:
        conn.close()
        flash("Agent not found.", "error")
        return redirect(url_for("admin_dashboard"))

    leads = conn.execute(
        "SELECT * FROM leads WHERE agent_id = ? ORDER BY created_at DESC",
        (agent_id,),
    ).fetchall()

    stats = {
        "total": len(leads),
        "pending": sum(1 for l in leads if l["status"] == "pending"),
        "in_progress": sum(
            1 for l in leads
            if l["status"] in {"accepted", "building", "completion", "prepare_to_be_paid"}
        ),
        "completed": sum(1 for l in leads if l["status"] == "paid_confirmed"),
    }

    conn.close()

    return render_template(
        "admin-agent-detail.html",
        agent=agent, leads=leads, stats=stats,
    )


@app.route('/admin/agent/<int:agent_id>/approve', methods=['POST'])
@admin_required
def admin_approve_agent(agent_id):
    conn = get_db()
    agent = conn.execute(
        "SELECT name, email, is_approved FROM agents WHERE id = ?", (agent_id,)
    ).fetchone()

    if not agent:
        conn.close()
        flash("Agent not found.", "error")
        return redirect(url_for("admin_dashboard"))

    already = agent["is_approved"] == 1
    conn.execute("UPDATE agents SET is_approved = 1 WHERE id = ?", (agent_id,))
    conn.commit()
    conn.close()

    if already:
        flash(f"{agent['name']} was already approved.", "success")
        return redirect(url_for("admin_dashboard"))

    sent = send_agent_approved_email(agent["name"], agent["email"])
    if sent:
        flash(f"{agent['name']} approved. Notification email sent.", "success")
    else:
        flash(f"{agent['name']} approved. Email could not be sent.", "error")
    return redirect(url_for("admin_dashboard"))


@app.route('/admin/agent/<int:agent_id>/reject', methods=['POST'])
@admin_required
def admin_reject_agent(agent_id):
    conn = get_db()
    conn.execute("UPDATE agents SET is_approved = -1 WHERE id = ?", (agent_id,))
    conn.commit()
    conn.close()
    flash("Agent rejected.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route('/admin/agent/<int:agent_id>/delete', methods=['POST'])
@admin_required
def admin_delete_agent(agent_id):
    conn = get_db()
    conn.execute("DELETE FROM leads WHERE agent_id = ?", (agent_id,))
    conn.execute("DELETE FROM agents WHERE id = ?", (agent_id,))
    conn.commit()
    conn.close()
    flash("Agent and their leads deleted.", "success")
    return redirect(url_for("admin_dashboard"))


# ============================================================
# ADMIN LEAD ACTIONS
# ============================================================

def _load_lead_with_agent(conn, lead_id):
    return conn.execute("""
        SELECT l.*, a.name AS agent_name, a.email AS agent_email
        FROM leads l JOIN agents a ON a.id = l.agent_id
        WHERE l.id = ?
    """, (lead_id,)).fetchone()


@app.route('/admin/lead/<int:lead_id>/approve', methods=['POST'])
@admin_required
def admin_approve_lead(lead_id):
    conn = get_db()
    conn.execute("UPDATE leads SET status = 'approved' WHERE id = ?", (lead_id,))
    conn.commit()
    conn.close()
    flash("Lead approved. Agent can now accept or lose it.", "success")
    return redirect(request.referrer or url_for("admin_dashboard"))


@app.route('/admin/lead/<int:lead_id>/reject', methods=['POST'])
@admin_required
def admin_reject_lead(lead_id):
    conn = get_db()
    conn.execute("UPDATE leads SET status = 'rejected' WHERE id = ?", (lead_id,))
    conn.commit()
    conn.close()
    flash("Lead rejected.", "success")
    return redirect(request.referrer or url_for("admin_dashboard"))


@app.route('/admin/lead/<int:lead_id>/agreed-price', methods=['POST'])
@admin_required
def admin_set_agreed_price(lead_id):
    raw = request.form.get("agreed_price", "").strip()
    try:
        agreed = float(raw)
    except ValueError:
        flash("Agreed price must be a number.", "error")
        return redirect(request.referrer or url_for("admin_dashboard"))

    if agreed <= 0:
        flash("Agreed price must be greater than zero.", "error")
        return redirect(request.referrer or url_for("admin_dashboard"))

    conn = get_db()
    lead = _load_lead_with_agent(conn, lead_id)

    if not lead:
        conn.close()
        flash("Lead not found.", "error")
        return redirect(url_for("admin_dashboard"))

    if lead["status"] != "accepted":
        conn.close()
        flash("You can only set the price on an accepted lead.", "error")
        return redirect(request.referrer or url_for("admin_dashboard"))

    conn.execute(
        "UPDATE leads SET agreed_price = ? WHERE id = ?",
        (agreed, lead_id),
    )
    conn.commit()
    conn.close()

    sent = send_agreed_price_email(
        lead["agent_name"], lead["agent_email"], lead["name"], agreed
    )
    if sent:
        flash(f"Agreed price set. Email sent to {lead['agent_name']}.", "success")
    else:
        flash("Agreed price saved. Email could not be sent.", "error")
    return redirect(request.referrer or url_for("admin_dashboard"))


@app.route('/admin/lead/<int:lead_id>/building', methods=['POST'])
@admin_required
def admin_lead_building(lead_id):
    conn = get_db()
    lead = _load_lead_with_agent(conn, lead_id)

    if not lead:
        conn.close()
        flash("Lead not found.", "error")
        return redirect(url_for("admin_dashboard"))

    if lead["status"] != "accepted":
        conn.close()
        flash("Lead must be in 'accepted' state.", "error")
        return redirect(request.referrer or url_for("admin_dashboard"))

    if not lead["agreed_price"]:
        conn.close()
        flash("Please set the agreed price first.", "error")
        return redirect(request.referrer or url_for("admin_dashboard"))

    conn.execute("UPDATE leads SET status = 'building' WHERE id = ?", (lead_id,))
    conn.commit()
    conn.close()
    flash("Lead moved to Building.", "success")
    return redirect(request.referrer or url_for("admin_dashboard"))


@app.route('/admin/lead/<int:lead_id>/completion', methods=['POST'])
@admin_required
def admin_lead_completion(lead_id):
    conn = get_db()
    conn.execute(
        "UPDATE leads SET status = 'completion' WHERE id = ? AND status = 'building'",
        (lead_id,),
    )
    conn.commit()
    conn.close()
    flash("Lead moved to Completion.", "success")
    return redirect(request.referrer or url_for("admin_dashboard"))


@app.route('/admin/lead/<int:lead_id>/prepare-payment', methods=['POST'])
@admin_required
def admin_lead_prepare_payment(lead_id):
    conn = get_db()
    conn.execute(
        "UPDATE leads SET status = 'prepare_to_be_paid' WHERE id = ? AND status = 'completion'",
        (lead_id,),
    )
    conn.commit()
    conn.close()
    flash("Lead moved to Prepare to be Paid.", "success")
    return redirect(request.referrer or url_for("admin_dashboard"))


@app.route('/admin/lead/<int:lead_id>/paid', methods=['POST'])
@admin_required
def admin_lead_paid(lead_id):
    raw = request.form.get("paid_amount", "").strip()
    try:
        paid = float(raw)
    except ValueError:
        flash("Paid amount must be a number.", "error")
        return redirect(request.referrer or url_for("admin_dashboard"))

    if paid <= 0:
        flash("Paid amount must be greater than zero.", "error")
        return redirect(request.referrer or url_for("admin_dashboard"))

    conn = get_db()
    lead = _load_lead_with_agent(conn, lead_id)

    if not lead:
        conn.close()
        flash("Lead not found.", "error")
        return redirect(url_for("admin_dashboard"))

    if lead["status"] != "prepare_to_be_paid":
        conn.close()
        flash("Lead must be in 'prepare to be paid' state.", "error")
        return redirect(request.referrer or url_for("admin_dashboard"))

    conn.execute(
        "UPDATE leads SET status = 'paid', paid_amount = ? WHERE id = ?",
        (paid, lead_id),
    )
    conn.commit()
    conn.close()

    sent = send_paid_email(
        lead["agent_name"], lead["agent_email"], lead["name"], paid
    )
    if sent:
        flash(f"Marked as Paid. Email sent to {lead['agent_name']}.", "success")
    else:
        flash("Marked as Paid. Email could not be sent.", "error")
    return redirect(request.referrer or url_for("admin_dashboard"))


# ============================================================
# CONTACT / SEO
# ============================================================

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        sent = send_contact_email(request.form)
        flash(
            'Your message has been sent. We\'ll get back to you soon.'
            if sent else
            f'Something went wrong. Please email {MAIL_RECIPIENT} directly.',
            'success' if sent else 'error',
        )
        return redirect(url_for('contact'))
    return render_template('contact.html', breadcrumbs=crumbs(('Contact', url_for('contact'))))


@app.route('/sitemap.xml')
def sitemap():
    """Only real, indexable URLs, each with an honest <lastmod> (not 'today' on every request)."""
    pages = []

    def add(endpoint, lastmod=CONTENT_UPDATED, **kwargs):
        pages.append({'url': SITE['url'] + url_for(endpoint, **kwargs), 'lastmod': lastmod})

    for endpoint in ['home', 'about', 'vision', 'services', 'work', 'insights', 'contact', 'become_agent']:
        add(endpoint)
    for s in SERVICES: add('service_detail', slug=s['slug'])
    for r in REGIONS: add('region_detail', slug=r['slug'])
    for i in INDUSTRIES: add('industry_detail', slug=i['slug'])
    for a in ARTICLES: add('article_detail', lastmod=a['updated'], slug=a['slug'])
    for p in PROJECTS: add('project_detail', slug=p['id'])
    return render_template('sitemap.xml', pages=pages), {'Content-Type': 'application/xml; charset=utf-8'}


@app.route('/robots.txt')
def robots():
    return render_template('robots.txt'), {'Content-Type': 'text/plain'}


if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG') == '1', host='0.0.0.0', port=5000)