from io import BytesIO
from PIL import Image, ImageDraw
import cognitive_face as CF
import argparse


def handleArgs():
	parser = argparse.ArgumentParser(description='Generate face group')
	parser.add_argument('-g', '--group', help='generate group', default=',')
	args = vars(parser.parse_args())
        return args


KEY = '271462f910094fa780016700488a0b62' 
CF.Key.set(KEY)

BASE_URL = 'https://westcentralus.api.cognitive.microsoft.com/face/v1.0'  
CF.BaseUrl.set(BASE_URL)


if __name__ == '__main__':

    args = handleArgs()

    if args['group'] == ',':
        print("argument error!!")
    else:   
        if args['group']:
            PERSON_GROUP_ID = args['group']
            

        response = CF.person_group.get_status(PERSON_GROUP_ID)
        status = response['status']

        print status


