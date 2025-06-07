#!/usr/bin/env python3
"""
📰 RadioX RSS Service - Standalone CLI
Pure RSS data collection testing interface - ALL feeds
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path for src imports
sys.path.append(str(Path(__file__).parent.parent))

from src.services.rss_service import RSSService


def generate_rss_html(feeds, news, stats):
    """Generate modern RSS dashboard HTML"""
    
    # Calculate category stats
    categories = {}
    for article in news:
        cat = article.category
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += 1
    
    # Source stats
    sources = {}
    for feed in feeds:
        source = feed['source_name']
        if source not in sources:
            sources[source] = []
        sources[source].append(feed)
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📰 RadioX RSS Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            min-height: 100vh;
            color: #2c3e50;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 25px;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 8px;
            color: #2c3e50;
            font-weight: 600;
        }}
        
        .header p {{
            font-size: 1.1rem;
            color: #7f8c8d;
        }}
        
        .stats-row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }}
        
        .stat-mini {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-left: 4px solid #3498db;
        }}
        
        .stat-mini-number {{
            font-size: 2rem;
            font-weight: bold;
            color: #2c3e50;
        }}
        
        .stat-mini-label {{
            font-size: 0.9rem;
            color: #7f8c8d;
            text-transform: uppercase;
            margin-top: 5px;
            font-weight: 500;
        }}
        
        .section {{
            background: white;
            border-radius: 8px;
            padding: 25px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 25px;
        }}
        
        .section h2 {{
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.5rem;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            font-weight: 600;
        }}
        
        .controls {{
            display: flex;
            gap: 25px;
            margin-bottom: 25px;
            flex-wrap: wrap;
            align-items: center;
            background: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #bdc3c7;
        }}
        
        .filter-group {{
            display: flex;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
        }}
        
        .filter-label {{
            font-weight: 600;
            color: #2c3e50;
            font-size: 0.95rem;
            margin-right: 8px;
        }}
        
        .filter-tag {{
            background: white;
            border: 2px solid #bdc3c7;
            color: #2c3e50;
            padding: 8px 15px;
            border-radius: 6px;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            white-space: nowrap;
            font-weight: 500;
        }}
        
        .filter-tag:hover {{
            background: #3498db;
            color: white;
            border-color: #3498db;
        }}
        
        .filter-tag.active {{
            background: #2980b9;
            color: white;
            border-color: #2980b9;
        }}
        
        .sort-select {{
            padding: 10px 15px;
            border: 2px solid #bdc3c7;
            border-radius: 6px;
            background: white;
            color: #2c3e50;
            font-size: 0.9rem;
            cursor: pointer;
            font-weight: 500;
        }}
        
        .news-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            font-size: 0.9rem;
            background: white;
        }}
        
        .news-table th {{
            background: #34495e;
            color: white;
            padding: 15px 12px;
            text-align: left;
            font-weight: 600;
            font-size: 0.9rem;
            border: none;
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        
        .news-table td {{
            padding: 15px 12px;
            border-bottom: 1px solid #ecf0f1;
            vertical-align: top;
        }}
        
        .news-table tr:hover {{
            background: #f8f9fa;
        }}
        
        .news-table tr:nth-child(even) {{
            background: #fafbfc;
        }}
        
        .news-table tr:nth-child(even):hover {{
            background: #f1f3f4;
        }}
        
        .news-title-cell {{
            max-width: 400px;
            min-width: 300px;
        }}
        
        .news-title-link {{
            color: #2c3e50;
            text-decoration: none;
            font-weight: 500;
            line-height: 1.4;
            display: block;
        }}
        
        .news-title-link:hover {{
            color: #3498db;
            text-decoration: underline;
        }}
        
        .category-badge {{
            background: #3498db;
            color: white;
            padding: 5px 12px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            white-space: nowrap;
        }}
        
        .source-badge {{
            background: #95a5a6;
            color: white;
            padding: 5px 12px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 500;
            white-space: nowrap;
        }}
        
        .priority-badge {{
            background: #27ae60;
            color: white;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 600;
        }}
        
        .time-badge {{
            background: #7f8c8d;
            color: white;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.8rem;
            white-space: nowrap;
            font-weight: 500;
        }}
        
        .link-group {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        
        .external-link {{
            color: #3498db;
            text-decoration: none;
            font-size: 0.85rem;
            font-weight: 500;
            padding: 4px 8px;
            border: 1px solid #3498db;
            border-radius: 4px;
            transition: all 0.2s ease;
        }}
        
        .external-link:hover {{
            background: #3498db;
            color: white;
        }}
        
        .rss-link {{
            color: #e67e22;
            text-decoration: none;
            font-size: 0.85rem;
            font-weight: 500;
            padding: 4px 8px;
            border: 1px solid #e67e22;
            border-radius: 4px;
            transition: all 0.2s ease;
        }}
        
        .rss-link:hover {{
            background: #e67e22;
            color: white;
        }}
        
        .timestamp {{
            text-align: center;
            color: #7f8c8d;
            margin-top: 25px;
            font-size: 0.9rem;
            padding: 15px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        @media (max-width: 768px) {{
            .controls {{
                flex-direction: column;
                align-items: stretch;
            }}
            
            .filter-group {{
                justify-content: center;
            }}
            
            .news-table {{
                font-size: 0.8rem;
            }}
            
            .news-table th,
            .news-table td {{
                padding: 10px 8px;
            }}
            
            .news-title-cell {{
                min-width: 250px;
            }}
            
            .link-group {{
                flex-direction: column;
                gap: 5px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📰 RadioX RSS Dashboard</h1>
            <p>Real-time news aggregation from all active sources</p>
        </div>
        
        <div class="stats-row">
            <div class="stat-mini">
                <div class="stat-mini-number">{len(feeds)}</div>
                <div class="stat-mini-label">Total Feeds</div>
            </div>
            <div class="stat-mini">
                <div class="stat-mini-number">{len(news)}</div>
                <div class="stat-mini-label">Articles</div>
            </div>
            <div class="stat-mini">
                <div class="stat-mini-number">{len(set(n.source for n in news))}</div>
                <div class="stat-mini-label">Active Sources</div>
            </div>
            <div class="stat-mini">
                <div class="stat-mini-number">{len(categories)}</div>
                <div class="stat-mini-label">Categories</div>
            </div>
        </div>
        
        <div class="content-grid">
            <div class="section">
                <h2>📰 News Dashboard</h2>
                
                <!-- Filter Controls -->
                <div class="controls">
                    <div class="filter-group">
                        <span class="filter-label">Categories:</span>
                        <a href="#" class="filter-tag active" data-category="all">All</a>"""
    
    # Add category filter tags
    for category in sorted(categories.keys()):
        html_content += f"""
                     <a href="#" class="filter-tag" data-category="{category}">{category} ({categories[category]})</a>"""
    
    html_content += """
                 </div>
                 
                 <div class="filter-group">
                     <span class="filter-label">Sort:</span>
                     <select class="sort-select" id="sortSelect">
                         <option value="latest">Latest First</option>
                         <option value="oldest">Oldest First</option>
                         <option value="priority">Priority High→Low</option>
                         <option value="source">Source A→Z</option>
                         <option value="category">Category A→Z</option>
                     </select>
                 </div>
                 </div>
                 
                 <!-- News Table -->
                 <table class="news-table" id="newsTable">
                     <thead>
                         <tr>
                             <th style="width: 35%;">Title</th>
                             <th style="width: 10%;">Category</th>
                             <th style="width: 10%;">Source</th>
                             <th style="width: 8%;">Priority</th>
                             <th style="width: 8%;">Weight</th>
                             <th style="width: 8%;">Age</th>
                             <th style="width: 21%;">Links</th>
                         </tr>
                     </thead>
                     <tbody>"""
    
    # Add all news items to table with RSS feed links
    for i, article in enumerate(news, 1):
        hours_old = int((datetime.now() - article.published).total_seconds() / 3600)
        safe_title = article.title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
        
        # Find the RSS feed URL for this article's source
        rss_feed_url = "#"
        for feed in feeds:
            if feed['source_name'] == article.source:
                rss_feed_url = feed['feed_url']
                break
        
        html_content += f"""
                     <tr data-category="{article.category}" data-priority="{article.priority}" data-age="{hours_old}" data-source="{article.source}">
                         <td class="news-title-cell">
                             <a href="{article.link}" target="_blank" class="news-title-link" rel="noopener noreferrer">
                                 {safe_title}
                             </a>
                         </td>
                         <td>
                             <span class="category-badge">{article.category}</span>
                         </td>
                         <td>
                             <span class="source-badge">{article.source}</span>
                         </td>
                         <td>
                             <span class="priority-badge">P{article.priority}</span>
                         </td>
                         <td>
                             <span style="font-weight: 500;">{article.weight}</span>
                         </td>
                         <td>
                             <span class="time-badge">{hours_old}h</span>
                         </td>
                         <td>
                             <div class="link-group">
                                 <a href="{article.link}" target="_blank" class="external-link" rel="noopener noreferrer">📰 Article</a>
                                 <a href="{rss_feed_url}" target="_blank" class="rss-link" rel="noopener noreferrer">📡 RSS Feed</a>
                             </div>
                         </td>
                     </tr>"""
    
    html_content += """
                 </tbody>
             </table>
         </div>
         
         <div class="section">
             <h2>📡 RSS Sources Overview</h2>
             <table class="news-table">
                 <thead>
                     <tr>
                         <th style="width: 25%;">Source</th>
                         <th style="width: 15%;">Priority</th>
                         <th style="width: 15%;">Weight</th>
                         <th style="width: 30%;">Categories</th>
                         <th style="width: 15%;">Actions</th>
                     </tr>
                 </thead>
                 <tbody>"""
    
    # Add RSS sources to table
    for source_name, source_feeds in sources.items():
        priority = source_feeds[0]['priority']
        weight = source_feeds[0]['weight']
        categories_list = [f['feed_category'] for f in source_feeds]
        source_url = source_feeds[0]['feed_url']
        
        html_content += f"""
                     <tr>
                         <td>
                             <strong style="color: #667eea;">{source_name}</strong>
                         </td>
                         <td>
                             <span class="priority-badge">P{priority}</span>
                         </td>
                         <td>
                             <span style="font-weight: 500;">{weight}</span>
                         </td>
                         <td>
                             <div style="display: flex; gap: 5px; flex-wrap: wrap;">"""
        
        for feed in source_feeds:
            html_content += f"""
                                 <span class="category-badge" style="font-size: 0.7rem;">{feed['feed_category']}</span>"""
        
        html_content += f"""
                             </div>
                         </td>
                         <td>
                             <a href="{source_url}" target="_blank" class="external-link" rel="noopener noreferrer">🔗 RSS Feed</a>
                         </td>
                     </tr>"""
    
    html_content += """
                 </tbody>
             </table>
         </div>
         
         <script>
             document.addEventListener('DOMContentLoaded', function() {{
                 // Filter functionality
                 const filterTags = document.querySelectorAll('.filter-tag');
                 const sortSelect = document.getElementById('sortSelect');
                 
                 // Add click event listeners to filter tags
                 filterTags.forEach(tag => {{
                     tag.addEventListener('click', function(e) {{
                         e.preventDefault();
                         const category = this.dataset.category;
                         
                         // Update active filter tag
                         filterTags.forEach(t => t.classList.remove('active'));
                         this.classList.add('active');
                         
                         // Filter table rows
                         filterByCategory(category);
                     }});
                 }});
                 
                 // Add change event listener to sort select
                 sortSelect.addEventListener('change', function() {{
                     sortTable(this.value);
                 }});
                 
                 function filterByCategory(category) {{
                     const table = document.getElementById('newsTable');
                     const rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');
                     
                     // Filter rows
                     for (let row of rows) {{
                         if (category === 'all' || row.dataset.category === category) {{
                             row.style.display = '';
                         }} else {{
                             row.style.display = 'none';
                         }}
                     }}
                 }}
                 
                 function sortTable(sortBy) {{
                     const table = document.getElementById('newsTable');
                     const tbody = table.getElementsByTagName('tbody')[0];
                     const rows = Array.from(tbody.getElementsByTagName('tr'));
                     
                     rows.sort((a, b) => {{
                         switch(sortBy) {{
                             case 'latest':
                                 return parseInt(a.dataset.age) - parseInt(b.dataset.age);
                             case 'oldest':
                                 return parseInt(b.dataset.age) - parseInt(a.dataset.age);
                             case 'priority':
                                 return parseInt(b.dataset.priority) - parseInt(a.dataset.priority);
                             case 'source':
                                 return a.dataset.source.localeCompare(b.dataset.source);
                             case 'category':
                                 return a.dataset.category.localeCompare(b.dataset.category);
                             default:
                                 return 0;
                         }}
                     }});
                     
                     // Re-append sorted rows
                     rows.forEach(row => tbody.appendChild(row));
                 }}
             }});
         </script>
         
         <div class="timestamp">
             Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
         </div>
    </div>
</body>
</html>"""
    
    return html_content


async def main():
    parser = argparse.ArgumentParser(description="📰 RadioX RSS Service")
    parser.add_argument("--hours", type=int, default=12, help="Max age in hours")
    parser.add_argument("--limit", type=int, default=15, help="Max number of results to display")
    parser.add_argument("--no-html", action="store_true", help="Skip HTML generation")
    
    args = parser.parse_args()
    
    print("📰 RSS SERVICE")
    print("=" * 30)
    
    service = RSSService()
    
    try:
        # Get ALL active feed configurations
        feeds = await service.get_all_active_feeds()
        
        if not feeds:
            print("❌ No active RSS feeds found")
            return
        
        # Collect recent news from ALL feeds
        news = await service.get_all_recent_news(max_age_hours=args.hours)
        
        if not news:
            print("⚠️ No recent news found")
            return
        
        # Display results
        print(f"📡 FEEDS: {len(feeds)} total configured")
        print(f"📰 NEWS: {len(news)} articles collected ({args.hours}h)")
        print(f"🔗 SOURCES: {len(set(n.source for n in news))} active")
        
        # Show top news
        print(f"\n🎯 TOP {min(args.limit, len(news))} NEWS:")
        for i, article in enumerate(news[:args.limit], 1):
            hours_old = int((datetime.now() - article.published).total_seconds() / 3600)
            print(f"{i:2d}. [{article.category}] {article.title[:60]}...")
            print(f"    📰 {article.source} | ⏰ {hours_old}h | 🎯 P{article.priority} | ⚖️ W{article.weight}")
        
        # Show feed summary by source
        print(f"\n📊 FEED SUMMARY:")
        sources = {}
        for feed in feeds:
            source = feed['source_name']
            if source not in sources:
                sources[source] = []
            sources[source].append(feed)
        
        for source_name, source_feeds in sources.items():
            priority = source_feeds[0]['priority']
            weight = source_feeds[0]['weight']
            categories = [f['feed_category'] for f in source_feeds]
            print(f"  📰 {source_name}: P{priority}, W{weight} ({', '.join(categories)})")
        
        # Show category distribution
        print(f"\n📊 CATEGORY DISTRIBUTION:")
        categories = {}
        for article in news:
            cat = article.category
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1
        
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  📂 {category}: {count} articles")
        
        # Generate HTML Dashboard
        if not args.no_html:
            print(f"\n🎨 Generating HTML dashboard...")
            
            # Find project root and create outplay directory
            current_dir = Path(__file__).parent
            project_root = current_dir.parent.parent  # Go up to RadioX root
            outplay_dir = project_root / "outplay"
            outplay_dir.mkdir(exist_ok=True)
            
            # Generate HTML content
            stats = {
                'feeds': len(feeds),
                'news': len(news),
                'sources': len(set(n.source for n in news)),
                'categories': len(categories)
            }
            
            html_content = generate_rss_html(feeds, news, stats)
            
            # Write HTML file
            html_file = outplay_dir / "rss.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ HTML dashboard created: {html_file}")
            print(f"🌐 Open in browser: file://{html_file.absolute()}")
        
        print(f"\n✅ RSS service operational - ALL feeds processed")
        
    except Exception as e:
        print(f"❌ RSS service error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 