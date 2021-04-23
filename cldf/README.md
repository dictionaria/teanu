<a name="ds-cldfmetadatajson"> </a>

# Dictionary A dictionary of Teanu (Vanikoro, Solomon islands)

**CLDF Metadata**: [cldf-metadata.json](./cldf-metadata.json)

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF Dictionary](http://cldf.clld.org/v1.0/terms.rdf#Dictionary)
[dc:creator](http://purl.org/dc/terms/creator) | Alexandre François
[dc:identifier](http://purl.org/dc/terms/identifier) | https://dictionaria.clld.org/contributions/teanu
[dc:license](http://purl.org/dc/terms/license) | https://creativecommons.org/licenses/by/4.0/
[dcat:accessURL](http://www.w3.org/ns/dcat#accessURL) | git@github.com:dictionaria/teanu
[prov:wasDerivedFrom](http://www.w3.org/ns/prov#wasDerivedFrom) | <ol><li><a href="git@github.com:dictionaria/teanu/tree/dae15eb">git@github.com:dictionaria/teanu dae15eb</a></li><li><a href="https://github.com/glottolog/glottolog/tree/v4.3-treedb-fixes">Glottolog v4.3-treedb-fixes</a></li></ol>
[prov:wasGeneratedBy](http://www.w3.org/ns/prov#wasGeneratedBy) | <ol><li><strong>python</strong>: 3.8.5</li><li><strong>python-packages</strong>: <a href="./requirements.txt">requirements.txt</a></li></ol>
[rdf:ID](http://www.w3.org/1999/02/22-rdf-syntax-ns#ID) | teanu
[rdf:type](http://www.w3.org/1999/02/22-rdf-syntax-ns#type) | http://www.w3.org/ns/dcat#Distribution


## <a name="table-entriescsv"></a>Table [entries.csv](./entries.csv)

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF EntryTable](http://cldf.clld.org/v1.0/terms.rdf#EntryTable)
[dc:extent](http://purl.org/dc/terms/extent) | 1793


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string` | Primary key
[Language_ID](http://cldf.clld.org/v1.0/terms.rdf#languageReference) | `string` | References [languages.csv::ID](#table-languagescsv)
[Headword](http://cldf.clld.org/v1.0/terms.rdf#headword) | `string` | 
[Part_Of_Speech](http://cldf.clld.org/v1.0/terms.rdf#partOfSpeech) | `string` | 
`1st_Person_SG` | `string` | 
`3rd_Person_SG` | `string` | 
`Contains` | list of `string` (separated by ` ; `) | References [entries.csv::ID](#table-entriescsv)
`Entry_IDs` | list of `string` (separated by ` ; `) | References [entries.csv::ID](#table-entriescsv)
`Etymology` | `string` | 
`Gloss` | `string` | 
`Gloss_Bislama` | `string` | 
`Gloss_French` | `string` | 
`Heterosemes` | list of `string` (separated by ` ; `) | References [entries.csv::ID](#table-entriescsv)
`Lovono_Equivalent` | `string` | 
`Main_Entry` | list of `string` (separated by ` ; `) | References [entries.csv::ID](#table-entriescsv)
`Morphology` | `string` | 
`Orthographic_Variant` | `string` | 
`Paradigm_Form` | `string` | 
`Phonetic_Form` | `string` | 
`Plural_Form` | `string` | 
`Reduplication_Form` | `string` | 
`Tanema_Equivalent` | `string` | 
`Variant_Comment` | `string` | 
`Variant_Form` | `string` | 

## <a name="table-sensescsv"></a>Table [senses.csv](./senses.csv)

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF SenseTable](http://cldf.clld.org/v1.0/terms.rdf#SenseTable)
[dc:extent](http://purl.org/dc/terms/extent) | 2629


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string` | Primary key
[Description](http://cldf.clld.org/v1.0/terms.rdf#description) | `string` | 
[Entry_ID](http://cldf.clld.org/v1.0/terms.rdf#entryReference) | `string` | References [entries.csv::ID](#table-entriescsv)
`Antonym` | list of `string` (separated by ` ; `) | References [entries.csv::ID](#table-entriescsv)
`Bibliographical_Reference` | `string` | 
`Contenu_Tableau` | `string` | 
`Contracted_To` | list of `string` (separated by ` ; `) | References [entries.csv::ID](#table-entriescsv)
`Encyclopedic_Info` | `string` | 
`Etymology_Comment` | `string` | 
`Etymology_Source` | `string` | 
`Explanation` | list of `string` (separated by ` ; `) | References [entries.csv::ID](#table-entriescsv)
`Infobox` | `string` | 
`Infobox_Teanu` | `string` | 
`Lexical_Function_Gloss` | `string` | 
`Link` | `string` | 
`Literally` | `string` | 
`Media_IDs` | list of `string` (separated by ` ; `) | References [media.csv::ID](#table-mediacsv)
`Plural_Form` | list of `string` (separated by ` ; `) | References [entries.csv::ID](#table-entriescsv)
`Possessive_Classifier` | list of `string` (separated by ` ; `) | References [entries.csv::ID](#table-entriescsv)
`Scientific_Name` | `string` | 
`See_Lexical_List` | list of `string` (separated by ` ; `) | References [entries.csv::ID](#table-entriescsv)
`Semantic_Domain` | `string` | 
`Sense_Comment` | `string` | 
`Singular_Form` | list of `string` (separated by ` ; `) | References [entries.csv::ID](#table-entriescsv)
[Source](http://cldf.clld.org/v1.0/terms.rdf#source) | list of `string` (separated by `;`) | 
`Synonym` | list of `string` (separated by ` ; `) | References [entries.csv::ID](#table-entriescsv)
`Syntactic_Restriction` | `string` | 
`Typical_Subject` | `string` | 
`alt_translation1` | `string` | 

## <a name="table-examplescsv"></a>Table [examples.csv](./examples.csv)

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF ExampleTable](http://cldf.clld.org/v1.0/terms.rdf#ExampleTable)
[dc:extent](http://purl.org/dc/terms/extent) | 2989


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string` | Primary key
[Language_ID](http://cldf.clld.org/v1.0/terms.rdf#languageReference) | `string` | References [languages.csv::ID](#table-languagescsv)
[Primary_Text](http://cldf.clld.org/v1.0/terms.rdf#primaryText) | `string` | 
[Analyzed_Word](http://cldf.clld.org/v1.0/terms.rdf#analyzedWord) | list of `string` (separated by `\t`) | 
[Gloss](http://cldf.clld.org/v1.0/terms.rdf#gloss) | list of `string` (separated by `\t`) | 
[Translated_Text](http://cldf.clld.org/v1.0/terms.rdf#translatedText) | `string` | 
[Meta_Language_ID](http://cldf.clld.org/v1.0/terms.rdf#metaLanguageReference) | `string` | References [languages.csv::ID](#table-languagescsv)
[Comment](http://cldf.clld.org/v1.0/terms.rdf#comment) | `string` | 
`Corpus_Reference` | `string` | 
`Example_Comment_English` | `string` | 
`Example_URL` | `string` | 
`Sense_IDs` | list of `string` (separated by ` ; `) | References [senses.csv::ID](#table-sensescsv)
`alt_translation1` | `string` | 

## <a name="table-mediacsv"></a>Table [media.csv](./media.csv)

property | value
 --- | ---
[dc:extent](http://purl.org/dc/terms/extent) | 108


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string` | Primary key
[Language_ID](http://cldf.clld.org/v1.0/terms.rdf#languageReference) | `string` | References [languages.csv::ID](#table-languagescsv)
`Filename` | `string` | 
`URL` | `anyURI` | 
`mimetype` | `string` | 
`size` | `integer` | 
[Description](http://cldf.clld.org/v1.0/terms.rdf#description) | `string` | 

## <a name="table-languagescsv"></a>Table [languages.csv](./languages.csv)

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF LanguageTable](http://cldf.clld.org/v1.0/terms.rdf#LanguageTable)
[dc:extent](http://purl.org/dc/terms/extent) | 1


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string` | Primary key
[Name](http://cldf.clld.org/v1.0/terms.rdf#name) | `string` | 
[Macroarea](http://cldf.clld.org/v1.0/terms.rdf#macroarea) | `string` | 
[Latitude](http://cldf.clld.org/v1.0/terms.rdf#latitude) | `decimal` | 
[Longitude](http://cldf.clld.org/v1.0/terms.rdf#longitude) | `decimal` | 
[Glottocode](http://cldf.clld.org/v1.0/terms.rdf#glottocode) | `string` | 
[ISO639P3code](http://cldf.clld.org/v1.0/terms.rdf#iso639P3code) | `string` | 

