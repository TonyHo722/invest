import os
from bs4 import BeautifulSoup

def add_links_to_report(input_path, output_path):
    """
    Reads the dma_200_screen_results.html file and wraps each ticker badge in a link 
    pointing to its corresponding financial data report.
    """
    print(f"Reading {input_path}...")
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
        link_url = f"{ticker}/{ticker.lower()}_financial_data.html"
        
        # Create a new <a> tag
        link_tag = soup.new_tag('a', href=link_url)
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
    # Define paths relative to the project root
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    report_in = os.path.join(base_dir, 'report', 'dma_200_screen_results.html')
    report_out = os.path.join(base_dir, 'report', 'dma_200_screen_result_link.html')

    add_links_to_report(report_in, report_out)
