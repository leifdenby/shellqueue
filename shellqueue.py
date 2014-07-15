DEFAULT_MANIFEST = {
        'exec': 'path/to/executable',
        'output': 'path/to/output/folder',
        }

DEFAULT_MANIFEST_STR = """

%s""" % "\n".join(["@%s: %s" for (k, v) in DEFAULT_MANIFEST.items()])

def parse_manifest(filename):
    lines = open(filename).readlines()

    option_lines = [l for l in lines if l.startswith('@')]
    options = {}

    for l in option_lines:
        option, value = l.split()
        option = option.strip('@')
        options[option] = value

    return options
