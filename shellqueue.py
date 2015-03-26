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
	parsed_line = l.split()
	option = parsed_line[0]
	if len(parsed_line) == 2:
	   value = parsed_line[1]
	else:
	   value = parsed_line[1:]
        option = option.strip('@')
        options[option] = value

    return options
