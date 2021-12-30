#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import sys
import logging
import ccs811LIBRARY

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG,  datefmt='%Y-%m-%d %H:%M:%S')

picdir = os.path.join(os.path.join(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'e-Paper'),'RaspberryPi_JetsonNano'),'python'),'pic')
logging.info("Add pic dir: "+ picdir)

#inintialize mockups on dev env, and real libs on rasp
if os.path.exists('/sys/bus/platform/drivers/gpiomem-bcm2835'):
    logging.info("Start in productive mode...")
    libdir = os.path.join(os.path.join(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'e-Paper'),'RaspberryPi_JetsonNano'),'python'),'lib')
    if os.path.exists(libdir):
        sys.path.append(libdir)
    logging.info("Add lib dir: "+ libdir)

    libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Adafruit_Python_DHT')
    if os.path.exists(libdir):
        sys.path.append(libdir)
    logging.info("Add lib dir: "+ libdir)

    import Adafruit_DHT
    from waveshare_epd import epd4in2
else:
    logging.info("Start in mockup mode...")
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mockups'))
    import Adafruit_DHT_mock
    from waveshare_epd import epd4in2_mock

import time
from PIL import Image, ImageDraw, ImageFont
import subprocess
import traceback
import requests

token = "eyJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAtMjU2In0.VTZdnH0IIZxxIMidsjR74w2NPhTHSu5H-QgxYPYc1o6vMY351re3mnhWjSsSvOOnmyGHH3KjaCifllzVr5Dqf8_Gd-oKD7tPjvNYP7GLGOdlK_Fj633j3yc4j9uM1aWNpQE4VTjCqY-fpPNff7Bk2dc_MI_YUu1ahKkkKOVu91ynSh_nV0Qovss765260lMHjW3R9ic8fGrlp7uHLOj8R2elOS5DrefFoy6OOkT_3gD0voGPl2Z97qqjeZY7KVUz_havJWf84BhfUFd0DjjvBJGel6q60Eja4TnAL-ZCltxb8Ljpwjnrrkv6rMSvtUvsefKAkKAqCSYJV6q3aZVv7RIklmR68Q6VrxKh7e7cTDaEOFubye6-0aD0hxkh4OZHU6_yfaqXDFVBy20DjxiOTqDZnJ5aWRyyGNP-yy7vZYWo9sdJThBVgMjGFgJJQQCJjci0FAO3xd2HCo72nhbsdTLRh05aj1nKLsMPCu7pHd3gUaiIWjXNT1CTkZANe4fCCv2-4yBnk5ock1W65shn0RLWFIiUs7vQVXBIh7k33S3sXc71fmfR11uXkxDbG8nRwsWRfyvLYBjHwlmpV950FjMmlAldIEDZKJjr91N1sctxNLSNVzv1Qezf4Lhh1bBGOoZdz6BfzZ7ePwaRR_AiCZS7wnSj_NvaiznuZbVpkWg.R5xLnvtGSSuoIIie.EFZ0UDR80iXcUdJpbeobxRSv4r7FSUSCdelfHWHDhFZrof5EYSpsr4F3XKKCuIcPZV_irP-R0APIwBUB_f7C--HrYsNFcNarMR2vNncQMitZtpsGYFvsoAXcEX0Ry4V0evfPSLOo9tnkwBG2viC0vRsJ5Pl_qtougBVwXxVcEuIJmqOzNeq4OZhUBLON6Ok6eJxNVOs28FhjK9cr4kPVGDNv-59W9eD7lC6NSuIxPgOIU3xqvn-fDWtoWvNnOQW6gpEKe3ddefd7nsDvcD9Y-GWIKTMv3tH1edF1jYHC6Uy0Uk4zVPfebnqTupA6CamsX5PGSbbHxTEjblNTAs4jL-EZS0MGQPugCzSFjI-nxkh5i-cfslgClQrvVsFJDJxiRPO1-4KAHXZubg4T5V6shtfoPq_zKnQY0WNf-qFAFrkRu5ySh2PO5jI7R3mewYErDQKCczuyxZUEeMB393nxPqK3YDoFUe5y6Hwv2Lah8lGJ3Tqy2VV7PSUaxnEFNDOgJpDjnr2hdSlv3i7YLrP-Ao5E5iANhXjW0PB595C9qnRrpQ-YPN9BwhwK4Pgqf6ScIe-MZz3_EGp1uFYi4FU76vQ5xXWcLqcOUrkpDIrzDxVDTxnCHTlmCz4E7flOtClsUzpsLFurB06c2jWn-y-5mzt5uOKPhp7qDdGKaqBAYJj_-CUJVgPlRyqr5T2D3QaflCk-4Dc4eDL8avsEsSEGlUIdQo5KDPbcfqMCFFFBGU4vybjDNAxy_FsSDT-9hq7ir_QpjbtsW8QkeFCKY68GGXu7xTbONcdmn4h9XBmtLrb4fi57fAzXu4GAimcnvyMxOYibTv8Fqa3G44Or9J0ZJO9N9vYRLZ8lNNrl_Eam8BuVVZVxKvvJlhCGFLnrqm2yJaMfMWV-2xbd2d7bYdypYN721fqJFJE2C0NXhkNZAsYbC-VIh-ov0ud-e_my09KY5XjNEYq3o14xhaouSP2mXpnZn7XvZslxVH8AJU-ADrtf0YJEMQAJvN9M3wlBXamWTO1vDJHKGYRjdcX3xZPPGI_xm7eYC6zH4oJtXqiH6x1uwah-668EVOWf1zzOsGFMQ9r9tODA5EUszsov2OwA7r83lHYghmUjnCmeh2fIpkzc10dmjpUydV8ZKiG6XvrcEyjFbcIIKbav3gKIEPqruvheShflRaMZtjTT5_fxlz_4KJo1kru_pjLApMKbfeTHa4-bH3nN89eZpOrLxrbDb5l9FtyxDZLv6UVXJ0ATDji8u2DtafHFvjoaqbCMXCokMDJfYlIHy7OWCg1OtWReuk-aKpBxQ24Re5fPsnhRxXtEGRwJAq1aWJnH3KHmhYaolS7d1ELmKX6y-oiG-gof1OY.PvD0sJEh53fz91AB_EAVlA"
header = {"Authorization": "Bearer " + token}

font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)


sensor = ccs811LIBRARY.CCS811()
def setup(mode=1):
    print('Starting CCS811 Read')
    sensor.configure_ccs811()
    sensor.set_drive_mode(mode)

    if sensor.check_for_error():
        sensor.print_error()
        raise ValueError('Error at setDriveMode.')

    result = sensor.get_base_line()
    sys.stdout.write("baseline for this sensor: 0x")
    if result < 0x100:
        sys.stdout.write('0')
    if result < 0x10:
        sys.stdout.write('0')
    sys.stdout.write(str(result) + "\n")


try:
    setup(1)
except IOError as e:
    logging.info(e)

try:
    epd = epd4in2.EPD()
    logging.info("Init and Clear display")
    epd.init()
    epd.Clear()
    loop = True
    cnt = 1
    while loop:
        image = Image.new('1', (epd.width, epd.height), 255)
        draw = ImageDraw.Draw(image)
        logging.info("Updating for Iteration " + str(cnt))
        cnt = cnt + 1
        logging.info("Read outside temp...")
        # req1 = "https://api.viessmann.com/iot/v1/equipment/installations/952499/gateways/7637415022052208/devices/0/features/heating.sensors.temperature.outside"
        # logging.info("reading temperature.outside")
        # response = requests.get(url=req1, headers=header)
        outsideTemp = 0.0
        # logging.info(response.json())
        # outsideTemp = str(response.json()["data"]["properties"]["value"]["value"])

        logging.info('Outside temp: {:.1f}°'.format(outsideTemp))
        draw.text((10, 0), 'Außen: {:.1f}°'.format(outsideTemp), font=font24, fill=0)

        # read humidity and inside temp
        logging.info("Read inside temperature and humidity...")
        insideHumidity, insideTemp = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, 4)

        if insideHumidity is not None and insideTemp is not None:
            logging.info( 'Inside temp: {:.1f}°'.format(insideTemp))
            logging.info( 'Rel. Humidity: {:.1f}%'.format(insideHumidity))
            draw.text((10, 50), 'Innen: {:.1f}°'.format(insideTemp), font = font24, fill = 0)
            draw.text((10, 100), 'Rel: {:.1f}%'.format(insideHumidity), font = font24, fill = 0)
        else:
            logging.info( "Could not read from Inside temp/Humidity")

        #res = subprocess.run("sudo pigpiod", shell=True, check=True, text=True)
        #logging.info(res.stdout)

        logging.info("Read CO2 and TVOC...")
        if sensor.data_available():
            sensor.read_logorithm_results()
            logging.info( "CO2: {0:.1f} TVOC: {1:.1f}".format(sensor.CO2, sensor.tVOC))
            draw.text((10, 150), "CO2: {0:.1f} TVOC: {1:.1f}".format(sensor.CO2, sensor.tVOC), font = font24, fill = 0)
        elif sensor.check_for_error():
            logging.info( "Could not read from CO2/TVOC Sensor")

        #res = subprocess.run("sudo killall pigpiod", shell=True, check=True, text=True)
        #logging.info(res.stdout)

        epd.display(epd.getbuffer(image))
        time.sleep(30)


except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd.Clear()
    epd.sleep()
    epd4in2.epdconfig.module_exit()
    exit()

'''draw.text((10, 20), '4.2inch e-Paper', font = font24, fill = 0)
	draw.text((150, 0), u'微雪电子', font = font24, fill = 0)    
	draw.line((20, 50, 70, 100), fill = 0)
	draw.line((70, 50, 20, 100), fill = 0)
	draw.rectangle((20, 50, 70, 100), outline = 0)
	draw.line((165, 50, 165, 100), fill = 0)
	draw.line((140, 75, 190, 75), fill = 0)
	draw.arc((140, 50, 190, 100), 0, 360, fill = 0)
	draw.rectangle((80, 50, 130, 100), fill = 0)
	draw.chord((200, 50, 250, 100), 0, 360, fill = 0)
	epd.display(epd.getbuffer(Himage))
	time.sleep(2)

	# Drawing on the Vertical image
	logging.info("2.Drawing on the Vertical image...")
	Limage = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
	draw = ImageDraw.Draw(Limage)
	draw.text((2, 0), 'hello world', font = font18, fill = 0)
	draw.text((2, 20), '4.2inch epd', font = font18, fill = 0)
	draw.text((20, 50), u'微雪电子', font = font18, fill = 0)
	draw.line((10, 90, 60, 140), fill = 0)
	draw.line((60, 90, 10, 140), fill = 0)
	draw.rectangle((10, 90, 60, 140), outline = 0)
	draw.line((95, 90, 95, 140), fill = 0)
	draw.line((70, 115, 120, 115), fill = 0)
	draw.arc((70, 90, 120, 140), 0, 360, fill = 0)
	draw.rectangle((10, 150, 60, 200), fill = 0)
	draw.chord((70, 150, 120, 200), 0, 360, fill = 0)
	epd.display(epd.getbuffer(Limage))
	time.sleep(2)

	logging.info("3.read bmp file")
	Himage = Image.open(os.path.join(picdir, '4in2.bmp'))
	epd.display(epd.getbuffer(Himage))
	time.sleep(2)

	logging.info("4.read bmp file on window")
	Himage2 = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
	bmp = Image.open(os.path.join(picdir, '100x100.bmp'))
	Himage2.paste(bmp, (50,10))
	epd.display(epd.getbuffer(Himage2))
	time.sleep(2)

	logging.info("Clear...")
	epd.Clear()

	Himage3 = Image.new('1', (epd.width, epd.height), 0)  # 255: clear the frame
	draw = ImageDraw.Draw(Himage3)
	print("Support for partial refresh, but the refresh effect is not good, but it is not recommended")
	print("Local refresh is off by default and is not recommended.")
	if(0):
		for j in range(0, int(20)):
			draw.rectangle((8, 80, 44, 155), fill = 0)
			draw.text((8, 80), str(j) , font = font35, fill = 1)
			draw.text((8, 120), str(20-j) , font = font35, fill = 1)
			epd.EPD_4IN2_PartialDisplay(8, 80, 42, 155, epd.getbuffer(Himage3))
			time.sleep(2);

	logging.info("5.4Gray display--------------------------------")
	epd.Init_4Gray()

	Limage = Image.new('L', (epd.width, epd.height), 0)  # 255: clear the frame
	draw = ImageDraw.Draw(Limage)
	draw.text((20, 0), u'微雪电子', font = font35, fill = epd.GRAY1)
	draw.text((20, 35), u'微雪电子', font = font35, fill = epd.GRAY2)
	draw.text((20, 70), u'微雪电子', font = font35, fill = epd.GRAY3)
	draw.text((40, 110), 'hello world', font = font18, fill = epd.GRAY1)
	draw.line((10, 140, 60, 190), fill = epd.GRAY1)
	draw.line((60, 140, 10, 190), fill = epd.GRAY1)
	draw.rectangle((10, 140, 60, 190), outline = epd.GRAY1)
	draw.line((95, 140, 95, 190), fill = epd.GRAY1)
	draw.line((70, 165, 120, 165), fill = epd.GRAY1)
	draw.arc((70, 140, 120, 190), 0, 360, fill = epd.GRAY1)
	draw.rectangle((10, 200, 60, 250), fill = epd.GRAY1)
	draw.chord((70, 200, 120, 250), 0, 360, fill = epd.GRAY1)
	epd.display_4Gray(epd.getbuffer_4Gray(Limage))
	time.sleep(3)

	#display 4Gra bmp
	Himage = Image.open(os.path.join(picdir, '4in2_Scale_1.bmp'))
	epd.display_4Gray(epd.getbuffer_4Gray(Himage))
	time.sleep(4)

	epd.Clear()
	logging.info("Goto Sleep...")'''
