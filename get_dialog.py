import argparse
import csv
import datetime
import logging
import os
import re

def is_dialog(line, dash_chars):
	# print('line: {}; dash_chars: {}'.format(line, dash_chars))
	return line[0] in dash_chars

def is_direct_speech(line):
	dialog_part = re.search("(-[ ].+-|-.+-|—[ ].+—|—.+—|–[ ].+–|–.+–)", line)
	if dialog_part:
#		print("{}".format(dialog_part.group(0)))
		return dialog_part.group(0)
	else:
		return line


def extract_dialog_from_txt(src_directory, src_txt_file, dst_directory, dash_chars):
	src_file_path = os.path.join(src_directory, src_txt_file)
	with open(src_file_path, 'r') as txt_file:
		dialog_list = []
		dialog_len = []
		for text_line in txt_file:
			# print(f'before text_line: {text_line}')
			text_line = text_line.strip()
			# print(f'after text_line: {text_line}')
			if text_line:
				if is_dialog(text_line, dash_chars):
					direct_speech = is_direct_speech(text_line)
					dialog_list += [direct_speech]
					dialog_len += [len(direct_speech)]

	dst_txt_file = src_txt_file
	dst_file_path = os.path.join(dst_directory, dst_txt_file)
	info = "Source: {}\nDestination: {}\nDialogs: {}".format(src_file_path, dst_file_path, len(dialog_list))
	logging.info(info)

	with open(dst_file_path, 'w') as txt_file:
		dialogs = '\n'.join(dialog_list)
		txt_file.write(dialogs)

	return dialog_len


def extract_dialog(src_directory, dst_directory, dash_chars):
	file_names = sorted(os.listdir(src_directory))
	if not os.path.isdir(dst_directory):
		os.mkdir(dst_directory)

	fieldnames = ["name_of_book", "number_of_replics", "mean_of_replics"]

	with open('stats.csv', 'w') as csvfile:
		writer = csv.DictWriter(csvfile, delimiter=',', fieldnames=fieldnames)
		writer.writeheader()
		for file_name in file_names:
			dialog_len = extract_dialog_from_txt(
				src_directory=src_directory,
				src_txt_file=file_name,
				dst_directory=dst_directory,
				dash_chars=dash_chars
			)
			dialog_count=len(dialog_len)
			mean = sum(dialog_len) / dialog_count if dialog_count > 0 else 0
			csv_row = {
				fieldnames[0]: file_name,
				fieldnames[1]: dialog_count,
				fieldnames[2]: mean
			}
			writer.writerow(csv_row)

def get_dash(file_path):
    try:
        with open(file_path, "r") as file:
            dash_chars = file.readline()
            info = file_path + ":\n"
    except:
        dash_chars = "-–─—"
        info = "Default dashes:\n"
    info += str({ord(dash): dash for dash in dash_chars})
    logging.info(info)
    return dash_chars

def get_args():
	parser = argparse.ArgumentParser()
	parser.add_argument(
		'src_directory',
		type=str,
		help='source directory'
	)
	parser.add_argument(
		'dst_directory',
		type=str,
		help='destination directory'
	)
	parser.add_argument(
		'--dash_file',
		type=str,
		default='dash.txt',
		help='file with dash examples'
	)
	return parser.parse_args()


def init_logger():
	file_name = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	log_directory = "log/"
	if not os.path.exists(log_directory):
		os.mkdir(log_directory)
	log_path = log_directory +  file_name + ".log"
	logging.basicConfig(filename=log_path, level=logging.INFO, format='\n%(asctime)s\n%(message)s')


def main():
	init_logger()
	args = get_args()
	dash_chars = get_dash(args.dash_file)
	extract_dialog(
        src_directory=args.src_directory,
        dst_directory=args.dst_directory,
        dash_chars=dash_chars
    )


if __name__ == "__main__":
	main()
