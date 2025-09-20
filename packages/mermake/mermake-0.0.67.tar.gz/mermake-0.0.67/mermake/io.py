import os
import re
import gc
import glob
from pathlib import Path
from fnmatch import fnmatch
from types import SimpleNamespace
from typing import List, Tuple, Optional
import json
import argparse
from argparse import Namespace
import functools
import concurrent.futures
import queue
import threading
from itertools import chain

import xml.etree.ElementTree as ET
import dask.array as da
import cupy as cp
import numpy as np

from . import blur
from . import __version__

def center_crop(A, shape):
	"""Crop numpy array to (h, w) from center."""
	h, w = shape[-2:]
	H, W = A.shape
	top = (H - h) // 2
	left = (W - w) // 2
	return A[top:top+h, left:left+w]

def load_flats(flat_field_tag, shape=None, **kwargs):
	stack = list()
	files = sorted(glob.glob(flat_field_tag + '*'))
	for file in files:
		im = np.load(file)['im']
		if shape is not None:
			im = center_crop(im, shape)
		cim = cp.array(im,dtype=cp.float32)
		blurred = blur.box(cim, (20,20))
		blurred = blurred / cp.median(blurred)
		stack.append(blurred)
	return cp.stack(stack)

def path_parts(path):
	path_obj = Path(path)
	fov = path_obj.stem  # The filename without extension
	tag = path_obj.parent.name  # The parent directory name (which you seem to want)
	return fov, tag


class Container:
	def __init__(self, path_or_array):
		if isinstance(path_or_array, str):
			# Load from file
			im = read_im(path_or_array)
			# Always split first axis into channels
			self.data = [Container(im[i]) for i in range(im.shape[0])]
			self.path = path_or_array
		else:
			# Already an array, just store it
			self.data = path_or_array
			self.path = None

	def __getitem__(self, idx):
		return self.data[idx]

	def __repr__(self):
		if isinstance(self.data, list):
			shapes = [getattr(ch.data, "shape", None) if isinstance(ch, Container) else getattr(ch, "shape", None)
					  for ch in self.data]
			return f"Container(path={self.path}, shapes={shapes})"
		else:
			return f"Container(shape={getattr(self.data, 'shape', None)})"

	def __array__(self, dtype=None):
		"""
		Return the underlying array for NumPy/CuPy interop.
		Called automatically when passed to np.array() or cupy.set().
		"""
		if isinstance(self.data, list):
			raise ValueError("Cannot convert a multi-channel Container to a single array")
		arr = self.data
		if dtype is not None:
			arr = arr.astype(dtype)
		return arr

	def compute(self):
		"""Compute only the current container (recursively if channels)."""
		if isinstance(self.data, list):
			for i, ch in enumerate(self.data):
				self.data[i] = ch.compute()  # recurse into sub-containers
			return self
		elif isinstance(self.data, da.Array):
			self.data = self.data.compute()
			return self
		else:
			return self


def read_im(path, return_pos=False):
	dirname = os.path.dirname(path)
	fov = os.path.basename(path).split('_')[-1].split('.')[0]
	file_ = os.path.join(dirname, fov, 'data')

	#z = zarr.open(file_, mode='r')
	#image = np.array(z[1:])
	from dask import array as da
	image = da.from_zarr(file_)[1:]

	shape = image.shape
	xml_file = os.path.splitext(path)[0] + '.xml'
	if os.path.exists(xml_file):
		txt = open(xml_file, 'r').read()
		tag = '<z_offsets type="string">'
		zstack = txt.split(tag)[-1].split('</')[0]

		tag = '<stage_position type="custom">'
		x, y = eval(txt.split(tag)[-1].split('</')[0])

		nchannels = int(zstack.split(':')[-1])
		nzs = (shape[0] // nchannels) * nchannels
		image = image[:nzs].reshape([shape[0] // nchannels, nchannels, shape[-2], shape[-1]])
		image = image.swapaxes(0, 1)

	if image.dtype == np.uint8:
		image = image.astype(np.uint16) ** 2

	if return_pos:
		return image, x, y
	return image

def get_ih(file_path):
	basename = os.path.basename(file_path)
	m = re.search(r'\d+', basename)  # first contiguous digits
	if m:
		return int(m.group())
	return 10**100
	#raise ValueError(f"No number found in {basename}")

def get_ifov(file_path):
	"""Extract ifov from filename - finds last digits before .zarr"""
	filename = Path(file_path).name  # Keep full filename with extension
	match = re.search(r'([0-9]+)[^0-9]*\.zarr', filename)
	if match:
		return int(match.group(1))
	raise ValueError(f"No digits found before .zarr in filename: {filename}")

def get_iset(file_path):
	"""
	Recursively extract 'iset' from filename or parent directories.
	Finds last digits after the word '_set'.
	"""
	path = Path(file_path)  # ensure Path object
	filename = path.name
	match = re.search(r'_set([0-9]+)', filename)
	if match:
		return int(match.group(1))

	# Base case: reached root
	if path.parent == path:
		raise ValueError(f"No digits found after the word _set in {file_path}")

	# Recurse up
	return get_iset(path.parent)

class FolderFilter:
	def __init__(self, hyb_range: str, regex_pattern: str, fov_min: float, fov_max: float):
		self.hyb_range = hyb_range
		self.regex = re.compile(regex_pattern)
		self.start_pattern, self.end_pattern = self.hyb_range.split(':')	
		self.fov_min = fov_min
		self.fov_max = fov_max
		
		# Parse start and end patterns
		self.start_parts = self._parse_pattern(self.start_pattern)
		self.end_parts = self._parse_pattern(self.end_pattern)
		
	def _parse_pattern(self, pattern: str) -> Optional[Tuple]:
		"""Parse a pattern using the regex to extract components"""
		match = self.regex.match(pattern)
		if match:
			return match.groups()
		return None
	
	def _extract_numeric_part(self, text: str) -> int:
		"""Extract numeric part from text like 'H1' -> 1"""
		match = re.search(r'\d+', text)
		return int(match.group()) if match else 0
	
	def _compare_patterns(self, file_parts: Tuple, start_parts: Tuple, end_parts: Tuple) -> bool:
		"""
		Compare if file_parts falls within the range defined by start_parts and end_parts
		Groups: (prefix, number, middle, set_number, suffix)
		"""
		if not all([file_parts, start_parts, end_parts]):
			return False
			
		# Extract components
		file_prefix, file_num, file_middle, file_set, file_suffix = file_parts
		start_prefix, start_num, start_middle, start_set, start_suffix = start_parts
		end_prefix, end_num, end_middle, end_set, end_suffix = end_parts
		
		# Convert to integers for comparison
		file_num = int(file_num)
		file_set = int(file_set)
		start_num = int(start_num)
		start_set = int(start_set)
		end_num = int(end_num)
		end_set = int(end_set)
	
		# Check if middle part matches (e.g., 'MER')
		if start_middle == '*':
			pass
		elif file_middle != start_middle or file_middle != end_middle:
			return False
			
		# Check if prefix matches
		if file_prefix != start_prefix or file_prefix != end_prefix:
			return False
			
		num_in_range = start_num <= file_num <= end_num
		set_in_range = start_set <= file_set <= end_set
		
		return num_in_range and set_in_range
	
	def isin(self, text: str) -> bool:
		"""Check if a single text/filename falls within the specified range"""
		file_parts = self._parse_pattern(text)
		if not file_parts:
			return False
		return self._compare_patterns(file_parts, self.start_parts, self.end_parts)
	
	def filter_files(self, filenames: List[str]) -> List[str]:
		"""Filter filenames that fall within the specified range"""
		matching_files = []
		
		for filename in filenames:
			if self.isin(filename):
				matching_files.append(filename)
				
		return matching_files

	def get_matches(self, folders):
		matches = dict()
		for root in folders:
			if not os.path.exists(root):
				continue
			try:
				with os.scandir(root) as entries:
					for sub in entries:
						if sub.is_dir(follow_symlinks=False) and self.isin(sub.name):
							try:
								with os.scandir(sub.path) as items:
									# we might need other ways to determine set
									iset = get_iset(str(sub.name))
									for item in items:
										if item.is_dir(follow_symlinks=False) and '.zarr' in item.name:
											ifov = get_ifov(str(item.name))
											if self.fov_min <= ifov <= self.fov_max:
												matches.setdefault((iset,ifov), []).append(item.path)

							except PermissionError:
								continue
			except PermissionError:
				continue
		return matches

class Block(list):
	def __init__(self, items=None):
		self.background = None
		if isinstance(items, (list, tuple)):
			for item in items:
				self.append(item)
		elif items:
			self.append(items)
	def parts(self):
		path = self[0].path
		fov, tag = path_parts(path)
		return fov, tag
	def fov(self):
		fov,_ = self.parts()
		return fov
	def tag(self):
		_,tag = self.parts()
		return tag
	def iset(self):
		return get_iset(self[0].path)
	
class ImageQueue:
	__version__ = __version__
	def __init__(self, args, prefetch_count=6):
		self.args = args
		self.args_array = namespace_to_array(self.args.settings)
		self.__dict__.update(vars(args.paths))

		os.makedirs(self.output_folder, exist_ok = True)
		
		fov_min, fov_max = (-float('inf'), float('inf'))
		if hasattr(self, "fov_range"):
			fov_min, fov_max = map(float, self.fov_range.split(':'))
		matches = FolderFilter(self.hyb_range, self.regex, fov_min, fov_max).get_matches(self.hyb_folders)
		background = None
		if hasattr(self, "background_range"):
			background = FolderFilter(self.background_range, self.regex, fov_min, fov_max).get_matches(self.hyb_folders)
			self.background = True

		# Peek at first image to set shape/dtype
		first_image = None
		for path in chain.from_iterable(matches.values()):
			try:
				first_image = read_im(path)
				break
			except:
				continue
		if first_image is None:
			raise RuntimeError("No valid images found.")
		self.shape = first_image.shape
		self.dtype = first_image.dtype
	
		# interlace the background with the regular images
		shared = set(matches.keys()).intersection(background.keys()) if background else matches.keys()
		#matches = [item for key in shared for item in matches[key]]
		#background = [item for key in shared for item in background[key]] if background else None
		interlaced = []
		for key in shared:
			if background and key in background:
				interlaced.extend(background[key])  # put background first
			hsorted = self.hsorted(matches[key])
			interlaced.extend(hsorted)			    # then all matches for that iset,ifov

		self.files = iter(interlaced)

		self.block = Block()
		# Start worker thread(s)
		self.queue = queue.Queue(maxsize=prefetch_count)
		self.stop_event = threading.Event()
		self.thread = threading.Thread(target=self._worker, daemon=True)
		self.thread.start()

	def hsorted(self, files):
		return sorted(files, key=lambda f: get_ih(os.path.dirname(f)))

	def containerize(self, path):
		# everythign in this method is done async and prefetched

		container = Container(path)

		fit_files = list()
		# check if the fov has been fitted
		fov, tag = path_parts(path)
		for icol in range(self.shape[0] - 1):
			filename = self.hyb_save.format(fov=fov, tag=tag, icol=icol)
			filepath = os.path.join(self.output_folder, filename)
			if not os.path.exists(filepath):
				container[icol].compute()
			else:
				container[icol].fits = cp.load(filepath)
		icol += 1
		filename = self.dapi_save.format(fov=fov, tag=tag, icol=icol)
		filepath = os.path.join(self.output_folder, filename)
		if not os.path.exists(filepath):
			container[icol].compute()
		else:
			container.Xh_plus = cp.load(filepath)['Xh_plus']
			container.Xh_minus = cp.load(filepath)['Xh_minus']
		return container

	def _worker(self):
		"""Continuously read images and put them in the queue."""
		for path in self.files:
			if self.stop_event.is_set():
				break
			try:
				container = self.containerize(path)
				self.queue.put(container)
			except Exception as e:
				print(f"Warning: failed to read {path}: {e}")
				#dummy = lambda : None
				#dummy.path = path
				#self.queue.put(dummy)
				self.queue.put(False)
				continue
		# Signal no more images
		self.queue.put(None)

	def __iter__(self):
		return self

	'''
	def __next__(self):
		img = self.queue.get()
		if img is None:
			raise StopIteration
		return img
	'''
	
	def __next__(self):
		"""Return the next block of images (same FOV)."""
		block = self.block
		first_item = self.queue.get()

		if first_item is None:
			if block:
				self.block = Block()
				self.queue.put(None)
				return block
			else:
				raise StopIteration
		
		if hasattr(self, "background_range"):
			self.block.background = first_item
		else:
			block.append(first_item)

		#ifov = None if first_item == False else get_ifov(first_item.path)
		#iset = None if first_item == False else get_iset(first_item.path)
		ifov = get_ifov(first_item.path) if first_item else first_item
		iset = get_iset(first_item.path) if first_item else first_item
		
		# Keep consuming queue until FOV changes or None
		while True:
			item = self.queue.get()
			if item == False:
				break
			if item is None:
				self.queue.put(None)
				self.block = Block()
				break
			if (get_ifov(item.path) != ifov) or (get_iset(item.path) != iset):
				if hasattr(self, "background_range"):
					self.block.background = item
				else:
					self.block = Block(item)
				break
			block.append(item)
		if hasattr(self, "background_range") and first_item == False:
			block.clear()
		block.ifov = ifov
		return block

	'''
	def __next__(self):
		"""Return the next block of images (same FOV)."""
		logger.debug(f"__next__ called, queue size: {getattr(self.queue, 'qsize', lambda: 'unknown')()}")
		
		block = Block()  # Fresh block each time
		
		# Get first item with debugging
		logger.debug("Getting first item from queue...")
		start_time = time.time()
		first_item = self.queue.get()
		get_time = time.time() - start_time
		logger.debug(f"Got first item in {get_time:.3f}s: {type(first_item).__name__}")
		
		if first_item is None:
			logger.debug("First item is None, raising StopIteration")
			raise StopIteration
		
		block.append(first_item)
		
		# Handle FOV logic with debugging
		if first_item == False:
			ifov = None
			logger.debug("First item is False, ifov = None")
		else:
			logger.debug(f"Getting ifov for: {getattr(first_item, 'path', 'NO_PATH_ATTR')}")
			ifov = get_ifov(first_item.path)
			logger.debug(f"ifov = {ifov}")
		
		# Keep consuming queue until FOV changes or None
		item_count = 1
		while True:
			logger.debug(f"Loop iteration {item_count}, getting next item...")
			start_time = time.time()
			item = self.queue.get()
			get_time = time.time() - start_time
			logger.debug(f"Got item {item_count} in {get_time:.3f}s: {type(item).__name__}")
			
			if item == False:
				logger.debug("Got False, breaking")
				break
			if item is None:
				logger.debug("Got None, putting back and breaking")
				self.queue.put(None)
				break
			
			logger.debug(f"Getting ifov for item {item_count}: {getattr(item, 'path', 'NO_PATH_ATTR')}")
			item_ifov = get_ifov(item.path)
			logger.debug(f"Item ifov: {item_ifov}, current ifov: {ifov}")
			
			if item_ifov != ifov:
				logger.debug("FOV changed, putting item back and breaking")
				self.queue.put(item)  # Put back the item with different FOV
				break
			
			block.append(item)
			item_count += 1
			logger.debug(f"Added item to block, block size now: {len(block)}")
		
		logger.debug(f"Returning block with {len(block)} items")
		return block
	'''

	'''
		# If we reach here, there are no more images in the current batch
		if False:
			# In watch mode, look for new files
			import time
			time.sleep(60)
			
			# Find any new files
			new_matches = self._find_matching_files()
			# Filter to only files we haven't processed yet
			new_matches = [f for f in new_matches if f not in self.processed_files]
			
			if new_matches:
				# New files found!
				new_matches.sort()
				self.matches = new_matches
				self.files = iter(self.matches)
				self.processed_files.update(new_matches)  # Mark as seen
				
				# Prefetch the first new image
				self._prefetch_next_image()
				
				# Try again to get the next image
				return self.__next__()
			else:
				# No new files yet, but we'll keep watching
				return self.__next__()

		self.close()
		raise StopIteration
	'''

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.close()

	def close(self):
		self.stop_event.set()
		self.thread.join()

	def _is_fitted(self, path):
		fov, tag = path_parts(path)
		for icol in range(self.shape[0] - 1):
			filename = self.hyb_save.format(fov=fov, tag=tag, icol=icol)
			filepath = os.path.join(self.output_folder, filename)
			if not os.path.exists(filepath):
				return False
		filename = self.dapi_save.format(fov=fov, tag=tag, icol=icol)
		filepath = os.path.join(self.output_folder, filename)
		if not os.path.exists(filepath):
			return False
		return True

	def save_hyb(self, path, icol, Xhf, attempt=1, max_attempts=3):
		fov,tag = path_parts(path)
		filename = self.hyb_save.format(fov=fov, tag=tag, icol=icol)
		filepath = os.path.join(self.output_folder, filename)
	
		Xhf = [x for x in Xhf if x.shape[0] > 0]
		if Xhf:
			xp = cp.get_array_module(Xhf[0])
			Xhf = xp.vstack(Xhf)
		else:
			xp = np
			Xhf = np.array([])
		if not os.path.exists(filepath) or (hasattr(self, "redo") and self.redo):
			xp.savez_compressed(filepath, Xh=Xhf, version=__version__, args=self.args_array)
			#  Optional integrity check after saving
			# this seems to greatly slow everything down
			#try:
			#	with np.load(filepath) as dat:
			#		_ = dat["Xh"].shape  # Try accessing a key
			#except Exception as e:
			#	os.remove(filepath)
			#	if attempt < max_attempts:
			#		return self.save_hyb(path, icol, Xhf, attempt=attempt+1, max_attempts=max_attempts)
			#	else:
			#		raise RuntimeError(f"Failed saving xfit file after {max_attempts} attempts: {filepath}")
		del Xhf
		if xp == cp:
			xp._default_memory_pool.free_all_blocks()  # Free standard GPU memory pool

	def save_dapi(self, path, icol, Xh_plus, Xh_minus, attempt=1, max_attempts=3):
		fov, tag = path_parts(path)
		filename = self.dapi_save.format(fov=fov, tag=tag, icol=icol)
		filepath = os.path.join(self.output_folder, filename)
	
		xp = cp.get_array_module(Xh_plus)
		if not os.path.exists(filepath) or (hasattr(self, "redo") and self.redo):
			xp.savez_compressed(filepath, Xh_plus=Xh_plus, Xh_minus=Xh_minus, version=__version__, args=self.args_array)
			#  Optional integrity check after saving
			# this seems to greatly slow everything down
			#try:
			#	with np.load(filepath) as dat:
			#		_ = dat["Xh_minus"].shape  # Try accessing a key
			#except Exception as e:
			#	os.remove(filepath)
			#	if attempt < max_attempts:
			#		return self.save_dapi(path, icol, Xh_plus, Xh_minus, attempt=attempt+1, max_attempts=max_attempts)
			#	else:
			#		raise RuntimeError(f"Failed saving xfit file after {max_attempts} attempts: {filepath}")
		del Xh_plus, Xh_minus
		if xp == cp:
			xp._default_memory_pool.free_all_blocks()

def read_xml(path):
	# Open and parse the XML file
	tree = None
	with open(path, "r", encoding="ISO-8859-1") as f:
		tree = ET.parse(f)
	return tree.getroot()

def get_xml_field(file, field):
	xml = read_xml(file)
	return xml.find(f".//{field}").text

def dict_to_namespace(d):
	"""Recursively convert dictionary into SimpleNamespace."""
	for key, value in d.items():
		if isinstance(value, dict):
			value = dict_to_namespace(value)
		elif isinstance(value, list):
			value = [dict_to_namespace(i) if isinstance(i, dict) else i for i in value]
		d[key] = value
	return SimpleNamespace(**d)
def namespace_to_dict(obj):
	"""Recursively convert namespace objects to dictionaries"""
	if isinstance(obj, argparse.Namespace):
		return {k: namespace_to_dict(v) for k, v in vars(obj).items()}
	elif isinstance(obj, list):
		return [namespace_to_dict(item) for item in obj]
	elif isinstance(obj, dict):
		return {k: namespace_to_dict(v) for k, v in obj.items()}
	else:
		return obj

def namespace_to_array(obj, prefix=''):
	"""
	Recursively convert Namespace or dict to list of (block, key, value) tuples.
	prefix is the accumulated parent keys joined by dots.
	"""
	rows = []
	if isinstance(obj, (Namespace, SimpleNamespace)):
		obj = vars(obj)
	if isinstance(obj, dict):
		for k, v in obj.items():
			full_key = f"{prefix}.{k}" if prefix else k
			if isinstance(v, (Namespace, SimpleNamespace, dict)):
				rows.extend(namespace_to_array(v, prefix=full_key))
			else:
				rows.append((prefix, k, str(v)))
	else:
		# For other types just append
		rows.append((prefix, '', str(obj)))
	return rows
