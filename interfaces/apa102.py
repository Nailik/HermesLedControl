# -*- coding: utf-8 -*-
import importlib

try:
	from gpiozero import LED
except:
	try:
		import mraa
	except:
		pass


from libraries.apa102   import APA102       as AAPA102
from models.Interface 	import Interface

class APA102(Interface):

	def __init__(self, numLed, global_brightness=AAPA102.MAX_BRIGHTNESS, order='rgb', bus=0, device=1, max_speed_hz=8000000, endFrame=255, hardware=None):
		super(APA102, self).__init__(numLed)
		self._leds  = AAPA102(numLed, global_brightness=global_brightness, order=order, bus=bus, device=device, max_speed_hz=max_speed_hz, endFrame=endFrame)

		try:
			self._power = LED(5)
		except:
			try:
				self._power = mraa.Gpio(5)
				self._power.dir(mraa.DIR_OUT)
			except Exception as e:
				self._logger.info('Device not using gpiozero or mraa, ignore power: {}'.format(e))

		self._hardware = hardware
		self._doa = None
		self._src = None
		if hardware and hardware['doa']:
			self._logger.info('Hardware is DOA capable')
			from libraries.seeedstudios.channel_picker import ChannelPicker
			from libraries.seeedstudios.source import Source

			lib = importlib.import_module('libraries.seeedstudios.' + hardware['doa'])
			klass = getattr(lib, 'DOA')

			self._src = Source(rate=hardware['rate'], channels=hardware['channels'])
			ch0 = ChannelPicker(channels=self._src.channels, pick=0)

			self._doa = klass(rate=hardware['rate'])
			self._src.link(ch0)
			self._src.link(self._doa)


	def setPixel(self, ledNum, red, green, blue, brightness):
		self._leds.set_pixel(ledNum, red, green, blue, brightness)


	def setPixelRgb(self, ledNum, color, brightness):
		self._leds.set_pixel_rgb(ledNum, color, brightness)


	def clearStrip(self):
		self._leds.clear_strip()


	def onStart(self):
		super().onStart()
		if self._doa:
			self._logger.info('Starting DOA')
			self._src.recursive_start()


	def onStop(self):
		super(APA102, self).onStop()
		self.clearStrip()
		self._leds.cleanup()
		if self._src:
			self._src.recursive_stop()


	def doa(self):
		if self._doa:
			try:
				return self._doa.get_direction()
			except:
				pass

		return 0