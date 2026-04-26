#!/usr/bin/env python3
"""
Tech Digest - Daily automated tech blog summarizer
Fetches articles from RSS/web, summarizes with Claude API, sends via Gmail API.
"""

import os, json, base64, hashlib, feedparser, anthropic
from datetime import datetime, timezone, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from sources import SOURCES
from email_template import build_email_html

RECIPIENT_EMAIL = os.environ["RECIPIENT_EMAIL"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
GMAIL_CREDENTIALS_JSON = os.environ["GMAIL_CREDENTIALS_JSON"]
SEEN_ARTICLES_FILE = "seen_articles.json"
MAX_ARTICLES_PER_SOURCE = 3
MAX_TOTAL_ARTICLES = 12
HOURS_LOOKBACK = 48


def load_seen_ids():
    if os.path.exists(SEEN_ARTICLES_FILE):
        with open(SEEN_ARTICLES_FILE) as f:
            return set(json.load(f))
    return set()


def save_seen_ids(seen_ids):
    with open(SEEN_ARTICLES_FILE, "w") as f:
        json.dump(list(seen_ids), f)


def article_id(url):
    return hashlib.md5(url.encode()).hexdigest()


def fetch_articles():
    cutoff = datetime.now(timezone.utc) - timedelta(hours=HOURS_LOOKBACK)
    seen_ids = load_seen_ids()
    new_articles = []
    for source in SOURCES:
        print(f"  Fetching: {source['name']}")
        try:
            feed = feedparser.parse(source["rss"])
            count = 0
            for entry in feed.entries:
                if count >= MAX_ARTICLES_PER_SOURCE:
                    break
                url = entry.get("link", "")
                aid = article_id(url)
                if aid in seen_ids:
                    continue
                pub = entry.get("published_parsed") or entry.get("updated_parsed")
                if pub:
                    pub_dt = datetime(*pub[:6], tzinfo=timezone.utc)
                    if pub_dt < cutoff:
                        continue
                new_articles.append({
                    "source": source["name"],
                    "source_color": source["color"],
                    "source_tag": source.get("tag", "Tech"),
                    "title": entry.get("title", "No title"),
                    "url": url,
                    "summary_raw": entry.get("summary", "")[:500],
                    "id": aid,
                })
                seen_ids.add(aid)
                count += 1
        except Exception as e:
            print(f"  Warning: Error fetching {source['name']}: {e}")
    save_seen_ids(seen_ids)
    return new_articles[:MAX_TOTAL_ARTICLES]


def summarize_articles(articles):
    if not articles:
        return [], [], [], ""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    article_list = "\n\n".join([
        f"[{i+1}] SOURCE: {a['source']}\nTITLE: {a['title']}\nURL: {a['url']}\nSNIPPET: {a['summary_raw']}"
        for i, a in enumerate(articles)
    ])
    prompt = f"""You are a tech editor preparing a daily digest for a Korean developer learning English.
Today is {datetime.now().strftime('%B %d, %Y')}.

Articles:
{article_list}

For EACH article provide JSON with: id, title_ko, title_en, summary_ko (3 sentences), summary_en (3 sentences), vocab (3 items as "term: Korean explanation"), tag (AI/ML|Infrastructure|Security|Research|Engineering|DevOps|Business).
Then provide trends_ko (3 items), trends_en (3 items), learning_tip.

Respond ONLY with valid JSON:
{{"articles": [...], "trends_ko": [...], "trends_en": [...], "learning_tip": "..."}}"""

    print("  Calling Claude API...")
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    result = json.loads(raw.strip())
    summary_map = {str(s["id"]): s for s in result["articles"]}
    for i, article in enumerate(articles):
        s = summary_map.get(str(i + 1), {})
        article.update({
            "title_ko": s.get("title_ko", article["title"]),
            "title_en": s.get("title_en", article["title"]),
            "summary_ko": s.get("summary_ko", ""),
            "summary_en": s.get("summary_en", ""),
            "vocab": s.get("vocab", []),
            "tag": s.get("tag", article["source_tag"]),
        })
    return articles, result.get("trends_ko", []), result.get("trends_en", []), result.get("learning_tip", "")


def get_gmail_service():
    creds_data = json.loads(GMAIL_CREDENTIALS_JSON)
    creds = Credentials(
        token=creds_data["token"],
        refresh_token=creds_data["refresh_token"],
        token_uri=creds_data["token_uri"],
        client_id=creds_data["client_id"],
        client_secret=creds_data["client_secret"],
        scopes=creds_data["scopes"],
    )
    return build("gmail", "v1", credentials=creds)


def send_email(service, subject, html_body, to=RECIPIENT_EMAIL):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["To"] = to
    msg["From"] = to
    msg.attach(MIMEText(html_body, "html"))
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": raw}).execute()
    print(f"  Sent: {subject}")


def main():
    today = datetime.now().strftime("%Y년 %m월 %d일")
    today_en = datetime.now().strftime("%B %d, %Y")
    print("Step 1: Fetching articles...")
    articles = fetch_articles()
    print(f"  Found {len(articles)} new articles")
    if not articles:
        print("  No new articles. Skipping.")
        return
    print("Step 2: Summarizing with Claude...")
    articles, trends_ko, trends_en, learning_tip = summarize_articles(articles)
    print("Step 3: Sending emails...")
    service = get_gmail_service()
    html_ko = build_email_html(lang="ko", date_str=today, articles=articles, trends=trends_ko, learning_tip=learning_tip)
    send_email(service, f"테크 다이제스트 | {today}", html_ko)
    html_en = build_email_html(lang="en", date_str=today_en, articles=articles, trends=trends_en, learning_tip=learning_tip)
    send_email(service, f"Tech Digest | {today_en}", html_en)
    print("Done!")


if __name__ == "__main__":
    main()
