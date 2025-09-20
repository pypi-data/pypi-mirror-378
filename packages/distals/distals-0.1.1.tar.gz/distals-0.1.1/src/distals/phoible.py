import csv

def collect(all_data, data_folder, langname_utils):
    print('Reading Phoible')
    lang_data = {}
    with open(data_folder + '/phoible.csv') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        first = True
        for row in reader:
            if first:
                first = False
            iso_code = langname_utils.toISO(row[2], False)
            if iso_code is None:
                continue
            inv_id = row[0]
            glyph_id = row[5]
            # Currently ignoring:
            # - row[4], dialect
            #   often NA, sometimes implying it's a standard/protoypical variety,
            #   sometimes implying it might be a very local variety (hard to tell
            #   if the local variety exists in opposition to a widely recognized
            #   standard or not)
            # - row[7], allophone
            if iso_code not in lang_data:
                lang_data[iso_code] = {}
            if inv_id not in lang_data[iso_code]:
                lang_data[iso_code][inv_id] = set()
            lang_data[iso_code][inv_id].add(glyph_id)
    for iso_code in lang_data:
        entries = lang_data[iso_code]
        all_data[iso_code]['phoible'] = [entries[key] for key in entries]
    return all_data


def inventory_dist(inv1, inv2):
    all_glyphs = inv1.union(inv2)
    if len(all_glyphs) == 0:
        return -1
    overlap = inv1.intersection(inv2)
    return 1 - len(overlap) / len(all_glyphs)


def distance_metric(info1, info2, key):
    min_dist = None
    for inv1 in info1:
        for inv2 in info2:
            dist = inventory_dist(inv1, inv2)
            if not min_dist or dist < min_dist:
                min_dist = dist
    if min_dist:
        return min_dist
    return -1
