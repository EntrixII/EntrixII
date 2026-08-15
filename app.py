from PIL import Image
from flask import Flask, render_template, request, redirect, url_for, flash
import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()  # reads variables from a .env file in the project root, if present

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# --- Email (contact form) configuration ---
# Set these as environment variables — never hardcode credentials.
#   MAIL_USERNAME   -> the Gmail address that sends the email (e.g. entrix2026@gmail.com)
#   MAIL_PASSWORD   -> a Gmail App Password (NOT your normal Gmail password)
#   MAIL_RECIPIENT  -> where the message should land (defaults to entrix2026@gmail.com)
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
MAIL_RECIPIENT = os.environ.get('MAIL_RECIPIENT', 'entrix2026@gmail.com')


def send_contact_email(form):
    """Send the contact form submission via Gmail SMTP. Returns True on success."""
    if not MAIL_USERNAME or not MAIL_PASSWORD:
        app.logger.warning('MAIL_USERNAME / MAIL_PASSWORD not set — contact email not sent.')
        return False

    name = form.get('name', '').strip()
    email = form.get('email', '').strip()
    company = form.get('company', '').strip()
    service = form.get('service', '').strip()
    description = form.get('description', '').strip()
    budget = form.get('budget', '').strip()

    service_title = next((s['title'] for s in SERVICES if s['id'] == service), service)

    msg = EmailMessage()
    msg['Subject'] = f'New project inquiry from {name or "website visitor"}'
    msg['From'] = MAIL_USERNAME
    msg['To'] = MAIL_RECIPIENT
    if email:
        msg['Reply-To'] = email

    msg.set_content(
        "New message from the Entrix II contact form\n"
        "--------------------------------------------\n"
        f"Name:      {name}\n"
        f"Email:     {email}\n"
        f"Company:   {company or '—'}\n"
        f"Service:   {service_title or '—'}\n"
        f"Budget:    {budget or '—'}\n"
        "\n"
        "Project description:\n"
        f"{description}\n"
    )

    try:
        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT, timeout=10) as smtp:
            smtp.starttls()
            smtp.login(MAIL_USERNAME, MAIL_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as exc:
        app.logger.error(f'Failed to send contact email: {exc}')
        return False


# Site configuration
SITE = {
    'name': 'Entrix II',
    'url': 'https://entrixii.com',  # change to actual domain
    'tagline': 'building what\'s next',
}

SOCIAL = {
    'github': 'https://github.com/EntrixII',
    'twitter': 'https://twitter.com/is_real999',
    'linkedin': '#',
    'instagram': '#',
    'facebook': '#',
    'whatsapp': '#',
    'email': 'hello@entrixii.com',
}

# Project data
PROJECTS = [
    {
        'id': 'jecyani-properties',
        'title': 'Jecyani Properties',
        'category': 'Real Estate',
        'url': 'https://jecyaniproperties.com/',
        'live': True,
        'description': 'A modern real estate platform showcasing properties with a sleek, trust-driven interface. Built for speed and conversion.',
        'image': 'project1.jpg',
        'technologies': ['Flask', 'Tailwind CSS', 'JavaScript', 'PostgreSQL'],
        'challenge': 'The client needed a digital presence that reflected their premium property portfolio while being easy to manage.',
        'solution': 'We built a custom CMS with property listings, advanced search, and a streamlined contact system.',
    },
    {
        'id': 'crownbee-global',
        'title': 'Crownbee Global Services',
        'category': 'Real Estate',
        'url': 'https://crownbeeglobalservices.com/',
        'live': True,
        'description': 'A corporate website for international real estate services, emphasizing trust and global reach.',
        'image': 'project2.jpg',
        'technologies': ['React', 'Node.js', 'MongoDB', 'AWS'],
        'challenge': 'Showcasing a diverse portfolio across multiple countries with a unified brand voice.',
        'solution': 'A multi-language site with dynamic content blocks and a powerful backend.',
    },
    {
        'id': 'verrazzano',
        'title': 'Verrazzano',
        'category': 'Furniture',
        'url': None,
        'live': False,
        'description': 'A high-end furniture brand concept. This case study explores e‑commerce and immersive product presentation.',
        'image': 'project3.jpg',
        'technologies': ['Next.js', 'Three.js', 'Stripe', 'GraphQL'],
        'challenge': 'Creating a digital showroom that feels as luxurious as the physical products.',
        'solution': 'A 3D product viewer with AR preview, integrated with a headless CMS for inventory.',
    },
    {
        'id': 'michie-plus',
        'title': 'Michie Plus',
        'category': 'E‑commerce',
        'url': None,
        'live': False,
        'description': 'A full-featured e‑commerce platform for fashion and lifestyle. Currently a case study of scalable architecture.',
        'image': 'project4.jpg',
        'technologies': ['Vue.js', 'Django', 'PostgreSQL', 'Redis', 'Celery'],
        'challenge': 'Handling high traffic during flash sales with a seamless checkout experience.',
        'solution': 'Microservices architecture with a message queue for order processing, and a responsive Vue storefront.',
    },
    {
        'id': 'becca-treats',
        'title': 'Becca Treats',
        'category': 'Food & Treats',
        'url': None,
        'live': False,
        'description': 'A delightful brand for homemade treats. This case study focuses on brand storytelling and online ordering.',
        'image': 'project5.jpg',
        'technologies': ['WordPress', 'WooCommerce', 'Custom Theme', 'SEO'],
        'challenge': 'Translating the warmth of a local bakery into a digital experience.',
        'solution': 'A custom WordPress theme with a focus on visuals and a simple ordering flow.',
    }
]

SERVICES = [
    {
        'id': 'website-development', 'title': 'Website Development', 'icon': '💻',
        'description': 'Custom-built, high-performance websites engineered from scratch — no bloated page builders, no cookie-cutter templates.',
        'features': ['Responsive, mobile-first builds', 'Fast-loading, SEO-ready architecture', 'Scalable Flask & Python backends'],
    },
    {
        'id': 'website-design', 'title': 'Website Design & Redesign', 'icon': '🎨',
        'description': 'Modern interfaces and full redesigns that turn outdated sites into fast, credible digital storefronts.',
        'features': ['Brand-aligned visual design', 'UX audits & redesign strategy', 'Conversion-focused layouts'],
    },
    {
        'id': 'web-applications', 'title': 'Web Applications', 'icon': '🧩',
        'description': 'Full-stack applications with real business logic — dashboards, portals, booking systems and internal tools.',
        'features': ['Custom backend logic & APIs', 'User authentication & roles', 'Database-driven features'],
    },
    {
        'id': 'mobile-applications', 'title': 'Mobile Applications', 'icon': '📱',
        'description': 'Mobile-friendly experiences and app-like interfaces that work seamlessly across devices.',
        'features': ['Responsive progressive web apps', 'Cross-device compatibility', 'App-like performance & feel'],
    },
    {
        'id': 'ecommerce', 'title': 'E-commerce', 'icon': '🛒',
        'description': 'Complete online stores built for real transactions — product catalogs, checkout and payment integration.',
        'features': ['Product & inventory management', 'Secure checkout & payments', 'Order & customer management'],
    },
    {
        'id': 'ui-ux', 'title': 'UI/UX', 'icon': '🎯',
        'description': 'Interfaces designed around real users — clear, usable and built to convert visitors into customers.',
        'features': ['Wireframing & prototyping', 'Usability-first interface design', 'Accessibility & responsive layouts'],
    },
    {
        'id': 'seo', 'title': 'SEO', 'icon': '🔍',
        'description': "Technical and on-page SEO that helps businesses get found, not just built.",
        'features': ['Technical SEO & site architecture', 'Metadata, schema & structured data', 'Search Console setup & monitoring'],
    },
    {
        'id': 'ai-automation', 'title': 'AI & Automation', 'icon': '🤖',
        'description': 'Practical AI integrations and automated workflows that save time and reduce manual work.',
        'features': ['AI-powered features & chat tools', 'Workflow & task automation', 'Third-party API integrations'],
    },
    {
        'id': 'custom-software', 'title': 'Custom Software / Digital Solutions', 'icon': '⚙️',
        'description': "Bespoke software built around a specific business workflow that off-the-shelf tools can't solve.",
        'features': ['Business-specific platforms', 'Admin & vendor dashboards', 'Scalable, maintainable architecture'],
    },
]

@app.context_processor
def inject_globals():
    return {
        'site': SITE,
        'social': SOCIAL,
        'projects': PROJECTS,
        'services': SERVICES,
        'now': datetime.now(),
    }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/work')
def work():
    return render_template('work.html', projects=PROJECTS)

@app.route('/work/<slug>')
def project_detail(slug):
    project = next((p for p in PROJECTS if p['id'] == slug), None)
    if not project:
        return "Project not found", 404
    return render_template('project_detail.html', project=project)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        sent = send_contact_email(request.form)
        if sent:
            flash('Your message has been sent. We\'ll get back to you soon.', 'success')
        else:
            flash(
                'Something went wrong sending your message. Please email us '
                f'directly at {MAIL_RECIPIENT}.',
                'error'
            )
        return redirect(url_for('contact'))
    return render_template('contact.html')

# Sitemap
@app.route('/sitemap.xml')
def sitemap():
    pages = [
        {'url': url_for('home'), 'priority': '1.0', 'changefreq': 'weekly'},
        {'url': url_for('about'), 'priority': '0.8', 'changefreq': 'monthly'},
        {'url': url_for('services'), 'priority': '0.8', 'changefreq': 'monthly'},
        {'url': url_for('work'), 'priority': '0.9', 'changefreq': 'weekly'},
    ]
    for p in PROJECTS:
        pages.append({
            'url': url_for('project_detail', slug=p['id']),
            'priority': '0.7',
            'changefreq': 'monthly'
        })
    pages.append({'url': url_for('contact'), 'priority': '0.6', 'changefreq': 'yearly'})
    return render_template('sitemap.xml', pages=pages), {'Content-Type': 'application/xml'}

# Robots.txt
@app.route('/robots.txt')
def robots():
    return render_template('robots.txt'), {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)