# Adapted script to convert Gutenberg KJV Luke to OpBible .txs format
# Handles multi-line verses by concatenating continuation lines

input_file = 'luke_kjv.txt'  # Your downloaded file
output_file = 'KJV-Luk.txs'      # Output for OpBible (book abbreviation 'Luk' for Luke)

with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
    current_verse = None
    current_text = []
    in_content = False  # Flag to skip header until first verse

    for line in infile:
        line = line.strip()
        
        if line.startswith('42:'):  # Start of a new verse
            # Write previous verse if exists
            if current_verse:
                full_text = ' '.join(current_text).strip()
                outfile.write(f'#{current_verse} {full_text}\n')
            
            # Parse new verse
            parts = line.split(' ', 1)
            if len(parts) >= 2:
                prefix, text = parts
                _, chapter, verse = prefix.split(':')
                chapter = str(int(chapter))  # Unpad
                verse = str(int(verse))      # Unpad
                current_verse = f'{chapter}:{verse}'
                current_text = [text.strip()]
                in_content = True  # Started processing content
        
        elif in_content and line:  # Continuation line of current verse
            # Append, removing leading spaces or artifacts
            current_text.append(line.strip())
        
        # Stop if reaching footer (optional, but helps if file has extra)
        if '*** END OF THE PROJECT GUTENBERG EBOOK' in line:
            break

    # Write the last verse
    if current_verse:
        full_text = ' '.join(current_text).strip()
        outfile.write(f'#{current_verse} {full_text}\n')

print(f'Conversion complete. Output saved to {output_file}')
