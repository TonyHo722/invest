import os
import argparse
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup


def get_report_dir():
    """Resolves the date-stamped report directory (same convention as screener.py)."""
    project_root = Path(__file__).resolve().parent.parent
    today_str = datetime.now().strftime("%Y%m%d")
    return project_root / f"{today_str}_report"


def add_links_to_report(input_path, output_path):
    """
    Reads the dma_200_screen_results.html file and wraps each ticker badge in a link
    pointing to its corresponding financial data report.
    """
    print(f"Reading {input_path}...")
    if not os.path.exists(input_path):
        print(f"ERROR: Input file not found: {input_path}")
        print("Hint: Run screener.py first to generate the HTML report.")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Find all ticker badges (e.g., <span class="ticker-badge">TTD</span>)
    badges = soup.find_all('span', class_='ticker-badge')
    print(f"Found {len(badges)} ticker badges to link.")

    for badge in badges:
        ticker = badge.text.strip()
        # The folders are named after the uppercase ticker,
        # and the files are named after the lowercase ticker.
        # Example: TTD/ttd_financial_data.html
        # Determine market subfolder
        market_subfolder = "US_stock"
        if ticker.endswith('.T'):
            market_subfolder = "JP_stock"
        elif ticker.endswith('.TW') or ticker.endswith('.TWO'):
            market_subfolder = "TW_stock"
            
        # Example: US_stock/TTD/ttd_financial_data.html
        link_url = f"{market_subfolder}/{ticker}/{ticker.lower()}_financial_data.html"

        # Create a new <a> tag that opens in a new tab
        link_tag = soup.new_tag('a', href=link_url, target='_blank')
        # Add style to remove underline and make it look like a button/badge
        link_tag['style'] = 'text-decoration: none; display: inline-block;'

        # Wrap the span inside the <a> tag
        badge.wrap(link_tag)

    # Enhance the CSS with a hover effect for better interactivity
    style_tag = soup.find('style')
    if style_tag and '.ticker-badge:hover' not in style_tag.string:
        hover_css = """
        .ticker-badge {
            transition: all 0.2s ease;
            cursor: pointer;
        }
        .ticker-badge:hover {
            filter: brightness(1.2);
            transform: scale(1.05);
            box-shadow: 0 4px 12px rgba(56, 189, 248, 0.3);
        }
        """
        style_tag.append(hover_css)

    # Write the modified HTML to the output file
    print(f"Writing updated report to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(soup.prettify())

    print("Done!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add links to screener report")
    parser.add_argument('--market', choices=['us', 'tw', 'jp', 'all'], default='us', help='Market to process')
    args = parser.parse_args()

    report_dir = get_report_dir()

    # Expand 'all' into individual market keys
    markets = ['us', 'tw', 'jp'] if args.market == 'all' else [args.market]

    for market_key in markets:
        report_in  = report_dir / f"dma_200_screen_results_{market_key}.html"
        report_out = report_dir / f"dma_200_screen_result_link_{market_key}.html"
        print(f"\n--- Processing {market_key.upper()} market ---")
        add_links_to_report(str(report_in), str(report_out))

