import os
import fnmatch
from datetime import datetime
from pathlib import Path

exclude_patterns = {"node_modules", ".git", "src", "scripts"}
exclude_file_patterns = [
    "*.js",
    "*.py",
    "*.lock",
    "*.html",
    "package.json",
    "tree.json",
]


def get_file_info(directory_path, item):
    """Retrieves last modified time and formatted size of a file."""
    item_path = os.path.join(directory_path, item)
    modified_time_timestamp = os.path.getmtime(item_path)
    modified_time_utc = (
        datetime.utcfromtimestamp(modified_time_timestamp).isoformat() + ".000Z"
    )
    size_bytes = os.path.getsize(item_path)
    formatted_size = format_size(size_bytes)
    return modified_time_utc, formatted_size


def format_size(size_bytes):
    """Auto formats bytes to B, KB, MB, or GB with appropriate precision."""
    if size_bytes < 100:
        return f"{size_bytes} B"
    elif size_bytes < 1024:
        return f"{size_bytes / 1024:.1f} kB"
    elif size_bytes < 100 * 1024:
        return f"{size_bytes / 1024:.0f} kB"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    elif size_bytes < 100 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.0f} MB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.0f} GB"


# def format_size(size_bytes):
#     """Auto formats bytes to KB, MB, or GB."""
#     if size_bytes < 1024:
#         return f"{size_bytes} B"
#     elif size_bytes < 1024 * 1024:
#         return f"{size_bytes / 1024:.1f} kB"
#     elif size_bytes < 1024 * 1024 * 1024:
#         return f"{size_bytes / (1024 * 1024):.1f} MB"
#     else:
#         return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def should_exclude(item):
    """Checks if an item (file or directory) should be excluded."""
    return (
        item in exclude_patterns
        or item.startswith(".")
        or any(fnmatch.fnmatch(item, pattern) for pattern in exclude_file_patterns)
    )


def generate_directory_html(directory_path, output_path):
    items_with_info = []
    for item in os.listdir(directory_path):
        if not should_exclude(item):
            item_path = os.path.join(directory_path, item)
            modified_time = (
                datetime.utcfromtimestamp(os.path.getmtime(item_path)).isoformat()
                + ".000Z"
            )
            if os.path.isfile(item_path):
                modified_time, size = get_file_info(directory_path, item)
                items_with_info.append(
                    {
                        "name": item,
                        "type": "file",
                        "modified": modified_time,
                        "size": size,
                    }
                )
            elif os.path.isdir(item_path):
                items_with_info.append(
                    {"name": item, "type": "dir", "modified": modified_time, "size": ""}
                )

    # Sort items: directories first, then files by modified time (newest first)
    # sorted_items = sorted(
    #     items_with_info,
    #     key=lambda x: (x["type"] == "file", x["modified"]),
    #     reverse=True,
    # )
    # sorted_items = sorted(
    #     items_with_info,
    #     key=lambda x: (x["type"] == "file", x["modified"]),
    #     reverse=True,
    # )

    def base_name(file_name):
        if file_name.endswith(".meta.json"):
            return file_name[:-10]  # remove ".meta.json"
        elif file_name.endswith(".a7p"):
            return file_name[:-4]  # remove ".a7p"
        else:
            return file_name

    def sort_key(item):
        # Directories come first (False < True)
        is_file = item["type"] == "file"
        name = item["name"]
        return (
            is_file,                        # dirs first (False), files after (True)
            base_name(name).lower(),       # group by common base name
            0 if name.endswith(".a7p") else 1  # .a7p before .meta.json
        )
    
    sorted_items = sorted(items_with_info, key=sort_key)


    html_content = f"""<!DOCTYPE html>
    <html>
    <head>
        <a>
        <title>Index of: {os.path.relpath(directory_path, '.')}</title>
        <style>
            body {{ font-family: monospace; }}
            h1 {{ margin-bottom: 1em; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ text-align: left; white-space: nowrap; }}  /* padding: 0.5em; */
            th {{  }}  /* border-bottom: 2px solid #000; */
            td {{ border-bottom: 1px dotted #ccc; }}
            .back-link {{ display: block; margin-bottom: 1em; }}
            .time-col {{ width: 20em; }}
            .size-col {{ width: 10em; }}
        </style>
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                const fullUrlContainer = document.createElement('p');
                fullUrlContainer.id = 'full-url';
                const fullUrlLink = document.createElement('a');
                fullUrlLink.href = window.location.href;
                fullUrlLink.textContent = window.location.href;
                fullUrlContainer.appendChild(document.createTextNode('Full URL: '));
                fullUrlContainer.appendChild(fullUrlLink);
                const h1Element = document.querySelector('h1');
                h1Element.parentNode.insertBefore(fullUrlContainer, h1Element);
            }});
        </script>
    </head>
    <body>
        <h1>Index of: {Path(os.path.relpath(directory_path, '.')).as_posix()}</h1>
        <table>
            <thead>
                <tr>
                    <th class="time-col">Last Modified</th>
                    <th class="size-col">Size</th>
                    <th>Key</th>
                </tr>
                <tr>
                    <th colspan="3"><hr></th>
                </tr>
            </thead>
            <tbody>
                """

    # Add back link if not at the root
    relative_path = os.path.relpath(directory_path, ".")
    if relative_path != ".":
        html_content += f'<tr><td></td><td></td><td><a class="back-link" href="../">../</a></td></tr>\n'

    for item_info in sorted_items:
        name = item_info["name"]
        modified = item_info["modified"]
        size = item_info["size"]

        if item_info["type"] == "dir":
            html_content += f'<tr><td>{modified}</td><td></td><td><a href="{name}/">{name}/</a></td></tr>\n'
        else:
            html_content += f'<tr><td>{modified}</td><td>{size}</td><td><a href="{name}">{name}</a></td></tr>\n'

    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """

    output_file_path = os.path.join(output_path, relative_path, "index.html")
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    with open(output_file_path, "w") as f:
        f.write(html_content)


def generate_static_site(root_dir, output_dir):
    for root, dirs, files in os.walk(root_dir):
        # Filter directories in place to prevent os.walk from descending into excluded ones
        dirs[:] = [d for d in dirs if not should_exclude(d)]

        # Generate HTML for the current directory
        generate_directory_html(root, output_dir)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)

    args = parser.parse_args()

    source_directory = args.path  # Your project root
    output_directory = args.path  # The directory to generate the static site

    generate_static_site(source_directory, output_directory)
    print(f"Static file tree generated in the '{output_directory}' directory.")
