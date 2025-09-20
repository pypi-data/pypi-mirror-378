

def get_stats_for_wiki(row, langname_utils):
    cols = row.find_all('td')
    if len(cols) == 0:
        return None, None

    # Col 4 contains the number of articles.
    num_articles = int(cols[4].text.replace(',', ''))

    # Col 0 contains the name of the wiki in the wiki's language;
    # often annotated with the language's ISO code
    # (rather than the wiki code!).
    # There can be multiple entries (in multiple scripts).
    lang_vals = set()
    for lang_span in cols[0].find_all(lang=True):
        lang_val = lang_span["lang"]
        # Remove the script code, if present
        lang_val = lang_val.split("-")[0]
        lang_vals.add(lang_val)
    if lang_vals:
        lang_val = lang_vals.pop()
        if len(lang_vals) > 1:
            # Doesn't happen for the Sep2025 version, but is conceivable
            # in the case of macrolanguages, in which case we should check
            # what exactly is happening and how to best process it.
            print(f"/!\\ {cols[3].text}.wikipedia.org has multiple ISO tags: {lang_vals}")
            print("Proceeding with:", lang_val)
            print("Please check wiki.py.")
        iso_code = langname_utils.toISO(lang_val, False)
        if iso_code:
            return iso_code, num_articles

    # Col 3 contains the wiki's wikicode (as used in the URL).
    # Note that the wikicode isn't necessarily a valid ISO code
    # or the correct ISO code for the wiki (but it can be!),
    # making it only a fallback in case the ISO code isn't in col 0.
    wiki_code = cols[3].text
    wiki_code_iso = langname_utils.toISO(wiki_code, False)
    if wiki_code_iso:
        return wiki_code_iso, num_articles
    return None, None


def collect(all_data, data_folder, langname_utils):
    from bs4 import BeautifulSoup
    # Add wikipedia sizes
    print('Getting wiki sizes')
    with open(data_folder + 'List_of_Wikipedias.htm') as f:
        soup = BeautifulSoup(f, features="html.parser")
        table = soup.find('table', attrs={'class': 'wikitable'})
        tbody = table.find('tbody')
        for row in tbody.find_all('tr'):
            lang, num_articles = get_stats_for_wiki(row, langname_utils)
            if lang:
                all_data[lang]['wiki_size'] = num_articles

    for lang_code in all_data:
        if 'wiki_size' not in all_data[lang_code]:
            all_data[lang_code]['wiki_size'] = 0
    return all_data


def distance_metric(lang1_size, lang2_size, key):
    if max(lang1_size, lang2_size) == 0:
        return 0.0
    return 1- min(lang1_size, lang2_size)/ max(lang1_size, lang2_size)
