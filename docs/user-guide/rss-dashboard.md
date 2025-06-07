# 📰 RSS Dashboard Guide

<div align="center">

![User Guide](https://img.shields.io/badge/guide-user-green)
![Difficulty](https://img.shields.io/badge/difficulty-beginner-brightgreen)
![Time](https://img.shields.io/badge/time-10%20min-orange)

**📊 Complete guide to using the RadioX RSS Dashboard**

[🏠 Documentation](../) • [👥 User Guides](../README.md#-user-guides) • [🎙️ Show Generation](show-generation.md) • [📚 API Reference](api-reference.md)

</div>

---

## 🎯 Overview

The **RSS Dashboard** is a modern, professional web interface that provides real-time access to all RSS feeds and news articles collected by RadioX. It features live filtering, sorting, and comprehensive analytics.

### ✨ **Key Features**
- 📊 **Real-time Statistics** - Live feed and article counts
- 🏷️ **Category Filtering** - Filter by news categories with one click
- 🔄 **Smart Sorting** - Sort by date, priority, source, or category
- 🔗 **Dual Links** - Direct access to articles and RSS feeds
- 📱 **Responsive Design** - Works perfectly on desktop and mobile
- 🎨 **Professional UI** - Modern business design with clean tables

---

## 🚀 Quick Start

### **1. Generate Dashboard**
```bash
# Navigate to CLI directory
cd backend/cli

# Generate RSS dashboard
python cli_rss.py

# Output:
📰 RSS SERVICE
📡 FEEDS: 30 total configured
📰 NEWS: 98 articles collected (12h)
🎨 Generating HTML dashboard...
✅ HTML dashboard created: /outplay/rss.html
🌐 Open in browser: file:///path/to/rss.html
```

### **2. Open Dashboard**
The dashboard is automatically created at:
```
/outplay/rss.html
```

Simply **double-click** the file or open it in your web browser.

---

## 📊 Dashboard Overview

### **📈 Statistics Cards**
At the top, you'll see real-time statistics:

| 📊 Metric | 📝 Description |
|-----------|----------------|
| **Total Feeds** | Number of RSS feeds configured (30) |
| **Articles** | Total articles collected (98) |
| **Active Sources** | News sources providing content (11) |
| **Categories** | Different news categories (12) |

### **🏷️ Category Filter Tags**
Click any category to filter articles:

- **All** - Show all articles (default)
- **news** (24) - General news articles
- **wirtschaft** (22) - Business and economy
- **zurich** (13) - Zurich local news
- **tech** (11) - Technology news
- **schweiz** (8) - Swiss national news
- **international** (8) - International news
- **crypto** (4) - Cryptocurrency news
- **bitcoin** (3) - Bitcoin-specific news
- **weather** (2) - Weather updates
- **science** (1) - Science articles
- **lifestyle** (1) - Lifestyle content
- **latest** (1) - Latest breaking news

### **🔄 Sorting Options**
Use the dropdown to sort articles:

| 🔄 Sort Option | 📝 Description |
|----------------|----------------|
| **Latest First** | Newest articles at top (default) |
| **Oldest First** | Historical articles first |
| **Priority High→Low** | P10, P9, P8 priority order |
| **Source A→Z** | Alphabetical by news source |
| **Category A→Z** | Alphabetical by category |

---

## 📰 News Table

### **📋 Table Columns**

| 📋 Column | 📝 Description | 📊 Width |
|-----------|----------------|----------|
| **Title** | Article headline (clickable) | 35% |
| **Category** | News category badge | 10% |
| **Source** | News source name | 10% |
| **Priority** | P10-P6 priority badge | 8% |
| **Weight** | Article weight value | 8% |
| **Age** | Hours since publication | 8% |
| **Links** | Article + RSS feed links | 21% |

### **🔗 Link System**
Each article row contains two links:

- **📰 Article** - Direct link to the news article (blue)
- **📡 RSS Feed** - Direct link to the RSS feed (orange)

Both links open in new tabs with security attributes.

### **🎨 Visual Elements**

#### **🏷️ Badges**
- **Category Badge** - Blue background with white text
- **Source Badge** - Gray background with white text  
- **Priority Badge** - Green background with white text
- **Time Badge** - Gray background showing age in hours

#### **🎨 Color Scheme**
- **Primary Blue** - #3498db (links, categories)
- **Dark Gray** - #2c3e50 (text, headers)
- **Orange** - #e67e22 (RSS feed links)
- **Light Gray** - #f5f7fa (background)

---

## 📡 RSS Sources Table

### **📊 Source Overview**
The second table shows all RSS sources:

| 📋 Column | 📝 Description |
|-----------|----------------|
| **Source** | News source name |
| **Priority** | P10-P6 priority level |
| **Weight** | Source weight value |
| **Categories** | All categories from this source |
| **Actions** | Direct RSS feed link |

### **🏢 Current Active Sources**

| 📰 Source | 🎯 Priority | ⚖️ Weight | 📂 Categories |
|-----------|-------------|-----------|---------------|
| **nzz** | P10 | 3.0 | zurich, schweiz, wirtschaft, international |
| **20min** | P10 | 0.8 | weather, zurich, schweiz, wirtschaft, crypto, science, tech, lifestyle |
| **heise** | P9 | 1.5 | news, tech |
| **srf** | P9 | 2.0 | news, schweiz, international, wirtschaft |
| **tagesanzeiger** | P8 | 3.0 | zurich, schweiz, wirtschaft |
| **cointelegraph** | P8 | 2.0 | bitcoin, crypto |
| **cash** | P7 | 1.5 | wirtschaft |
| **techcrunch** | P7 | 1.3 | latest |
| **bbc** | P7 | 1.5 | tech, wirtschaft, international |
| **theverge** | P6 | 1.2 | tech |
| **rt** | P6 | 1.0 | international |

---

## 🔧 Advanced Usage

### **🎯 Filtering Workflow**
1. **Start with "All"** - See complete overview
2. **Click Category** - Filter to specific topic
3. **Change Sort** - Organize by preference
4. **Click Links** - Read articles or check RSS feeds

### **📱 Mobile Usage**
The dashboard is fully responsive:
- **Tables adapt** to smaller screens
- **Touch-friendly** filter tags and buttons
- **Readable text** on all devices
- **Optimized layout** for mobile browsing

### **🔄 Refresh Data**
To get fresh data:
```bash
# Run CLI again to update dashboard
python cli_rss.py

# Dashboard automatically updates with new timestamp
```

### **⚙️ Customization Options**
```bash
# Limit CLI output (dashboard shows all articles)
python cli_rss.py --limit 5

# Custom time range
python cli_rss.py --hours 24

# Skip HTML generation
python cli_rss.py --no-html
```

---

## 🎯 Use Cases

### **📰 News Monitoring**
- **Morning Briefing** - Check latest overnight news
- **Category Focus** - Filter to specific topics of interest
- **Source Tracking** - Monitor specific news sources
- **Trend Analysis** - Sort by priority to see important stories

### **🔍 Content Research**
- **Article Discovery** - Find relevant content for radio shows
- **Source Verification** - Access original RSS feeds
- **Category Analysis** - Understand news distribution
- **Time Tracking** - See how fresh the content is

### **📊 Analytics & Insights**
- **Feed Performance** - See which sources are most active
- **Category Distribution** - Understand content balance
- **Priority Analysis** - Identify high-priority content
- **Source Diversity** - Monitor news source variety

---

## 🛠️ Troubleshooting

### **❌ Dashboard Not Generated**
```bash
# Check if CLI runs successfully
python cli_rss.py --no-html

# Verify outplay directory exists
ls -la /outplay/

# Check for errors in output
```

### **🔗 Links Not Working**
- **Article Links** - May require internet connection
- **RSS Feed Links** - Should always work if feeds are active
- **Security Warnings** - Normal for external links

### **📱 Mobile Display Issues**
- **Zoom Level** - Adjust browser zoom if text is too small
- **Orientation** - Landscape mode may work better for tables
- **Browser** - Try different mobile browsers if needed

### **🔄 Data Not Fresh**
```bash
# Force fresh data collection
python cli_rss.py --hours 6

# Check timestamp at bottom of dashboard
# Should show recent generation time
```

---

## 💡 Pro Tips

### **🚀 Efficiency Tips**
1. **Bookmark Dashboard** - Save `/outplay/rss.html` as bookmark
2. **Use Filters** - Start with categories you care about most
3. **Check Timestamps** - Look at article age for relevance
4. **Priority First** - Sort by priority for important news

### **📊 Analysis Tips**
1. **Compare Sources** - See which sources cover similar topics
2. **Track Trends** - Monitor category distribution over time
3. **Source Quality** - Higher priority sources often have better content
4. **Fresh Content** - Articles under 6 hours are usually most relevant

### **🔗 Link Management**
1. **Right-click Links** - Open in new tabs to keep dashboard open
2. **RSS Feeds** - Use RSS feed links to subscribe in your reader
3. **Article Sharing** - Copy article links for sharing
4. **Source Exploration** - Use RSS links to discover more content

---

## 📞 Support

### **🐛 Report Issues**
If you encounter problems with the dashboard:
1. Check the CLI output for errors
2. Verify internet connection for external links
3. Try regenerating with `python cli_rss.py`
4. Report persistent issues to the development team

### **💡 Feature Requests**
The dashboard is actively developed. Suggestions welcome for:
- Additional filtering options
- New sorting methods
- Enhanced mobile experience
- Integration with other services

---

<div align="center">

**🎉 You're now ready to use the RSS Dashboard like a pro!**

[🏠 Back to Documentation](../) • [📰 RSS Service](../developer-guide/services.md#-rss-service) • [🎙️ Show Generation](show-generation.md)

</div> 