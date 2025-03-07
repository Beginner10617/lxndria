from flask import Blueprint, send_from_directory, Response, request
import datetime
sitemaps_bp = Blueprint('sitemaps', __name__)

def get_pages():
    """List of relative paths instead of full URLs"""
    return [
        {"path": "/", "priority": "1.0"},
        {"path": "/about", "priority": "0.9"},
        {"path": "/register", "priority": "0.8"},
        {"path": "/login", "priority": "0.7"},
    ]

@sitemaps_bp.route('/sitemap.xml')
def dynamic_sitemap():
    """Dynamically generates sitemap.xml with the current host"""
    lastmod = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    base_url = request.host_url.rstrip("/")  # Gets the current domain dynamically
    if base_url.startswith("http://"):
        base_url = base_url.replace("http://", "https://", 1)  # Force HTTPS

    sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>'
    sitemap_xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'

    for page in get_pages():
        full_url = f"{base_url}{page['path']}"
        sitemap_xml += f"""
        <url>
            <loc>{full_url}</loc>
            <lastmod>{lastmod}</lastmod>
            <priority>{page['priority']}</priority>
        </url>
        """

    sitemap_xml += "</urlset>"

    return Response(sitemap_xml, mimetype="application/xml")