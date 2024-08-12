import serial
import serial.tools.list_ports
from PIL import Image

class EZSign:
	NEXT = 0xfe
	PREV = 0xff
	SOD = b'\xbb'  # start of data
	EOD = b'\x7e'  # end of data
	SEND = b'\x00'
	RECV = b'\x01'
	WIDTH = 400
	HEIGHT = 300
	COLOR_THRESHOLD = 20

	def __init__(self, serial_port) -> None:
		self.__serial = serial_port

	def __del__(self):
		pass

	def __checksum(self, data :bytes):
		length = len(data)
		sum = 0
		for i in range(length):
			sum = sum + data[i]
		sum = 0xff &  sum
		return sum

	def __mkcommand(self, data :bytes):
		sum = self.__checksum(self.SEND + data)
		b = self.SOD + self.SEND + data + bytes([sum]) + self.EOD
		return b

	def __recvdata(self, payload_bytes):
		packet_bytes = payload_bytes + 4
		rdata = self.__serial.read(packet_bytes)
		sum = self.__checksum(rdata[1:packet_bytes-2])
		if bytes([rdata[0]]) == self.SOD and \
			bytes([rdata[1]]) == self.RECV and \
			rdata[packet_bytes -2] == sum and \
			bytes([rdata[packet_bytes -1]]) == self.EOD :
			# print("recvdata OK")
			return rdata[2:packet_bytes - 2]
		else:
			data_size = 0
			print("recvdata err")
			print(rdata)
			return None

	def poweroff(self):
		command = self.__mkcommand(b'\x07x\01x\00')
		self.__serial.write(command)
		rdata =  self.__recvdata(3) #070101
		if rdata != None:
			return True
		else:
			return False
	def showpage(self, page_number):
		command = self.__mkcommand(b'\x00' + b'\x01' + bytes([page_number]))
		self.__serial.write(command)
		rdata =  self.__recvdata(3) # same as command bytes
		print("Wait about 30 seconds for the screen to refresh.")
		if rdata != None:
			return True
		else:
			return False
	def readimage(self, page_number, filename = None):
		image_size = (self.WIDTH, self.HEIGHT)
		img = Image.new("RGB", image_size)
		count_max = int(self.WIDTH * self.HEIGHT / (8 * 16)) + 1
		progress = 0
		prev_progress = 0
		for c in range(2):
			x = 0
			y = 0
			for i in range(count_max): # 938
				command0504 = self.__mkcommand(b'\x05' + b'\x04' + bytes([page_number]) + bytes([c]) + i.to_bytes(2, 'big'))
				self.__serial.write(command0504)
				rdata = self.__recvdata(4+16)
				progress = int((i + c * count_max) * 100 / (2 * count_max))
				if progress > prev_progress :
					print(str(progress) + "/100 %" )
					prev_progress = progress
				if rdata != None:
					for j in range(16):
						if y >= self.HEIGHT:
							break
						for k in range(8):
							if rdata[j+4] & (0x80 >> k):
								if c == 1:
									img.putpixel((x, y), (255, 0, 0))
								else :
									img.putpixel((x, y), (255, 255, 255))
							else:
								if c == 1 :
									pass
								else :
									img.putpixel((x, y), (0, 0, 0))
							x = x + 1
							if x >= self.WIDTH:
								x = 0
								y = y + 1
				else:
					return False
		if filename == None:
			img.show()
		else:
			img.save(filename)
		print("100/100 %")
		return True
		
	def writeimage(self, page_number, filename):
		img_orig = Image.open(filename)
		width, height = img_orig.size
		if width != self.WIDTH or height != self.HEIGHT :
			img_orig = img_orig.resize((self.WIDTH, self.HEIGHT))
		img = img_orig.convert('RGB')
		command0101 = self.__mkcommand(b'\x01' + b'\x01' + bytes([page_number]))
		self.__serial.write(command0101)
		rdata = self.__recvdata(3)  # 0101fe
		if rdata == None:
			return False
		# print("0101command resp" + str(rdata))
		b = 0x00
		ba = bytearray(16)
		count_max = self.WIDTH * self.HEIGHT
		progress = 0
		prev_progress = 0
		for c in range(2): # 0 black 1 red
			i = 0
			count = 0
			baindex = 0
			command0302 = self.__mkcommand(b'\x03' + b'\x02'  + bytes([page_number]) + bytes([c]))
			self.__serial.write(command0302)
			rdata = self.__recvdata(3)  # 030101
			if rdata == None:
				return False
			#print("0302command resp" + str(rdata))
			for y in range(self.HEIGHT):
				for x in range(self.WIDTH):
					doton = False
					pixel = img.getpixel((x, y))
					if c == 1:
						#if pixel[0] == 255 and pixel[1] == 0 and pixel[2] == 0 :
						if pixel[0] > (255 - self.COLOR_THRESHOLD) and pixel[1] < self.COLOR_THRESHOLD and pixel[2] < self.COLOR_THRESHOLD :
							doton = True # red
					else :
						#if pixel[0] == 255 and pixel[1] == 255 and pixel[2] == 255 :
						if pixel[0] > (255 - self.COLOR_THRESHOLD) and pixel[1] > (255 - self.COLOR_THRESHOLD) and pixel[2]> (255 - self.COLOR_THRESHOLD) :
							doton = True # white
					b = b << 1
					if doton :
						b = b | 0x01
					count = count + 1
					if count % 8 == 0 : # 1 byte 
						b = b & 0xff
						ba[baindex] = b
						baindex = baindex + 1
						b = 0x00
					if (count % (8 * 16) == 0) or ( count >= (self.WIDTH * self.HEIGHT)): # 16 bytes or last pixel
						# 0412 0000-03a9 16bytes pixeldata
						command0412 = self.__mkcommand(b'\x04' + b'\x12' + i.to_bytes(2, 'big') + ba)
						self.__serial.write(command0412)
						progress = int(count * 100 / count_max)
						if progress > prev_progress :
							print(str(progress) + "/100 %" )
							prev_progress = progress
							# print(str(count) + " " + str(page_number) + " " + str(c) + " " + hex(i) + ":" + str(command0412))
						rdata = self.__recvdata(3)  #  040101
						if rdata == None:
							return False
						ba.__init__(len(ba)) # zero clear
						baindex = 0
						i = i + 1
		command0001 = self.__mkcommand(b'\x00' + b'\x01' + bytes([page_number]))
		self.__serial.write(command0001)
		rdata = self.__recvdata(3)  # 0001page_number
		# print("0001command resp" + str(rdata))
		if rdata == None:
			return False
		print("100/100 %")
		print("Wait about 30 seconds for the screen to refresh.")
		return True

####

if __name__ == '__main__':
	import traceback
	import signal
	def sigint_handler(signum, frame):
		raise KeyboardInterrupt
	signal.signal(signal.SIGINT, sigint_handler)
	import argparse 
	parser = argparse.ArgumentParser(description='EZSign epaper display reader/writer', usage='serialport [-s pagenumber] [-r pagenumber filename] [-w pagenumber filename]')
	parser.add_argument('serialport', help='e.g. COM0 /dev/ttyACM0 /dev/tty.usbserial-Disabled')
	parser.add_argument('-s', '--showpage', metavar='pagenumber', help='1-5 or N or P ')
	parser.add_argument('-r', '--readimage', nargs=2, metavar=('pagenumber', 'filename'), help='arguments are pagenumber(1-5) and filename to save.')
	parser.add_argument('-w', '--writeimage', nargs=2,  metavar=('pagenumber', 'filename'), help=' arguments are pagenumber(1-5) and filename to upload.')
	#parser.add_argument('-0', '--poweroff', action='store_true')
	args = parser.parse_args()

	try:
		Serial_Port=serial.Serial(port=args.serialport, baudrate=38400, parity= 'N')

		ezsign = EZSign(Serial_Port)
		if args.showpage :
			if args.showpage[0] == 'P' :
				print("Show previous page.")
				ezsign.showpage(EZSign.PREV)
			elif args.showpage[0] == 'N' :
				print("Show next page.")
				ezsign.showpage(EZSign.NEXT)
			else:
				pagenum = int(args.showpage[0])
				if pagenum > 0 and pagenum < 6:
					print("Show pagenumber " + str(pagenum))
					ezsign.showpage(pagenum)
				else:
					raise ValueError("Specify pagenumber 1 to 5 or N(ext) or P(revious).")
		if args.readimage :
			pagenum = int(args.readimage[0])
			if pagenum > 0 and pagenum < 6:
				print("Read image data from pagenumber " + str(pagenum) + "and save into " + args.readimage[1])
				ezsign.readimage(pagenum, args.readimage[1])
			else:
				raise("Specify pagenumber 1 to 5.")
		if args.writeimage :
			pagenum = int(args.writeimage[0])
			if pagenum > 0 and pagenum < 6:
				print("Write imagefile " + args.writeimage[1] + " to pagenumber " + str(pagenum))
				ezsign.writeimage(pagenum, args.writeimage[1])
			else:
				raise("Specify pagenumber 1 to 5.")
		#if args.poweroff :
		#	print("Power off")
		#	ezsign.poweroff()
	except ValueError as e:
		print(e)
	except:
		traceback.print_exc()
	finally:
		Serial_Port.close()
		exit()

