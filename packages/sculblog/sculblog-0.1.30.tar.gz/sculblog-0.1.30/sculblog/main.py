import sqlite3
import os
from bs4 import BeautifulSoup
from datetime import datetime
import markdown
import pypandoc
import re
import importlib.resources as resources
from contextlib import contextmanager
import sys
import traceback

from sculblog.diego_flavored_markdown import count_markdown_words
from sculblog.db import DbConn

#===============================
# Configuration and Utilities
#===============================

db_path = os.path.abspath(os.path.join('/', 'var', 'www', 'html', 'database', 'db.db'))
draft_db_path = os.path.abspath(os.path.join('/', 'var', 'www', 'html', 'database', 'drafts.db')) # the variable does not have an s. the filename does

input_header_message = "what is the header of the page? "

def sanitize_filename(filename: str) -> str:
    return re.sub(r'[^\w\-_\. ]', '_', filename)

def remove_extension(filename):
    return os.path.splitext(filename)[0]

def custom_date():
    now = datetime.now()
    year, day, month_abbr = now.year, now.day, now.strftime('%b')
    month = 'July' if month_abbr == 'Jul' else month_abbr
    return f"{year} {month} {day:02d}"

lua_filter = str(resources.files('sculblog') / 'subsection-wrapper.lua')

#===============================
# HTML and Content Management
#===============================


def write_page_html(file_path: str):
    try:
        html = pypandoc.convert_file(
            file_path,
            to='html',
            format='markdown+fenced_divs-markdown_in_html_blocks',
            extra_args=['--mathml', f'--lua-filter={lua_filter}']
        )
    except Exception as e:
        print(f"Error in write_page_html: {str(e)}")
        raise
    return html

def write_preview_html(html_content: str, char_len: int):
    try:
        # Parse HTML content
        soup = BeautifulSoup(html_content, 'html.parser')
        
        for s_tag in soup.find_all(['style', 'iframe']):
            s_tag.replace_with("")

        # Convert link tags to spans
        for a_tag in soup.find_all('a'):
            span_tag = soup.new_tag('span', **{'class': 'false-external-link'})
            span_tag.string = a_tag.get_text()
            a_tag.replace_with(span_tag)
        
        # Convert header tags to spans
        for h_tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            span_tag = soup.new_tag('span', **{'class': 'preview-header'})
            span_tag.string = h_tag.get_text()
            h_tag.replace_with(span_tag)
        
        # Unwrap any tags that aren't standard text formatting elements
        for tag in soup.find_all():
            if tag.name not in ['span', 'sup', 'sub', 'em', 'strong', 'i', 'b',
                                's', 'strike', 'del',  # Strikethrough variations
                                'u',                   # Underline
                                'mark',                # Highlight/marking
                                'small',               # Smaller text
                                'q', 'cite',           # Quotations
                                'code', 'kbd',         # Code and keyboard input
                                'abbr',                # Abbreviations
                            ]:           
                tag.unwrap()
        
        # Get all text content to check length
        text_content = soup.get_text()
        
        # If text is longer than char_len, truncate
        if len(text_content) > char_len:
            # Find all text nodes and accumulate up to char_len
            text_nodes = []
            current_count = 0
            
            for element in soup.descendants:
                if isinstance(element, str) and current_count < char_len:
                    if current_count + len(element) <= char_len:
                        text_nodes.append((element, element))
                        current_count += len(element)
                    else:
                        # Truncate this text node
                        truncated = element[:char_len - current_count] + "..."
                        text_nodes.append((element, truncated))
                        current_count = char_len
                        break
            
            # Replace text nodes with truncated versions
            for original, truncated in text_nodes:
                if original != truncated:
                    original.replace_with(truncated)
        
        # Get final HTML with all tags properly closed
        clean_html = ''.join(str(tag) for tag in soup.contents)
        return clean_html
        
    except Exception as e:
        print(f"Error in write_preview_html: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
        raise

#===============================
# Main Functions
#===============================

def post_updater(category, file_path, subcommand): 
        try:

            draft_db = DbConn(draft_db_path)
            db = DbConn(db_path)

            page_html = write_page_html(file_path)
            file_name = os.path.splitext(file_path)[0]

            with open(os.path.abspath(file_path), "r") as file: # this is to get word count
                markdown_content = file.read()

            post_data = {
                "text": page_html,
                "preview_html": write_preview_html(page_html, 1500),
                "word_count": count_markdown_words(markdown_content), 
            }
            
            # if it's not in there yet
            if not db.value_in_column(category, "file_name", file_name): 

                post_data["header"] = input(input_header_message)
                post_data["file_name"] = file_name
                post_data["date_splash"] = custom_date()
                
                # draft 0 is for preview. everything else is for regular drafts

                post_data["draft"] = 1
                if db.insert_row(category, post_data):
                    pass
                else:
                    raise Exception("Failed to insert data.")

                for x in [0,1]:
                    draft_data = post_data.copy()
                    draft_data["draft"] = x
                    if draft_db.insert_row(category, draft_data): # this was post_data
                        pass
                    else:
                        raise Exception("Failed to insert data.")

                    print(f"Successfully inserted data for post {file_name}")    

            # here it is in there already 
            else:
                # db.update_row(category, "file_name", file_name, post_data)
                values = list(post_data.values()) + [file_name]

                # if it is draft, then it makes a copy and increments the draft counter. if it is preview, then it just updates the where draft is zero
                if subcommand == "draft": 

                    set_clause = ", ".join([f"{col} = ?" for col in post_data.keys()])
                    where_clause = f"WHERE file_name = ? AND draft = (SELECT MAX(draft) FROM {category} WHERE file_name = ?)"
                    draft_columns = ', '.join(post_data.keys()) + ', file_name, draft'
                    placeholders = ', '.join(['?'] * len(post_data))
                    subquery_draft = f"(SELECT COALESCE(MAX(draft), 0) + 1 FROM {category} WHERE file_name = ?)"
                    draft_values = list(post_data.values()) + [file_name, file_name, file_name, file_name]

                    draft_query = f"""
                        INSERT INTO {category} ({draft_columns})
                        SELECT {placeholders}, ?, {subquery_draft}
                        FROM {category}
                        {where_clause}
                        LIMIT 1
                    """

                    draft_db.execute_query(draft_query, draft_values)
                    columns = ', '.join([f"{key} = ?" for key in post_data.keys()])

                    query = f"""
                        UPDATE {category}
                        SET draft = draft + 1, {columns}
                        WHERE file_name = ?
                    """
                    
                    db.execute_query(query, values)

                elif subcommand == "update":
                    
                    long_values = list(post_data.values()) + [file_name, file_name]
                    set_clause = ", ".join([f"{col} = ?" for col in post_data.keys() if col != "date_splash"])
                    where_clause = f" file_name = ? AND draft = (SELECT MAX(draft) FROM {category} WHERE file_name = ?)"
                    query = F"UPDATE {category} SET {set_clause} WHERE {where_clause}"

                    alt_where_clause = f" file_name = ? AND draft = 0"
                    alt_query = F"UPDATE {category} SET {set_clause} WHERE {alt_where_clause}"

                    draft_db.execute_query(alt_query, values)
                    draft_db.execute_query(query, long_values)
                    db.execute_query(query, long_values)

                elif subcommand == "preview":
                    
                    set_clause = ", ".join([f"{col} = ?" for col in post_data.keys()])
                    where_clause = "file_name = ? AND draft = 0"

                    query = f"""
                        UPDATE {category}
                        SET {set_clause}
                        WHERE {where_clause} 
                    """

                    draft_db.execute_query(query, values)

                else:
                    print(f"something is very wrong with subcommand {subcommand}")
                
        except Exception as e:
            print(f"An error of Exception type {type(e).__name__} occurred: {e}")   

def db_single_updater(func):
    def wrapper(category, file_path, *args, **kwargs):
        file_name = remove_extension(file_path)
        field, value = func(*args, **kwargs)
        DbConn(db_path).update_row(category, "file_name", file_name, {field: value})
    return wrapper

@db_single_updater
def hide():
    return "hide", "0"

@db_single_updater
def unhide():
    return "hide", ""

@db_single_updater
def date():
    date_splash = input("What is the date of the page? ")
    return "date_splash", date_splash

@db_single_updater
def header():
    header = input(input_header_message)
    return "header", header

def main():
    if len(sys.argv) < 4:
        print("Usage: sculblog <command> <category> <postname> \n\t  commands: preview, draft, hide, unhide, date, header")
        sys.exit(1)
        
    command, category, file_path = sys.argv[1], sys.argv[2], sys.argv[3]
    
    if command == "preview":
        post_updater(category, file_path, "preview")
    elif command == "draft":
        post_updater(category, file_path, "draft")
    elif command == "update":
        post_updater(category, file_path, "update")

    elif command == "hide":
        hide(category, file_path)
    elif command == "unhide":
        unhide(category, file_path)

    elif command == "date":
        date(category, file_path)
    elif command == "header":
        header(category, file_path)

    else:
        print('Invalid command. Command must be "preview", "draft", "hide", "unhide", "date", or "header"')
        sys.exit(1)

if __name__ == "__main__":
    main()
