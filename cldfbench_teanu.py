from collections import ChainMap, defaultdict
from itertools import chain
import pathlib
import re

from cldfbench import Dataset as BaseDataset, CLDFSpec

from pybtex.database import parse_string
from pydictionaria.sfm_lib import Database as SFM
from pydictionaria.preprocess_lib import marker_fallback_sense, merge_markers
from pydictionaria import sfm2cldf


CROSSREF_BLACKLIST = {'xv', 'lg'}
CROSSREF_MARKERS = {'cf', 'mn', 'sy', 'an', 'cont', 'lv'}


def _unhtml(pair):
    marker, value = pair
    if marker == 'mr':
        return marker, re.sub(r'<compo>([^<]+)</compo>', r'|fv{\1}', value)
    else:
        return pair


def unhtml_mr(entry):
    if entry.get('mr'):
        return entry.__class__(map(_unhtml, entry))
    else:
        return entry


def prepreprocess(entry):
    entry = unhtml_mr(entry)
    return entry


class MySFM(SFM):
    def __init__(self, entries):
        self.extend(entries)


class EntrySplitter:

    def __init__(self):
        self._homonyms = defaultdict(int)
        self.id_map = {}
        self.la_index = {}

    def _split_groups(self, entry):
        groups = [entry.__class__()]
        for marker, value in entry:
            if marker == 'gp':
                groups.append(entry.__class__())
            groups[-1].append((marker, value))
        return groups[0], groups[1:]

    def _split_senses(self, entry):
        if not entry:
            return []
        senses = [entry.__class__()]
        for marker, value in entry:
            if marker == 'sn':
                senses.append(entry.__class__())
            senses[-1].append((marker, value))
        return senses

    def _extract_subentries(self, entry):
        main_entry = entry.__class__()
        subentries = []
        senses = self._split_senses(entry)
        for sense in senses:
            sense_subentries = []
            for marker, value in sense:
                if marker == 'se':
                    sense_subentries.append(entry.__class__())
                if sense_subentries:
                    sense_subentries[-1].append((marker, value))
                else:
                    main_entry.append((marker, value))
            subentries.extend(sense_subentries)
        return main_entry, subentries

    def _generate_subentry(self, subentry, parent_id, ps):
        lx = subentry.get('se')
        hm = subentry.get('hm') or ''
        old_id = '{}_{}'.format(lx, hm) if hm else lx

        self._homonyms[lx] += 1
        new_hm = str(self._homonyms[lx])
        new_id = '{}{}'.format(lx, new_hm)
        self.id_map[old_id] = new_id

        new_entry = subentry.__class__()
        new_entry.append(('lx', lx))
        new_entry.append(('hm', new_hm))
        new_entry.append(('cont', parent_id))
        # Some subentries override the part of speech of the entry
        if ps and not subentry.get('ps'):
            new_entry.append(('ps', ps))
        new_entry.extend((m, v) for m, v in subentry if m not in ('se', 'hm'))

        return new_entry

    def split_entry(self, entry):
        lx = entry.get('lx')
        la = entry.get('la')
        hm = entry.get('hm') or ''
        citation_form = la or lx
        old_id = '{}_{}'.format(citation_form, hm) if hm else citation_form
        ps = entry.get('ps')

        main_entry, groups = self._split_groups(entry)

        if groups:
            new_entries = []
            subentries = []

            for group in groups:
                group_entries = self._split_groups(group)
                gp = group.get('gp') or ''
                old_gid = '{}.{}'.format(old_id, gp) if gp else old_id

                self._homonyms[lx] += 1
                new_hm = str(self._homonyms[lx])
                new_id = '{}{}'.format(lx, new_hm)
                self.id_map[old_gid] = new_id
                if la:
                    if la not in self.la_index:
                        self.la_index[la] = new_id
                    la_gid = '{}.{}'.format(la, gp) if gp else la
                    if la_gid not in self.la_index:
                        self.la_index[la_gid] = new_id

                group_entry, group_subentries = self._extract_subentries(group)
                group_ps = group_entry.get('ps')

                new_entry = entry.__class__(
                    (m, v) for m, v in main_entry if m not in ('hm', 'ps'))
                new_entry.append(('hm', new_hm))
                # Some groups override the part of speech of the entry
                if ps and not group_ps:
                    new_entry.append(('ps', ps))
                new_entry.extend(
                    (m, v) for m, v in group_entry if m != 'gp')

                new_entries.append(new_entry)
                subentries.extend(
                    self._generate_subentry(subentry, old_gid, group_ps or ps)
                    for subentry in group_subentries)

            if len(new_entries) > 1:
                for entry in new_entries:
                    heterosemes = [
                        '{}{}'.format(e.get('lx'), e.get('hm'))
                        for e in new_entries
                        if e is not entry]
                    entry.append(('heterosemes', ' ; '.join(heterosemes)))

            for e in new_entries:
                yield e
            for e in subentries:
                yield e
        else:
            main_entry, subentries = self._extract_subentries(main_entry)

            self._homonyms[lx] += 1
            new_hm = str(self._homonyms[lx])
            new_id = '{}{}'.format(lx, new_hm)
            self.id_map[old_id] = new_id
            if la and la not in self.la_index:
                self.la_index[la] = new_id

            new_entry = entry.__class__(
                (m, v) for m, v in main_entry if m != 'hm')
            new_entry.insert(1, ('hm', new_hm))

            yield new_entry
            for subentry in subentries:
                yield self._generate_subentry(subentry, old_id, ps)


def _fix_single_ref(ref, id_map):
    # Shave off sense numbers
    ref = re.sub(r'–\d+$', '', ref.strip())
    return (
        id_map.get(ref)
        or id_map.get('{}_1'.format(ref))
        or id_map.get('{}.A'.format(ref))
        or id_map.get('{}_1.A'.format(ref))
        or ref)


def _fix_crossref_field(value, id_map):
    return ';'.join(_fix_single_ref(v, id_map) for v in value.split(';'))


def fix_crossrefs(entry, id_map):
    def fix_inline_crossref(match):
        new_link = _fix_crossref_field(
            '{}{}'.format(match.group(2), match.group(3) or ''),
            id_map)
        return '|{}{{{}}}'.format(match.group(1), new_link)

    new_entry = entry.__class__()
    for marker, value in entry:
        if marker in CROSSREF_MARKERS:
            value = _fix_crossref_field(value, id_map)
        elif marker not in CROSSREF_BLACKLIST:
            value = re.sub(
                r'\|(fv|vl)\{([^}]+)\}(?:\|hm\{(\d+)\})?',
                fix_inline_crossref,
                value)
        new_entry.append((marker, value))
    return new_entry


def reorganize(sfm):
    """Use this function if you need to manually add or remove entrys from the
    SFM data.

    Takes an SFM database as an argument and returns a modified SFM database.
    """
    splitter = EntrySplitter()
    sfm = MySFM(
        new_entry
        for old_entry in sfm
        for new_entry in splitter.split_entry(old_entry))
    sfm.visit(lambda e: fix_crossrefs(e, ChainMap(splitter.id_map, splitter.la_index)))
    return sfm


def _convert_before_sn(mapping, entry):
    found_sn = False
    for m, v in entry:
        if found_sn:
            yield m, v
        elif m == 'sn':
            found_sn = True
            yield m, v
        else:
            yield mapping.get(m, m), v


def convert_before_sn(mapping, entry):
    if entry.get('sn'):
        return entry.__class__(_convert_before_sn(mapping, entry))
    else:
        return entry


def remove_markers(markers, entry):
    return entry.__class__(
        (m, v)
        for m, v in entry
        if m not in markers)


def move_images_into_sense(entry):
    """Sometimes there are \pc tags in the entry -- move those to the first sense."""
    if not entry.get('sn') or not entry.get('pc'):
        return entry

    new_entry = entry.__class__()
    found_sn = None
    images = []
    for m, v in entry:
        if found_sn:
            new_entry.append((m, v))
        elif m == 'pc':
            images.append([v])
        elif m == 'lg':
            images[-1].append(v)
        elif m == 'sn':
            # jump out early if the entry did not contain any pictures
            if not images:
                return entry
            found_sn = True
            new_entry.append((m, v))
            for image in images:
                new_entry.append(('pc', image[0]))
                for lg in image[1:]:
                    new_entry.append(('lg', lg))
        else:
            new_entry.append((m, v))
    return new_entry


def _box_markers(box):
    if 'conf' in box:
        conf = '{}: {}'.format(box['tie'], box['conf']) if 'tie' in box else box['conf']
        yield 'conf', conf
    if 'cona' in box:
        cona = '{}: {}'.format(box['tin'], box['cona']) if 'tin' in box else box['cona']
        yield 'cona', cona
    if 'conv' in box:
        conv = '{}: {}'.format(box['tiv'], box['conv']) if 'tiv' in box else box['conv']
        yield 'conv', conv


def merge_infobox_titles(entry):
    box_markers = {'enc', 'tie', 'tin', 'tiv', 'conv', 'conf', 'cona'}
    box = {}
    new_entry = entry.__class__()
    for marker, value in entry:
        if marker == 'enc':
            box['enc'] = value
        elif box:
            if marker in box_markers:
                box[marker] = value
            else:
                new_entry.extend(_box_markers(box))
                box = {}
                new_entry.append((marker, value))
        else:
            new_entry.append((marker, value))
    if box:
        new_entry.extend(_box_markers(box))
    return new_entry


def merge_etymology(marker_dict):
    return '{el}{sep1}{et}{sep2}{eg}'.format(
        el=marker_dict.get('el') or '',
        sep1=': ' if marker_dict.get('el') and len(marker_dict) > 1 else '',
        et=marker_dict.get('et'),
        sep2=' ' if marker_dict.get('el') and marker_dict.get('eg') else '',
        eg="'{}'".format(marker_dict.get('eg')) if marker_dict.get('eg') else '')


def generate_link_label(entry):
    link_label = entry.get('la') or entry.get('lx') or ''
    new_entry = entry.__class__(entry)
    new_entry.insert(1, ('link_label', link_label))
    return new_entry


def preprocess(entry):
    """Use this function if you need to change the contents of an entry before
    any other processing.

    This is run on every entry in the SFM database.
    """
    entry = remove_markers(('dnu',), entry)
    entry = move_images_into_sense(entry)
    entry = marker_fallback_sense(entry, 'de', 'gn')
    entry = marker_fallback_sense(entry, 'gxx', 'ge')
    entry = marker_fallback_sense(entry, 'gxy', 'gr')
    entry = merge_infobox_titles(entry)
    entry = merge_markers(entry, ['ue', 'ee'], 'ee')
    entry = merge_markers(entry, ['un', 'en'], 'en')
    entry = merge_markers(entry, ['pdl', 'pdv'], 'pdv')
    entry = merge_markers(entry, ['el', 'et', 'eg'], 'et', format_fn=merge_etymology)
    entry = generate_link_label(entry)
    return entry


def _remove_inline_markers(val):
    if isinstance(val, str):
        return re.sub(r'\|\w+\{([^}]+)\}', r'\1', val)
    else:
        return val


def _warn_about_table(table_name, table, columns, link_regex, cldf_log):
    if not columns:
        return

    for row in table:
        row_id = row.get('ID')
        for colname, value in row.items():
            if colname not in columns:
                continue
            for link_match in re.finditer(link_regex, value):
                link = link_match.group(0)
                if re.fullmatch(r'\s*\[.*\]\s*\(.*\)\s*', link):
                    continue
                msg = '{}:{}:{}:unknown in-line cross reference `{}`'.format(
                    table_name, row.get('ID'), colname, link)
                cldf_log.warn(msg)


def warn_about_inline_references(
    entries, senses, examples, props, cldf_log
):
    props = sfm2cldf._add_property_fallbacks(props)
    if not props.get('link_regex') or not props.get('process_links_in_markers'):
        return

    _warn_about_table(
        'EntryTable',
        entries,
        {
            props['entry_map'][m]
            for m in props['process_links_in_markers']
            if m in props['entry_map']
        },
        props['link_regex'],
        cldf_log)

    _warn_about_table(
        'SenseTable',
        senses,
        {
            props['sense_map'][m]
            for m in props['process_links_in_markers']
            if m in props['sense_map']
        },
        props['link_regex'],
        cldf_log)

    _warn_about_table(
        'ExampleTable',
        examples,
        {
            props['example_map'][m]
            for m in props['process_links_in_markers']
            if m in props['example_map']
        },
        props['link_regex'],
        cldf_log)


def remove_inline_markers(val):
    if isinstance(val, list):
        return [_remove_inline_markers(v) for v in val]
    else:
        return _remove_inline_markers(val)


def clean_table(table):
    return [
        {k: remove_inline_markers(v) for k, v in row.items()}
        for row in table]


def authors_string(authors):
    """Return formatted string of all authors."""
    def is_primary(a):
        return not isinstance(a, dict) or a.get('primary', True)

    primary = ' and '.join(
        a['name'] if isinstance(a, dict) else a
        for a in authors
        if is_primary(a))
    secondary = ' and '.join(
        a['name']
        for a in authors
        if not is_primary(a))
    if primary and secondary:
        return '{} with {}'.format(primary, secondary)
    else:
        return primary or secondary


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "teanu"

    def cldf_specs(self):  # A dataset must declare all CLDF sets it creates.
        return CLDFSpec(
            dir=self.cldf_dir,
            module='Dictionary',
            metadata_fname='cldf-metadata.json')

    def cmd_download(self, args):
        """
        Download files to the raw/ directory. You can use helpers methods of `self.raw_dir`, e.g.

        >>> self.raw_dir.download(url, fname)
        """
        pass

    def cmd_makecldf(self, args):
        """
        Convert the raw data to a CLDF dataset.

        >>> args.writer.objects['LanguageTable'].append(...)
        """

        # read data

        md = self.etc_dir.read_json('md.json')
        properties = md.get('properties') or {}
        language_name = md['language']['name']
        isocode = md['language']['isocode']
        language_id = md['language']['isocode']
        glottocode = md['language']['glottocode']

        marker_map = ChainMap(
            properties.get('marker_map') or {},
            sfm2cldf.DEFAULT_MARKER_MAP)
        entry_sep = properties.get('entry_sep') or sfm2cldf.DEFAULT_ENTRY_SEP
        sfm = SFM(
            self.raw_dir / 'db.sfm',
            marker_map=marker_map,
            entry_sep=entry_sep)

        examples = sfm2cldf.load_examples(self.raw_dir / 'examples.sfm')

        if (self.raw_dir / 'sources.bib').exists():
            sources = parse_string(self.raw_dir.read('sources.bib'), 'bibtex')
        else:
            sources = None

        if (self.etc_dir / 'cdstar.json').exists():
            media_catalog = self.etc_dir.read_json('cdstar.json')
        else:
            media_catalog = {}

        # preprocessing

        sfm.visit(prepreprocess)
        sfm = reorganize(sfm)
        sfm.visit(preprocess)

        # processing

        with open(self.dir / 'cldf.log', 'w', encoding='utf-8') as log_file:
            log_name = '%s.cldf' % language_id
            cldf_log = sfm2cldf.make_log(log_name, log_file)

            entries, senses, examples, media = sfm2cldf.process_dataset(
                self.id, language_id, properties,
                sfm, examples, media_catalog=media_catalog,
                glosses_path=self.raw_dir / 'glosses.flextext',
                examples_log_path=self.dir / 'examples.log',
                glosses_log_path=self.dir / 'glosses.log',
                cldf_log=cldf_log)

            # Note: If you want to manipulate the generated CLDF tables before
            # writing them to disk, this would be a good place to do it.

            warn_about_inline_references(
                entries, senses, examples, properties, cldf_log)

            entries = clean_table(entries)
            senses = clean_table(senses)
            examples = clean_table(examples)
            media = clean_table(media)

            # cldf schema

            sfm2cldf.make_cldf_schema(
                args.writer.cldf, properties,
                entries, senses, examples, media)

            sfm2cldf.attach_column_titles(args.writer.cldf, properties)

            print(file=log_file)

            entries = sfm2cldf.ensure_required_columns(
                args.writer.cldf, 'EntryTable', entries, cldf_log)
            senses = sfm2cldf.ensure_required_columns(
                args.writer.cldf, 'SenseTable', senses, cldf_log)
            examples = sfm2cldf.ensure_required_columns(
                args.writer.cldf, 'ExampleTable', examples, cldf_log)
            media = sfm2cldf.ensure_required_columns(
                args.writer.cldf, 'media.csv', media, cldf_log)

            entries = sfm2cldf.remove_senseless_entries(
                senses, entries, cldf_log)

        # output

        if sources:
            args.writer.cldf.add_sources(sources)
        args.writer.cldf.properties['dc:creator'] = authors_string(
            md.get('authors') or ())

        language = {
            'ID': language_id,
            'Name': language_name,
            'ISO639P3code': isocode,
            'Glottocode': glottocode,
        }
        args.writer.objects['LanguageTable'] = [language]

        args.writer.objects['EntryTable'] = entries
        args.writer.objects['SenseTable'] = senses
        args.writer.objects['ExampleTable'] = examples
        args.writer.objects['media.csv'] = media
